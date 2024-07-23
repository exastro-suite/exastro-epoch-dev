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

BASEDIR=$(dirname $0)

$(
    cd "${BASEDIR}";
    sudo docker compose rm -s -f;
)

ln -sf ${BASEDIR}/initial_data/mysql/create_databases.sql ${BASEDIR}/initial_data/create_databases.sql
ln -sf ${BASEDIR}/initial_data/mysql/create_users.sql ${BASEDIR}/initial_data/create_users.sql

sudo docker compose -f "${BASEDIR}/docker-compose.yml" -f "${BASEDIR}/docker-compose-mysql.yml" up;

$(
    cd "${BASEDIR}";
    sudo docker compose rm -s -f;
)
