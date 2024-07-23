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
if [ ${CHECK_RESULT} != 'OK' ]; then
    exit 1
fi

# argocd admin password hash
# ※see helm show value
_ARGOCD_ADMIN_PASSWORD=$(htpasswd -nbBC 10 "" ${ARGOCD_ADMIN_PASSWORD} | tr -d ':\n' | sed 's/$2y/$2a/')

#
# argo helm repo
#
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

#
# helm show values
#
helm show values argo/argo-cd --version=${ARGOCD_CHART_VERSION} > ${BASEDIR}/sample.argocd-values.yaml

#
# Generate epoch-argocd-value.yaml
#
sed -e "s|{{HTTP_PROXY}}|${HTTP_PROXY}|g" \
    -e "s|{{HTTPS_PROXY}}|${HTTPS_PROXY}|g" \
    -e "s|{{NO_PROXY}}|${NO_PROXY}|g" \
    -e "s|{{ARGOCD_APP_VERSION}}|${ARGOCD_APP_VERSION}|g" \
    -e "s|{{ARGOCD_HTTP_PORT}}|${ARGOCD_HTTP_PORT}|g" \
    -e "s|{{ARGOCD_HTTPS_PORT}}|${ARGOCD_HTTPS_PORT}|g" \
    -e "s|{{_ARGOCD_ADMIN_PASSWORD}}|${_ARGOCD_ADMIN_PASSWORD}|g" \
    ${BASEDIR}/epoch-argocd-values.yaml > /tmp/epoch-argocd-values.yaml

#
# install argocd
#
helm upgrade -n exastro argocd argo/argo-cd -f /tmp/epoch-argocd-values.yaml --create-namespace --install --version=${ARGOCD_CHART_VERSION}

exit 0


