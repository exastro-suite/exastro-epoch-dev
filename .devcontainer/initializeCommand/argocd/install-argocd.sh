#!/bin/bash

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

BASEDIR=$(realpath $(dirname "$0"))
BASENAME=$(basename "$0")
REPOROOT=$(realpath "${BASEDIR}/../../..")

which helm &> /dev/null
if [ $? -ne 0 ]; then
    echo "** ERROR ** helm command not installed"
    exit 1
fi

echo "---------------------------------------------------------------------------------"
echo "-- Start ${BASENAME}"
echo "---------------------------------------------------------------------------------"

# set parameter
. ${REPOROOT}/.devcontainer/.env

# check parameters
CHECK_RESULT='OK'
if [ -z "${ARGOCD_CHART_VERSION}" ]; then
    echo "** ERROR: ARGOCD_CHART_VERSION undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${ARGOCD_APP_VERSION}" ]; then
    echo "** ERROR: ARGOCD_APP_VERSION undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${ARGOCD_HTTP_PORT}" ]; then
    echo "** ERROR: ARGOCD_HTTP_PORT undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${ARGOCD_HTTPS_PORT}" ]; then
    echo "** ERROR: ARGOCD_HTTPS_PORT undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${ARGOCD_ADMIN_PASSWORD}" ]; then
    echo "** ERROR: ARGOCD_ADMIN_PASSWORD undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${DEV_SERVER_HOST}" ]; then
    echo "** ERROR: DEV_SERVER_HOST undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${EXTERNAL_URL}" ]; then
    echo "** ERROR: EXTERNAL_URL undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ ${CHECK_RESULT} != 'OK' ]; then
    exit 1
fi

# argocd admin password hash
# ※see helm show value
_ARGOCD_ADMIN_PASSWORD=$(htpasswd -nbBC 10 "" ${ARGOCD_ADMIN_PASSWORD} | tr -d ':\n' | sed 's/$2y/$2a/')

# argocd netloc
_ARGOCD_EXTERNAL_NETLOC=$(echo "${EXTERNAL_URL}" | sed -e 's!^.*://!!' -e 's|/.*$||')

# argocd external hostname
_ARGOCD_EXTERNAL_HOSTNAME=$(echo "${EXTERNAL_URL}" | sed -e 's!^.*://!!' -e 's|/.*$||' -e 's|:.*$||')

#
# argo helm repo
#
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

#
# helm show values
#
helm show values argo/argo-cd --version=${ARGOCD_CHART_VERSION} > ${BASEDIR}/sample.argocd-values.yaml
# helm show values argo/argo-cd > ${BASEDIR}/sample.argocd-values.yaml

#
# Generate epoch-argocd-value.yaml
#
if [ -z "${EXTERNAL_URL_HOST_IP}" ]; then
    sed -e '/# if defined EXTERNAL_URL_HOST_IP/,/# endif defined EXTERNAL_URL_HOST_IP/d' \
        ${BASEDIR}/epoch-argocd-values.yaml > /tmp/epoch-argocd-values.yaml
else
    cp -f ${BASEDIR}/epoch-argocd-values.yaml /tmp/epoch-argocd-values.yaml
fi

sed -i \
    -e "s|{{HTTP_PROXY}}|${HTTP_PROXY}|g" \
    -e "s|{{HTTPS_PROXY}}|${HTTPS_PROXY}|g" \
    -e "s|{{NO_PROXY}}|${NO_PROXY}|g" \
    -e "s|{{ARGOCD_APP_VERSION}}|${ARGOCD_APP_VERSION}|g" \
    -e "s|{{DEV_SERVER_HOST}}|${DEV_SERVER_HOST}|g" \
    -e "s|{{EXTERNAL_URL}}|${EXTERNAL_URL}|g" \
    -e "s|{{_ARGOCD_EXTERNAL_NETLOC}}|${_ARGOCD_EXTERNAL_NETLOC}|g" \
    -e "s|{{_ARGOCD_EXTERNAL_HOSTNAME}}|${_ARGOCD_EXTERNAL_HOSTNAME}|g" \
    -e "s|{{EXTERNAL_URL_HOST_IP}}|${EXTERNAL_URL_HOST_IP}|g" \
    -e "s|{{ARGOCD_HTTP_PORT}}|${ARGOCD_HTTP_PORT}|g" \
    -e "s|{{ARGOCD_HTTPS_PORT}}|${ARGOCD_HTTPS_PORT}|g" \
    -e "s|{{_ARGOCD_ADMIN_PASSWORD}}|${_ARGOCD_ADMIN_PASSWORD}|g" \
    /tmp/epoch-argocd-values.yaml

# cat /tmp/epoch-argocd-values.yaml
# exit 0

#
# install argocd
#
helm upgrade -n exastro argocd argo/argo-cd -f /tmp/epoch-argocd-values.yaml --create-namespace --install --version=${ARGOCD_CHART_VERSION}
# helm upgrade -n exastro argocd argo/argo-cd -f /tmp/epoch-argocd-values.yaml --create-namespace --install

exit 0


