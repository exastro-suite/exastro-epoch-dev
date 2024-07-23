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

CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS T_ORGANIZATION_DB
    (
        ORGANIZATION_ID VARCHAR(36) NOT NULL,
        DB_HOST VARCHAR(255),
        DB_PORT INT,
        DB_DATABASE VARCHAR(255),
        DB_USER VARCHAR(255),
        DB_PASSWORD VARCHAR(255),
        CREATE_TIMESTAMP DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CREATE_USER VARCHAR(40),
        LAST_UPDATE_TIMESTAMP DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        LAST_UPDATE_USER VARCHAR(40),
        PRIMARY KEY (ORGANIZATION_ID)
    )
    """,
]
