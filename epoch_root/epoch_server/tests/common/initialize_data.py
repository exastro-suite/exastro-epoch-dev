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

import os
from contextlib import closing
import subprocess

from common_library.common.db import DBconnector
from common_library.common.db_init import DBinit

PREFIX_ORG_DB_USER = DBinit.prefix_org_db
PREFIX_WS_DB_USER = DBinit.prefix_workspace_db
PREFIX_ORG_DB = DBinit.prefix_org_db
PREFIX_WS_DB = DBinit.prefix_workspace_db


def drop_users():
    with closing(DBconnector().connect_admin()) as conn, conn.cursor() as cursor:

        cursor.execute("""
            SELECT * FROM mysql.user
                WHERE   user like %(prefix_org_db_user_like)s
                OR      user like %(prefix_ws_db_user_like)s
                OR      user =    %(epoch_db_user)s
        """, {
            "prefix_org_db_user_like": (PREFIX_ORG_DB_USER + '%'),
            "prefix_ws_db_user_like": (PREFIX_WS_DB_USER + '%'),
            "epoch_db_user": os.environ.get('DB_USER')
        })
        users = cursor.fetchall()

        for user in users:
            cursor.execute("DROP USER %(user)s@%(host)s", {"user": user['User'], "host": user['Host']})


def drop_databases():
    with closing(DBconnector().connect_admin()) as conn, conn.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM INFORMATION_SCHEMA.SCHEMATA
                WHERE   SCHEMA_NAME LIKE    %(prefix_org_db_like)s
                OR      SCHEMA_NAME LIKE    %(prefix_ws_db_like)s
                OR      SCHEMA_NAME =       %(epoch_db)s
        """, {
            "prefix_org_db_like": (PREFIX_ORG_DB + '%'),
            "prefix_ws_db_like": (PREFIX_WS_DB + '%'),
            "epoch_db": os.environ.get('DB_DATABASE')
        })

        databases = cursor.fetchall()

        for database in databases:
            cursor.execute(f"DROP DATABASE {database['SCHEMA_NAME']}")


def import_databases():
    sql_file = os.path.join(os.path.dirname(__file__), "..", "initial_data", "create_databases.sql")

    result_command = subprocess.run(
        f"mysql -u {os.environ['DB_ADMIN_USER']} -p{os.environ['DB_ADMIN_PASSWORD']} -h {os.environ['DB_HOST']} < {sql_file}",
        shell=True)

    if result_command.returncode != 0:
        raise Exception(f'FAILED : mysql command (create_databases.sql)')


def import_users():
    sql_file = os.path.join(os.path.dirname(__file__), "..", "initial_data", "create_users.sql")

    result_command = subprocess.run(
        f"mysql -u {os.environ['DB_ADMIN_USER']} -p{os.environ['DB_ADMIN_PASSWORD']} -h {os.environ['DB_HOST']} < {sql_file}",
        shell=True)

    if result_command.returncode != 0:
        raise Exception(f'FAILED : mysql command (create_users.sql)')
