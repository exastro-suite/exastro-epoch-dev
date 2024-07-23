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
import requests_mock
from unittest import mock

import pymysql
import copy


def requsts_mocker_default():
    """requstsのデフォルトmocker

    Returns:
        _type_: _description_
    """
    requests_mocker = requests_mock.Mocker()

    return requests_mocker


def pymysql_execute_mocker(sqlstmt, rows: list = None, raise_exception=None):
    """SQL実行のmock

    Args:
        sqlstmt (stmt): SQL that causes an exception
        rows (list): SQL return rows
        raise_exception (Exception): Raise Exception

    Returns:
        _type_: _description_
    """
    # オリジナルのpymysql.connectメソッドを退避
    pymysql_connect = pymysql.connect

    def mocked_function(host, database, user, password, port, charset, collation, cursorclass, max_allowed_packet=None):
        conn = pymysql_connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port,
            charset=charset,
            collation=collation,
            cursorclass=cursorclass,
            max_allowed_packet=max_allowed_packet
        )
        # pymysql.connectで返す内容を__pymysql_connection_mocked instanceにする
        return __pymysql_connection_mocked(conn, sqlstmt, rows, raise_exception)

    return mock.patch.object(pymysql, 'connect', side_effect=mocked_function)


class __pymysql_connection_mocked():
    """pymysqlのconnectインスタンス（モック時）
    """
    def __init__(self, conn, sqlstmt, rows, raise_exception):
        self.sqlstmt = sqlstmt
        self.conn = conn
        self.rows = rows
        self.raise_exception = raise_exception

    def begin(self):
        return self.conn.begin()

    def close(self):
        return self.conn.close()

    def commit(self):
        return self.conn.commit()

    def cursor(self):
        cursor = self.conn.cursor()
        return __pymysql_cursor_mocked(cursor, self.sqlstmt, self.rows, self.raise_exception)

    def rollback(self):
        return self.conn.rollback()


class __pymysql_cursor_mocked():
    """pymysqlのcursorインスタンス（モック時）
    """
    def __init__(self, cursor, sqlstmt, rows, raise_exception):
        self.cursor = cursor
        self.sqlstmt = sqlstmt
        self.rows = copy.deepcopy(rows)
        self.raise_exception = raise_exception
        self.match_sql = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()

    def close(self):
        self.cursor.close()

    def execute(self, query, args=None):
        if query == self.sqlstmt:
            self.match_sql = True

        if self.match_sql and self.raise_exception is not None:
            raise self.raise_exception

        return self.cursor.execute(query, args)

    def fetchall(self):
        if self.match_sql:
            return self.rows
        else:
            return self.cursor.fetchall()

    def fetchone(self):
        if self.match_sql:
            return self.rows.pop(0)
        else:
            return self.cursor.fetchone()


def delete_dict_item_written_info(target_vars):
    """delete written infomation item
        target_vars配下の作成日時・作成者・最終更新日時・最終更新者の情報を削除します
        ※target_varsの内容を書き換えますので注意

    Args:
        target_vars (_type_): _description_
    """
    delete_dict_item(
        target_vars,
        [
            'create_timestamp',
            'create_user',
            'last_update_timestamp',
            'last_update_user'
        ]
    )


def delete_dict_item(target_vars, delete_item_keys):
    """delete item
        target_vars配下の指定キーの情報を削除します
        ※target_varsの内容を書き換えますので注意

    Args:
        target_vars (_type_): _description_
        delete_item_keys (_type_): _description_
    """
    for target_var in (target_vars if type(target_vars) is list else [target_vars]):
        for delete_item_key in (delete_item_keys if type(delete_item_keys) is list else [delete_item_keys]):
            if delete_item_key in target_var:
                del target_var[delete_item_key]
