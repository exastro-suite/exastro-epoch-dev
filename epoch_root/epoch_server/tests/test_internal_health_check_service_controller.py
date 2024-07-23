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
# from unittest import mock
from tests.common import test_common, request_parameters

from libs import health_check_service_queries

import logging

logger = logging.getLogger(__name__)


def test_internal_health_check_liveness(connexion_client):
    """internal health check liveness api test

    Args:
        connexion_client (_type_): _description_
    """
    with test_common.requsts_mocker_default():

        response = connexion_client.get(
            "/internal-api/health-check/liveness",
            content_type='application/json',
            headers=request_parameters.request_headers("dummy_user_id"))

        assert response.status_code == 200

    with test_common.requsts_mocker_default(), \
            test_common.pymysql_execute_mocker(
                health_check_service_queries.SQL_QUERY_HEALTH_CHECK,
                raise_exception=Exception('DB execute Error')):

        response = connexion_client.get(
            "/internal-api/health-check/liveness",
            content_type='application/json',
            headers=request_parameters.request_headers("dummy_user_id"))

        assert response.status_code == 500


def test_internal_health_check_readiness(connexion_client):
    """internal health check readiness api test

    Args:
        connexion_client (_type_): _description_
    """
    with test_common.requsts_mocker_default():

        response = connexion_client.get(
            "/internal-api/health-check/readiness",
            content_type='application/json',
            headers=request_parameters.request_headers("dummy_user_id"))

        assert response.status_code == 200

    with test_common.requsts_mocker_default(), \
            test_common.pymysql_execute_mocker(
                health_check_service_queries.SQL_QUERY_HEALTH_CHECK,
                raise_exception=Exception('DB execute Error')):

        response = connexion_client.get(
            "/internal-api/health-check/readiness",
            content_type='application/json',
            headers=request_parameters.request_headers("dummy_user_id"))

        assert response.status_code == 500
