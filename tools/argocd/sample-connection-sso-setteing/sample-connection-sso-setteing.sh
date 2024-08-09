#!/bin/bash
#
# 機能実装を行う前にSSO設定を行うためのSHELLスクリプト
# オーガナイゼーション作成後に実行
#
# Usage: connection-sso-setteing.sh organization_id
#

BASEDIR=$(realpath $(dirname "$0"))
BASENAME=$(basename "$0")

. /workspace/.devcontainer/.env

KEYCLOAK_BASEURL=http://keycloak:8080/auth
ARGOCD_NAMESPACE=exastro

if [ -z "$1" ]; then
    echo "Usage: ${BASENAME} organization_id"
    exit 1
fi
ORGANIZATION_ID=$1

#
# token発行
#
TOKEN=$(
    curl -Ss \
        -X POST \
        -H "Content-type: application/x-www-form-urlencoded" \
        -d "client_id=admin-cli" \
        -d "username=${KEYCLOAK_ADMIN}" \
        -d "password=${KEYCLOAK_ADMIN_PASSWORD}" \
        -d "grant_type=password" \
        "${KEYCLOAK_BASEURL}/realms/master/protocol/openid-connect/token" \
    | jq -r ".access_token"
)
if [ -z "${TOKEN}" ]; then
    echo "ERROR: get token failed"
    exit 9
fi

#
# argocd sso用client作成
#
sed -e  "s|{{ORGANIZATION_ID}}|${ORGANIZATION_ID}|g" \
    -e  "s|{{EXTERNAL_URL}}|${EXTERNAL_URL}|g"  \
    "${BASEDIR}/keycloak-client.json" \
| curl -Ss \
  -X  POST \
  -H  "Authorization: Bearer ${TOKEN}" \
  -H  "Content-type: application/json" \
  -d  @- \
  "${KEYCLOAK_BASEURL}/admin/realms/${ORGANIZATION_ID}/clients"

echo

#
# argocd sso設定
#
PATCH_FILE=/tmp/${BASENAME}.$$.yaml

sed -e  "s|{{ORGANIZATION_ID}}|${ORGANIZATION_ID}|g" \
    -e  "s|{{EXTERNAL_URL}}|${EXTERNAL_URL}|g"  \
    "${BASEDIR}/argocd-cm-header.yaml" \
    > "${PATCH_FILE}"

# ORGANIZATION LIST LOOP
curl -Ss \
    -H "Authorization: Bearer ${TOKEN}" \
    "${KEYCLOAK_BASEURL}/admin/realms" \
    | jq -r ".[].realm" \
| while read ORG_ID; do

    # ARGOCD SAML CLIENTの存在チェック
    ARGOCD_CLIENT_EXISTS=$(
        curl -Ss \
            -H "Authorization: Bearer ${TOKEN}" \
            "${KEYCLOAK_BASEURL}/admin/realms/${ORG_ID}/clients" \
            | jq -r '.[].clientId' \
            | grep "_${ORG_ID}-argocd-saml" \
            | wc -l \
    )
    if [ ${ARGOCD_CLIENT_EXISTS} -gt 0 ]; then
        # CADATA生成
        CADATA=$(
            curl -k -s "${KEYCLOAK_BASEURL}/realms/${ORG_ID}/protocol/saml/descriptor" | \
            sed \
                -e 's|^.*<ds:X509Data><ds:X509Certificate>||' \
                -e 's|</ds:X509Certificate></ds:X509Data>.*$||' \
                -e '1i-----BEGIN CERTIFICATE-----' \
                -e '$a-----END CERTIFICATE-----' | \
            base64 -w 0 \
        )

        # ファイルに追記
        sed -e  "s|{{ORGANIZATION_ID}}|${ORG_ID}|g" \
            -e  "s|{{EXTERNAL_URL}}|${EXTERNAL_URL}|g"  \
            -e  "s|{{CADATA}}|${CADATA}|g"  \
            "${BASEDIR}/argocd-cm-org-sso.yaml" \
            >> "${PATCH_FILE}"
    fi
done;

# ArgoCDに反映
kubectl patch cm argocd-cm -n "${ARGOCD_NAMESPACE}" --patch-file "${PATCH_FILE}"
