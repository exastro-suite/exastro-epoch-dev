import urllib.parse
import globals
import requests
import os
from flask import request, redirect, make_response
import urllib
import re
import json

from common_library.common import common
# from common_library.common import multi_lang

# ARGOCDの外部公開のBASE PATH / BASE PATH for external publication of ARGOCD
ARGOCD_EXTERNAL_BASEPATH = '/_/argocd'


def routing(connection_app):
    """controllerのrouting設定 / controller routing settings

    Args:
        connection_app (_type_): _description_
    """
    # オーガナイゼーションを指定したSSO呼び出し / SSO call with organization specified
    connection_app.add_url_rule(f"{ARGOCD_EXTERNAL_BASEPATH}/direct_sso_login", methods=["GET"], view_func=direct_sso_login)
    # ArgoCD settings API
    connection_app.add_url_rule(f"{ARGOCD_EXTERNAL_BASEPATH}/api/v1/settings", methods=["GET"], view_func=argocd_settings)
    # ArgoCD logout
    connection_app.add_url_rule(f"{ARGOCD_EXTERNAL_BASEPATH}/auth/logout", methods=["GET"], view_func=logout)


@common.api_common_decorator
def direct_sso_login():
    """オーガナイゼーションを指定したSSO呼び出し / SSO call with organization specified

    Returns:
        Response: SSO呼出へのredirect response / redirect response to SSO call
    """
    globals.logger.debug('* START: direct_sso_login')

    # オーガナイゼーションID指定パラメータ / Organization ID specification parameter
    organization_id = request.args.get("organization_id")
    if organization_id is None:
        # オーガナイゼーションIDのパラメータが無い場合はエラーとする / If the organization ID parameter is missing, an error will occur.
        # TODO: message id
        raise common.BadRequestException(message_id='000-00000', message='organization_id parameter is required')

    # argocdの表示URLパラメータ(ログイン後に表示するページ) / argocd display URL parameters (page to display after login)
    argocd_url = request.args.get("argocd_url")
    if argocd_url is None:
        # オーガナイゼーションIDのパラメータが無い場合はエラーとする / If the organization ID parameter is missing, an error will occur.
        # TODO: message id
        raise common.BadRequestException(message_id='000-00000', message='argocd_url parameter is required')

    # argocd base URL
    argocd_basepath = f"{os.environ.get('ARGOCD_SERVER_PROTOCOL')}://{os.environ.get('ARGOCD_SERVER_HOST')}:{os.environ.get('ARGOCD_SERVER_PORT')}"

    # ---------------------------------------------------------------------------------------------
    # argocdのSSOログイン開始までの動きを模倣して実行する
    # Execute by imitating the steps up to the start of argocd's SSO login
    # ---------------------------------------------------------------------------------------------
    
    #
    # call /auth/login
    #   ログイン画面のSSOボタンをクリックした際の動作
    #   Behavior when clicking the SSO button on the login screen
    #
    globals.logger.debug("* direct_sso_login - step1")
    resp_login = requests.get(
        argocd_basepath + '/auth/login',
        params={"return_url": argocd_url},
        allow_redirects=False)
    globals.logger.debug(f"{resp_login.status_code=}")
    if not (resp_login.status_code > 300 and resp_login.status_code <= 399):
        # TODO: message_id
        raise common.InternalErrorException(message_id='000-00000', message="call failed : /auth/login")
    globals.logger.debug(f"{resp_login.headers.get('Location')=}")

    #
    # call /api/dex/auth
    #   /auth/loginからのリダイレクト要求をPROXY経由せず直接呼び出す
    #   Directly call redirect request from /auth/login without going through PROXY
    #
    globals.logger.debug("* direct_sso_login - step2")
    auth_urls = urllib.parse.urlparse(resp_login.headers.get('Location'))
    auth_urls = auth_urls._replace(scheme=os.environ.get('ARGOCD_SERVER_PROTOCOL'))
    auth_urls = auth_urls._replace(netloc=f"{os.environ.get('ARGOCD_SERVER_HOST')}:{os.environ.get('ARGOCD_SERVER_PORT')}")
    auth_urls = auth_urls._replace(path=re.sub(rf'^{ARGOCD_EXTERNAL_BASEPATH}', '', auth_urls.path))

    globals.logger.debug(f"** redirect call:{auth_urls.geturl()=}")
    resp_auth = requests.get(auth_urls.geturl(), cookies=resp_login.cookies, allow_redirects=False)
    globals.logger.debug(f"{resp_auth.status_code=}")
    if resp_auth.status_code == 200:
        pass

    elif resp_auth.status_code > 300 and resp_auth.status_code <= 399:
        globals.logger.debug(f"{resp_auth.headers.get('Location')=}")

    else:
        # TODO: message_id
        raise common.InternalErrorException(message_id='000-00000', message="call failed : /api/dex/auth")

    #
    # redirect response
    #   SSO先の一覧からSSO先を選択した時の呼び先にredirectする
    #   Redirect to the call destination when selecting an SSO destination from the list of SSO destinations
    #
    globals.logger.debug("* direct_sso_login - step3")
    redirect_urls = urllib.parse.urlparse(auth_urls.geturl())
    redirect_urls = redirect_urls._replace(path=f'/api/dex/auth/{argocd_sso_id(organization_id)}')

    response = redirect(redirect_urls.geturl())
    # 一連の呼び出しで受け付けたcookieについてもresponseする / Also responds to cookies accepted in a series of calls
    response.set_cookie("argocd.oauthstate", resp_login.cookies.get('argocd.oauthstate'), path=f"{ARGOCD_EXTERNAL_BASEPATH}/auth", httponly=True, secure=True, samesite='Lax')

    return response


def argocd_settings():
    """ArgoCD API(/api/v1/settings) Rewrite

    Returns:
        Response: ArgoCD API(/api/v1/settings) response
    """
    req_urls = urllib.parse.urlparse(request.url)
    req_urls = req_urls._replace(scheme=os.environ.get('ARGOCD_SERVER_PROTOCOL'))
    req_urls = req_urls._replace(netloc=f"{os.environ.get('ARGOCD_SERVER_HOST')}:{os.environ.get('ARGOCD_SERVER_PORT')}")
    req_urls = req_urls._replace(path=re.sub(rf'^{ARGOCD_EXTERNAL_BASEPATH}', '', req_urls.path))

    res_api = requests.get(req_urls.geturl(), cookies=request.cookies)
    if res_api.status_code == 200 and res_api.json is not None:
        res_json = json.loads(res_api.text)
        try:
            # SSOの一覧を消す / Clear SSO list
            res_json["dexConfig"]["connectors"] = []
        except Exception:
            pass
        # deepcode ignore XSS: <please specify a reason of ignoring this>
        return make_response(res_json, 200)
    else:
        # deepcode ignore XSS: <please specify a reason of ignoring this>
        return make_response(res_api.text, res_api.status_code)


@common.api_common_decorator
def logout():
    """ArgoCD logout

    Returns:
        Response: logout redirect
    """
    # argocd base URL
    argocd_basepath = f"{os.environ.get('ARGOCD_SERVER_PROTOCOL')}://{os.environ.get('ARGOCD_SERVER_HOST')}:{os.environ.get('ARGOCD_SERVER_PORT')}"

    # Argocd Logout CALL
    resp_logout = requests.get(argocd_basepath + "/auth/logout", cookies=request.cookies, allow_redirects=False)
    globals.logger.debug(f"{resp_logout.status_code=}")

    # Redirect要求を返す
    # TODO:画面の構成決定後に遷移決定
    response = redirect(None)

    # ArgoCDのセッション情報をブラウザから削除
    response.set_cookie("argocd.oauthstate", "", path=f"{ARGOCD_EXTERNAL_BASEPATH}/auth", httponly=True, secure=True, samesite='Lax')
    response.set_cookie("argocd.token", "", path=f"{ARGOCD_EXTERNAL_BASEPATH}", httponly=True, secure=True, samesite='Lax')

    return response


def argocd_sso_id(organization_id):
    """argocdのSSO定義ID / argocd SSO definition ID
        configmap argocd-cm.dex.config connectors[*].idの定義 / configmap argocd-cm.dex.config connectors[*].id definition

    Args:
        organization_id (str): organization id

    Returns:
        str: argocd sso id
    """
    return f"exastro.{organization_id}"
