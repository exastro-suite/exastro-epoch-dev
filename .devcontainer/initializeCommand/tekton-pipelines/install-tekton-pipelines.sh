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
if [ -z "${TEKTON_OPERATOR_VERSION}" ]; then
    echo "** ERROR: TEKTON_OPERATOR_VERSION undefined (.env settings)"
    CHECK_RESULT='NG'
fi
if [ ${CHECK_RESULT} != 'OK' ]; then
    exit 1
fi

kubectl apply -f https://storage.googleapis.com/tekton-releases/operator/previous/${TEKTON_OPERATOR_VERSION}/release.yaml

kubectl apply -f https://raw.githubusercontent.com/tektoncd/operator/main/config/crs/kubernetes/config/basic/operator_v1alpha1_config_cr.yaml

exit 0
