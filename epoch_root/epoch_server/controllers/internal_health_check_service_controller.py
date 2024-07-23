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
from common_library.common import common, multi_lang
from common_library.common.db import DBconnector

from libs import health_check_service_queries


@common.api_common_decorator
def internal_health_check_liveness():  # noqa: E501
    """Internal health check liveness

     # noqa: E501


    :rtype: InlineResponse2002
    """
    try:
        with closing(DBconnector().connect_epochdb()) as conn:
            with conn.cursor() as cursor:
                # テスト用のSQLを実行 / Execute test SQL
                cursor.execute(health_check_service_queries.SQL_QUERY_HEALTH_CHECK)
                cursor.fetchone()
            return common.response_200_ok(None)
    except Exception:
        message_id = "500-01001"
        message = multi_lang.get_text(message_id, "health check failed")
        raise common.InternalErrorException(message_id=message_id, message=message)


@common.api_common_decorator
def internal_health_check_readiness():  # noqa: E501
    """Internal health check readiness

     # noqa: E501


    :rtype: InlineResponse2002
    """
    try:
        with closing(DBconnector().connect_epochdb()) as conn:
            with conn.cursor() as cursor:
                # テスト用のSQLを実行 / Execute test SQL
                cursor.execute(health_check_service_queries.SQL_QUERY_HEALTH_CHECK)
                cursor.fetchone()
            return common.response_200_ok(None)
    except Exception:
        message_id = "500-01001"
        message = multi_lang.get_text(message_id, "health check failed")
        raise common.InternalErrorException(message_id=message_id, message=message)
