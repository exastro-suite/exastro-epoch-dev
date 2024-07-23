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
echo "-- Start ${BASENAME}"
echo "---------------------------------------------------------------------------------"
if [ "$1" != "detach" ]; then
    touch "/tmp/attach-devcontainer"
else
    rm  "/tmp/attach-devcontainer"
fi

pid=$(ps -ef | grep '[p]ython3 /app/agent_manager.py$' | awk '{print $2}')
if [ -n "$pid" ]; then
    kill $pid
fi

echo "---------------------------------------------------------------------------------"
echo "-- finish ${BASENAME}"
echo "---------------------------------------------------------------------------------"
exit 0
