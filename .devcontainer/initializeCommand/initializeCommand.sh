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

echo "---------------------------------------------------------------------------------"
echo "-- Start ${BASENAME}" - initialize volumes
echo "---------------------------------------------------------------------------------"

mkdir -p "${REPOROOT}/.volumes/exastro/log"
mkdir -p "${REPOROOT}/.volumes/storage"
mkdir -p "${REPOROOT}/.vscode_extensions/epoch-server/.vscode-server/extensions"
mkdir -p "${REPOROOT}/.vscode_extensions/epoch-server/.vscode-server-insiders/extensions"
mkdir -p "${REPOROOT}/.vscode_extensions/epoch-agent/.vscode-server/extensions"
mkdir -p "${REPOROOT}/.vscode_extensions/epoch-agent/.vscode-server-insiders/extensions"
mkdir -p "${REPOROOT}/.vscode_extensions/epoch-migration/.vscode-server/extensions"
mkdir -p "${REPOROOT}/.vscode_extensions/epoch-migration/.vscode-server-insiders/extensions"


# create test kind cluster
${BASEDIR}/kind-cluster/create-kind-cluster.sh

# install metrics-server
${BASEDIR}/metrics-server/install-metrics-server.sh

# install gitlab
${BASEDIR}/gitlab/install-gitlab.sh

# install argocd
${BASEDIR}/argocd/install-argocd.sh

# install tekton-pipelines
${BASEDIR}/tekton-pipelines/install-tekton-pipelines.sh

# install argo-workflows
${BASEDIR}/argo-workflows/install-argo-workflows.sh


echo "---------------------------------------------------------------------------------"
echo "-- finish ${BASENAME}"
echo "---------------------------------------------------------------------------------"
exit 0
