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


def main():
    with closing(DBconnector().connect_admin()) as conn, conn.cursor() as cursor:
        #
        # Database user generate script output
        #
        with open(os.path.join(os.environ.get('INITIAL_DATA_DEST'), 'create_users.sql'), mode="w") as fp_sql:
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
                cursor.execute("show create user %(user)s@%(host)s", {"user": user['User'], "host": user['Host']})
                create_user = cursor.fetchone()
                fp_sql.writelines([
                    f"{create_user[list(create_user.keys())[0]]};\n",
                ])

                cursor.execute("show grants for %(user)s@%(host)s", {"user": user['User'], "host": user['Host']})
                grants_users = cursor.fetchall()
                fp_sql.writelines([
                    f"{grant_user[list(grant_user.keys())[0]]};\n" for grant_user in grants_users
                ])
        #
        # Databases export
        #
        # get all database list
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
        databases = [database['SCHEMA_NAME'] for database in cursor.fetchall()]

        # databases export
        subprocess.run([*[
            "mysqldump", "-u", os.environ.get('DB_ADMIN_USER'), f"-p{os.environ.get('DB_ADMIN_PASSWORD')}", "-h", os.environ.get('DB_HOST'),
            "--result-file", os.path.join(os.environ.get('INITIAL_DATA_DEST'), 'create_databases.sql'),
            "--databases"], *databases])

    return 0


if __name__ == '__main__':
    ret = main()
    exit(ret)

