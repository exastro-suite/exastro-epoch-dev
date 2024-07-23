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
if [ -z "${ARGOWF_CHART_VERSION}" ]; then
    echo "** ERROR: ARGOWF_CHART_VERSION undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${ARGOWF_APP_VERSION}" ]; then
    echo "** ERROR: ARGOWF_APP_VERSION undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${ARGOWF_HTTP_PORT}" ]; then
    echo "** ERROR: ARGOWF_HTTP_PORT undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ ${CHECK_RESULT} != 'OK' ]; then
    exit 1
fi


#
# argo helm repo
#
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

#
# helm show values
#
helm show values argo/argo-workflows --version=${ARGOWF_CHART_VERSION} > ${BASEDIR}/sample.argo-workflows-values.yaml

#
# Generate epoch-argo-workflows-values.yaml
#
sed -e "s|{{ARGOWF_APP_VERSION}}|${ARGOWF_APP_VERSION}|g" \
    -e "s|{{ARGOWF_HTTP_PORT}}|${ARGOWF_HTTP_PORT}|g" \
    ${BASEDIR}/epoch-argo-workflows-values.yaml > /tmp/epoch-argo-workflows-values.yaml

#
# install argocd
#
helm upgrade -n exastro argo-workflows argo/argo-workflows -f /tmp/epoch-argo-workflows-values.yaml --create-namespace --install --version=${ARGOWF_CHART_VERSION}

exit 0


