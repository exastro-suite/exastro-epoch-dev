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
if [ -z "${EPOCH_REPO_ROOT}" ]; then
    echo "** ERROR: EPOCH_REPO_ROOT undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${KIND_CLUSTER_NAME}" ]; then
    echo "** ERROR: KIND_CLUSTER_NAME undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${KIND_CLUSTER_IMAGE}" ]; then
    echo "** ERROR: KIND_CLUSTER_IMAGE undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${DEV_SERVER_HOST}" ]; then
    echo "** ERROR: DEV_SERVER_HOST undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${GITLAB_HOST}" ]; then
    echo "** ERROR: GITLAB_HOST undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${GITLAB_PORT}" ]; then
    echo "** ERROR: GITLAB_PORT undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${GITLAB_REGISTORY_PORT}" ]; then
    echo "** ERROR: GITLAB_REGISTORY_PORT undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${GITLAB_PROTOCOL}" ]; then
    echo "** ERROR: GITLAB_PROTOCOL undefined (.env settings)"
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
if [ ${CHECK_RESULT} != 'OK' ]; then
    exit 1
fi

#
# Check exists test kind cluster
#
CLUSTERS=$((kind get clusters 2> /dev/null )| grep ${KIND_CLUSTER_NAME} | wc -l)

if [ ${CLUSTERS} -eq 0 ]; then
    #
    # Generate epoch-kind-cluster.yaml
    #
    sed -e "s|{{EPOCH_REPO_ROOT}}|${EPOCH_REPO_ROOT}|g" \
        -e "s/{{DEV_SERVER_HOST}}/${DEV_SERVER_HOST}/g" \
        -e "s/{{GITLAB_HOST}}/${GITLAB_HOST}/g" \
        -e "s/{{GITLAB_PORT}}/${GITLAB_PORT}/g" \
        -e "s/{{GITLAB_REGISTORY_PORT}}/${GITLAB_REGISTORY_PORT}/g" \
        -e "s/{{GITLAB_PROTOCOL}}/${GITLAB_PROTOCOL}/g" \
        -e "s/{{ARGOCD_HTTP_PORT}}/${ARGOCD_HTTP_PORT}/g" \
        -e "s/{{ARGOCD_HTTPS_PORT}}/${ARGOCD_HTTPS_PORT}/g" \
        -e "s/{{ARGOWF_HTTP_PORT}}/${ARGOWF_HTTP_PORT}/g" \
        ${BASEDIR}/epoch-kind-cluster.yaml > /tmp/epoch-kind-cluster.yaml

    #
    # Create epoch-kind-cluster
    #
    kind create cluster \
        "--name=${KIND_CLUSTER_NAME}" \
        "--config=/tmp/epoch-kind-cluster.yaml" \
        --image "${KIND_CLUSTER_IMAGE}"

    #
    # Create kubeconfig
    #
    # kubernetes api serverのアドレスを0.0.0.0指定で生成しているため、configファイルの内容を置換する
    kind get kubeconfig --name=${KIND_CLUSTER_NAME} | \
        sed -e "/^  *server:/s|https://0\.0\.0\.0:|https://${DEV_SERVER_HOST}:|" > ~/.kube/config

    cp -f ~/.kube/config ${REPOROOT}/.secrets/kubeconfig
else
    echo "test kind cluster alredy created"
fi

exit 0
