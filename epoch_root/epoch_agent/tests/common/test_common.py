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
