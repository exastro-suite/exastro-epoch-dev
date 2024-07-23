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
import time
import datetime
import pymysql
import os
from jinja2 import Template
from contextlib import closing

import globals
from libs import queries_common

WAIT_INTERVAL = 5


def wait_until_connect_to_db(host, user, password, database):
    """wait until connect to db

    Args:
        host (str): database host
        user (str): database user
        password (str): database password
        database (str): database name

    Returns:
        Connection: Database Connection
    """
    start_time = datetime.datetime.now()
    timeout_seconds_connect_db = int(os.environ.get("TIMEOUT_SECONDS_CONNECT_DB", "-1"))

    globals.logger.info(f'WAIT UNTIL CONNECT DATABASE({user}@{host}/{database})...')

    while True:
        try:
            conn = pymysql.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=3306,
                charset='utf8mb4',
                collation='utf8mb4_general_ci',
                cursorclass=pymysql.cursors.DictCursor,
            )
            break
        except Exception:
            if timeout_seconds_connect_db != -1 and datetime.datetime.now() > start_time + datetime.timedelta(seconds=timeout_seconds_connect_db):
                raise Exception(f"Connection to database timed out : {timeout_seconds_connect_db}s")

            time.sleep(WAIT_INTERVAL)

    return conn


def get_db_data_version(conn, lock=False):
    """ Get Database data version

    Args:
        conn (Connection): Database Connection
        lock (bool, optional): version record lock. Defaults to False.

    Returns:
        str: Database data version
    """
    with conn.cursor() as cursor:

        # Check Exists Version Table Exists
        globals.logger.debug('Check Exists Version Table')
        template = Template(source=queries_common.EXISTS_VERSION_TABLE)
        query = template.render(os.environ)
        globals.logger.debug(f'EXECUTE SQL:{query}')

        cursor.execute(query)
        result = cursor.fetchone()

        if result is None:
            # Not Exists Version Table
            globals.logger.debug('Not Exists Version Table')
            return None

        # Select version table
        globals.logger.debug('Get Version Table')
        if lock:
            template = Template(source=queries_common.SELECT_VERSION_TABLE_LOCK)
        else:
            template = Template(source=queries_common.SELECT_VERSION_TABLE)

        query = template.render(os.environ)
        globals.logger.debug(f'EXECUTE SQL:{query}')

        cursor.execute(query)
        result = cursor.fetchone()

        if result is None:
            # Not Exists Version Table
            globals.logger.debug('Not Exists Version Table Record')
            return None

        return result.get("VERSION")


def update_db_data_version(conn, version, update_user='system'):
    """Update Database data version

    Args:
        conn (Connection): Database Connection
        version (str): version
    """
    with conn.cursor() as cursor:
        globals.logger.info(f'UPDATE DATABASE VERSION : {version}')
        cursor.execute(queries_common.UPDATE_VERSION_TABLE, {"version": version, "last_update_user": update_user})


def insert_migration_history(version, result, message=None, create_user='system'):
    """Insert migration history

    Args:
        version (str): version
        result (str): "START" or "SUCCEED" or "FAILED"
        message (str): Error Message
        create_user (str, optional): user. Defaults to 'system'.
    """
    message_substr = message[:4095] if message is not None else None

    with closing(connect_epoch_db()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                queries_common.INSERT_MIGRATION_HISTORY,
                {
                    "version": version,
                    "result": result,
                    "message": message_substr,
                    "create_user": create_user,
                    "last_update_user": create_user
                }
            )
            conn.commit()


def connect_epoch_db():
    conn = pymysql.connect(
        host=os.environ.get('DB_HOST'),
        database=os.environ.get('DB_DATABASE'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        port=3306,
        charset='utf8mb4',
        collation='utf8mb4_general_ci',
        cursorclass=pymysql.cursors.DictCursor,
    )
    return conn

