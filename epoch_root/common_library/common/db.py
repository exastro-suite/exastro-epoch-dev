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

from contextlib import closing
import os
import pymysql
import json

from common_library.common import common
from common_library.common import encrypt
from common_library.common import multi_lang

import globals


class DBconnector:
    """database connection class
    """

    SQL_WORKSPACE_DB_INFO = """
    SELECT DB_HOST, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD
    FROM T_WORKSPACE_DB
    WHERE ORGANIZATION_ID = %s
    AND WORKSPACE_ID = %s
    """

    SQL_ORGANIZATION_DB_INFO = """
    SELECT DB_HOST, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD
    FROM T_ORGANIZATION_DB
    WHERE ORGANIZATION_ID = %s
    """

    class DBinfo:
        """dbinfo
        """
        db_host: str
        db_port: int
        db_database: str
        db_user: str
        db_password: str

        def __init__(self):
            self.db_host = ""
            self.db_port = 3306
            self.db_database = ""
            self.db_user = ""
            self.db_password = ""

    def __get_dbinfo_epoch(self):
        """get epochdb dbinfo

        Returns:
            DBinfo: epochdb dbinfo
        """
        epochdb = self.DBinfo()
        epochdb.db_host = os.environ.get('DB_HOST')
        epochdb.db_port = 3306
        epochdb.db_database = os.environ.get('DB_DATABASE')
        epochdb.db_user = os.environ.get('DB_USER')
        epochdb.db_password = encrypt.encrypt_str(os.environ.get('DB_PASSWORD'))
        return epochdb

    def __get_dbinfo_admin(self):
        """get admin dbinfo

        Returns:
            DBinfo: admin dbinfo
        """
        db_admin = self.DBinfo()
        db_admin.db_host = os.environ.get('DB_HOST')
        db_admin.db_port = 3306
        db_admin.db_database = ""
        db_admin.db_user = os.environ.get('DB_ADMIN_USER')
        db_admin.db_password = encrypt.encrypt_str(os.environ.get('DB_ADMIN_PASSWORD'))
        return db_admin

    def __get_dbinfo_organization(self, organization_id):
        """get organization dbinfo

        Args:
            organization_id (str): organization id

        Returns:
            DBinfo: organization dbinfo
        """
        with closing(self.connect_epochdb()) as conn:
            with conn.cursor() as cursor:
                sql = self.SQL_ORGANIZATION_DB_INFO
                cursor.execute(sql, (organization_id, ))
                result = cursor.fetchone()

        orgdb = self.DBinfo()
        if result:
            orgdb.db_host = result.get('DB_HOST')
            orgdb.db_port = result.get('DB_PORT')
            orgdb.db_database = result.get('DB_DATABASE')
            orgdb.db_user = result.get('DB_USER')
            orgdb.db_password = result.get('DB_PASSWORD')
        else:
            globals.logger.error(f"organization not found id:{organization_id}")
            message_id = "404-00001"
            message = multi_lang.get_text(
                message_id,
                "organization not found id:{0}",
                organization_id
            )
            raise common.NotFoundException(message_id=message_id, message=message)

        return orgdb

    def __get_dbinfo_workspace(self, organization_id, workspace_id):
        """get workspace dbinfo

        Args:
            organization_id (str): organization id
            workspace_id (str): workspace id

        Returns:
            DBinfo: workspace dbinfo
        """
        with closing(self.connect_orgdb(organization_id)) as conn:
            with conn.cursor() as cursor:
                sql = self.SQL_WORKSPACE_DB_INFO
                cursor.execute(sql, (organization_id, workspace_id, ))
                result = cursor.fetchone()

        info = self.DBinfo()
        if result:
            info.db_host = result.get('DB_HOST')
            info.db_port = result.get('DB_PORT')
            info.db_database = result.get('DB_DATABASE')
            info.db_user = result.get('DB_USER')
            info.db_password = result.get('DB_PASSWORD')
        else:
            globals.logger.error(f"workspace not found organization_id:{organization_id} workspace_id:{workspace_id}")
            message_id = "404-00002"
            message = multi_lang.get_text(
                message_id,
                "workspace not found organization_id:{0} workspace_id:{1}",
                organization_id,
                workspace_id
            )
            raise common.NotFoundException(message_id=message_id, message=message)

        return info

    def get_dbinfo_organization(self, organization_id):
        """get organization dbinfo

        Args:
            organization_id (str): organization id

        Returns:
            DBinfo: organization dbinfo
        """
        return self.__get_dbinfo_organization(organization_id)

    def get_dbinfo_workspace(self, organization_id, workspace_id):
        """get workspace dbinfo

        Args:
            organization_id (str): organization id
            workspace_id (str): workspace id

        Returns:
            DBinfo: organization dbinfo
        """
        return self.__get_dbinfo_workspace(organization_id, workspace_id)

    def connection(self, dbinfo: DBinfo):
        """connect database

        Args:
            dbinfo (DBinfo): dbinfo

        Returns:
            pymysql.connections.Connection: connection
        """
        conn = pymysql.connect(
            host=dbinfo.db_host,
            database=dbinfo.db_database,
            user=dbinfo.db_user,
            password=encrypt.decrypt_str(dbinfo.db_password),
            port=dbinfo.db_port,
            charset='utf8mb4',
            collation='utf8mb4_general_ci',
            cursorclass=pymysql.cursors.DictCursor,
            max_allowed_packet=536_870_912  # 512MB
        )
        return conn

    def connect_admin(self) -> pymysql.connections.Connection:
        """connect database at admin

        Returns:
            pymysql.connections.Connection: admin connection
        """
        db_admin = self.__get_dbinfo_admin()
        conn = self.connection(db_admin)
        return conn

    def connect_epochdb(self) -> pymysql.connections.Connection:
        """connect database at epoch

        Returns:
            pymysql.connections.Connection: epoch connection
        """
        epochdb = self.__get_dbinfo_epoch()
        conn = self.connection(epochdb)
        return conn

    def connect_orgdb(self, organization_id: str) -> pymysql.connections.Connection:
        """connect database at organization

        Args:
            organization_id (str): organization_id

        Returns:
            pymysql.connections.Connection: organization connection
        """
        orgdb = self.__get_dbinfo_organization(organization_id)
        conn = self.connection(orgdb)
        return conn

    def connect_workspacedb(self, organization_id: str, workspace_id: str) -> pymysql.connections.Connection:
        """connect database at workspace

        Args:
            organization_id (str): organization id
            workspace_id (str): workspace id

        Returns:
            pymysql.connections.Connection: organization connection
        """
        db = self.__get_dbinfo_workspace(organization_id, workspace_id)
        conn = self.connection(db)
        return conn
