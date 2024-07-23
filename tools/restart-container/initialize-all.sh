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
REPOROOT=$(realpath "${BASEDIR}/../..")

HOST_SSH_KEY=${REPOROOT}/.secrets/docker-host.pem

#
# set parameter
#
. ${REPOROOT}/.devcontainer/.env

#
# test kind clusterの削除
#
ssh -o StrictHostKeyChecking=no -i ${HOST_SSH_KEY} ${DEV_SERVER_USER}@${DEV_SERVER_HOST} "kind delete cluster --name=${KIND_CLUSTER_NAME}"

#
# volumeの削除
#
sudo rm -rf ${REPOROOT}/.volumes

#
# devcontainerの停止
#
nohup ssh -o StrictHostKeyChecking=no -i ${HOST_SSH_KEY} ${DEV_SERVER_USER}@${DEV_SERVER_HOST} 'docker rm -f $(docker ps -qa -f label=com.docker.compose.project=devcontainer)' >& /dev/null
