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
PROJECT_NAME=$(basename ${BASEDIR})

export ENCRYPT_KEY=$(cat /dev/urandom | head -c 32 | base64)

#
# cleanup container
#
CONTAINER_ID=$(sudo docker ps -qa -f label=com.docker.compose.project=${PROJECT_NAME})
if [ -n "${CONTAINER_ID}" ]; then
    sudo docker rm ${CONTAINER_ID}
fi

#
# build migration
#
sudo docker compose -f ${BASEDIR}/docker-compose-mariadb.yml build

#
# create mariadb initialize data
#
sudo docker compose -f ${BASEDIR}/docker-compose-mariadb.yml up

#
# cleanup container
#
CONTAINER_ID=$(sudo docker ps -qa -f label=com.docker.compose.project=${PROJECT_NAME})
if [ -n "${CONTAINER_ID}" ]; then
    sudo docker rm ${CONTAINER_ID} > /dev/null
fi

#
# create mysql initialize data
#
sudo docker compose -f ${BASEDIR}/docker-compose-mysql.yml up

#
# cleanup container
#
CONTAINER_ID=$(sudo docker ps -qa -f label=com.docker.compose.project=${PROJECT_NAME})
if [ -n "${CONTAINER_ID}" ]; then
    sudo docker rm ${CONTAINER_ID} > /dev/null
fi

echo 'ENCRYPT_KEY = "'"${ENCRYPT_KEY}"'"' > ${BASEDIR}/../../initial_data/encrypt_key.py
