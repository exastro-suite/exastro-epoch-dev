#   Copyright 2024 NEC Corporation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import pytest

import os
import os.path
import connexion
from contextlib import closing
from importlib import import_module
import base64

from flask import request
import logging
from logging.config import dictConfig as dictLogConf

from tests.common import initialize_data
import globals
from common_library.common.exastro_logging import ExastroLogRecordFactory, LOGGING
from common_library.common.db import DBconnector
from common_library.common import multi_lang, encrypt
from common_resources.en import language


@pytest.fixture(scope='session', autouse=True)
def check_pytest_ini():
    app_root_dir = os.path.dirname(os.path.dirname(__file__))
    if not os.path.isfile(os.path.join(app_root_dir, 'pytest.ini')):
        raise Exception('Not Exists pytest.ini')


@pytest.fixture(scope='session')
def connexion_client():
    """flask connexion test client 取得

    Returns:
        FlaskClient: _description_
    """
    app_root_dir = os.path.dirname(os.path.dirname(__file__))

    connexion_app = connexion.FlaskApp(
        __name__,
        specification_dir=f'{app_root_dir}/swagger/',
        server_args={'template_folder': '../templates'})

    connexion_app.add_api('swagger.yaml')
    
    app = connexion_app.app
    globals.init(app)

    org_factory = logging.getLogRecordFactory()
    logging.setLogRecordFactory(ExastroLogRecordFactory(org_factory, request))
    globals.logger = logging.getLogger('root')
    dictLogConf(LOGGING)

    globals.logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

    return connexion_app.app.test_client()


@pytest.fixture(scope="session")
def docker_compose_command() -> str:
    """pytest-docker docker-composeコマンド設定

    Returns:
        str: docker composeコマンド
    """
    if os.environ.get('DOCKER_COMPOSE_UP_UNITTEST_NODE', 'MANUAL') == 'AUTO':
        return "sudo docker compose "
    else:
        return ":"


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig, autouse=True):
    """pytest-docker docker-compose.ymlファイル指定

    Args:
        pytestconfig (_type_): pytestconfig fixtureパラメータ
        autouse (bool, optional): fixture自動起動=true

    Returns:
        str: docker-compose.ymlファイルパス
    """
    return os.path.join(os.path.dirname(__file__), "docker-compose.yml")


@pytest.fixture(scope='session', autouse=True)
def docker_compose_up(docker_ip, docker_services):
    """docker compose起動

    Args:
        docker_ip (_type_): docker_ip fixtureパラメータ
        docker_services (_type_): docker_services fixtureパラメータ
    """
    if os.environ.get('DOCKER_COMPOSE_UP_UNITTEST_NODE', 'MANUAL') == 'AUTO':
        # 起動待ち
        docker_services.wait_until_responsive(
            timeout=300.0,
            pause=1.0,
            check=lambda: is_responsive())
    else:
        # MANUAL MODEの場合はちょっと待って起動していない場合、エラーとする
        docker_services.wait_until_responsive(
            timeout=5.0,
            pause=1.0,
            check=lambda: is_responsive())


def is_responsive():
    """起動確認

    Returns:
        bool: 起動結果
    """
    try:
        with closing(DBconnector().connect_admin()):
            return True
    except Exception:
        return False


@pytest.fixture(scope='function', autouse=True)
def data_initalize():
    """データー初期化

    """
    initialize_data.drop_users()

    initialize_data.drop_databases()

    initialize_data.import_databases()

    initialize_data.import_users()


@pytest.fixture(autouse=True)
def encrypt_key(mocker):
    """unit test用のencrypt key設定
        Encrypt key settings for unit test

    Args:
        mocker (_type_): _description_
    """
    encrypt_key = import_module("tests.initial_data.encrypt_key")
    mocker.patch.object(encrypt, 'ENCRYPT_KEY', new=base64.b64decode(encrypt_key.ENCRYPT_KEY))


@pytest.fixture(autouse=True)
def multi_lang_get_text(mocker):
    """multi_lang.get_textモック
        unit testではLanguage textが登録されていない場合、エラーを引き起こします

    Args:
        mocker (obj): mocker

    Returns:
        _type_: _description_
    """
    multi_lang_get_text = multi_lang.get_text

    def mocked_function(text_id, origin_text, *args):
        if text_id is not None and text_id != '000-00000':
            assert text_id in language.LanguageList.lang_array, f'Check lang_array Text id : {text_id}'
        return multi_lang_get_text(text_id, origin_text, *args)

    mocker.patch.object(multi_lang, 'get_text', side_effect=mocked_function)
