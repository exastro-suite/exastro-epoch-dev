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

GITLAB_NAMESPACE=gitlab

echo "---------------------------------------------------------------------------------"
echo "-- Start ${BASENAME}"
echo "---------------------------------------------------------------------------------"

# set parameter
. ${REPOROOT}/.devcontainer/.env

# check parameters
CHECK_RESULT='OK'
if [ -z "${GITLAB_PROTOCOL}" ]; then
    echo "** ERROR: GITLAB_PROTOCOL undefined (.env settings)"
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
if [ -z "${GITLAB_ROOT_PASSWORD}" ]; then
    echo "** ERROR: GITLAB_ROOT_PASSWORD undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ -z "${GITLAB_ROOT_TOKEN}" ]; then
    echo "** ERROR: GITLAB_ROOT_TOKEN undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ ${CHECK_RESULT} != 'OK' ]; then
    exit 1
fi

#
# Generate epoch-gitlab.yaml
#
sed -e "s/{{GITLAB_PROTOCOL}}/${GITLAB_PROTOCOL}/g" \
    -e "s/{{GITLAB_HOST}}/${GITLAB_HOST}/g" \
    -e "s/{{GITLAB_PORT}}/${GITLAB_PORT}/g" \
    -e "s/{{GITLAB_REGISTORY_PORT}}/${GITLAB_REGISTORY_PORT}/g" \
    -e "s/{{GITLAB_ROOT_PASSWORD}}/${GITLAB_ROOT_PASSWORD}/g" \
    -e "s/{{GITLAB_ROOT_TOKEN}}/${GITLAB_ROOT_TOKEN}/g" \
    ${BASEDIR}/epoch-gitlab.yaml > /tmp/epoch-gitlab.yaml

#
# create namespace
#
(kubectl get ns ${GITLAB_NAMESPACE} &> /dev/null) || kubectl create ns ${GITLAB_NAMESPACE}

#
# apply gitlab.yaml
#
kubectl apply -n ${GITLAB_NAMESPACE} -f /tmp/epoch-gitlab.yaml

exit 0
