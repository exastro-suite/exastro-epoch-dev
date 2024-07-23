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

SQL_ORGANIZATION_CREATE_TABLES = [
    """
    -- ワークスペースDB管理情報 / workspace database management infomation
    CREATE TABLE IF NOT EXISTS T_WORKSPACE_DB
    (
        ORGANIZATION_ID                 VARCHAR(36) NOT NULL,
        WORKSPACE_ID                    VARCHAR(36) NOT NULL,
        DB_HOST                         VARCHAR(255),
        DB_PORT                         INT,
        DB_DATABASE                     VARCHAR(255),
        DB_USER                         VARCHAR(255),
        DB_PASSWORD                     VARCHAR(255),
        CREATE_TIMESTAMP                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        CREATE_USER                     VARCHAR(40),
        LAST_UPDATE_TIMESTAMP           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        LAST_UPDATE_USER                VARCHAR(40),
        PRIMARY KEY (ORGANIZATION_ID, WORKSPACE_ID)
    )ENGINE = InnoDB, CHARSET = utf8mb4, COLLATE = utf8mb4_bin, ROW_FORMAT=COMPRESSED ,KEY_BLOCK_SIZE=8;
    """,
]

SQL_INSERT_ORGANIZATION_DBINFO = """
INSERT INTO T_ORGANIZATION_DB (ORGANIZATION_ID, DB_HOST, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD, CREATE_USER, LAST_UPDATE_USER)
VALUES (%(organization_id)s, %(db_host)s, %(db_port)s, %(db_database)s, %(db_user)s, %(db_password)s, %(create_user)s, %(last_update_user)s)
"""

SQL_DELETE_ORGANIZATION_DBINFO = """
DELETE FROM T_ORGANIZATION_DB WHERE ORGANIZATION_ID = %(organization_id)s
"""

SQL_WORKSPACE_CREATE_TABLES = [
]

SQL_INSERT_WORKSPACE_DBINFO = """
INSERT INTO T_WORKSPACE_DB (ORGANIZATION_ID, WORKSPACE_ID, DB_HOST, DB_PORT, DB_DATABASE,
                            DB_USER, DB_PASSWORD, CREATE_USER, LAST_UPDATE_USER)
VALUES (%(organization_id)s, %(workspace_id)s, %(db_host)s, %(db_port)s, %(db_database)s,
                            %(db_user)s, %(db_password)s, %(create_user)s, %(last_update_user)s)
"""

SQL_DELETE_WORKSPACE_DBINFO = """
DELETE FROM T_WORKSPACE_DB
WHERE ORGANIZATION_ID = %(organization_id)s
AND WORKSPACE_ID = %(workspace_id)s
"""
