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

import inspect
import connexion

import globals
from common_library.common.db_init import DBinit
from common_library.common import common
from common_library.common import multi_lang


@common.api_common_decorator
def organization_create(body, organization_id):  # noqa: E501
    """Create creates an organization

     # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param organization_id: 
    :type organization_id: str

    :rtype: ResponseOk
    """
    globals.logger.info(f"### func:{inspect.currentframe().f_code.co_name}")

    r = connexion.request
    user_id = r.headers.get("User-id")

    dbinit = DBinit()
    org_dbinfo = dbinit.generate_dbinfo(dbinit.prefix_org_db)

    try:
        # organization database 作成
        # create organization database
        dbinit.create_database(org_dbinfo)

        # Table 作成
        # create table in organization database
        dbinit.create_table_organizationdb(org_dbinfo)

        # organization database 接続情報登録
        # organization database connect infomation registration
        dbinit.insert_organization_dbinfo(org_dbinfo, organization_id, user_id)

    except Exception as e:
        globals.logger.error(f"create organization database error:{str(e)}")

        dbinit.drop_database(org_dbinfo)

        message_id = "500-02015"  # TODO
        message = multi_lang.get_text(
            message_id,
            "Organization Database 作成に失敗しました(対象ID:{0} database:{1})",
            organization_id,
            org_dbinfo.db_database,
        )
        raise common.InternalErrorException(message_id=message_id, message=message)

    return common.response_200_ok(None)
