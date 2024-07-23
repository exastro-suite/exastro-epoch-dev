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

import globals
from common_library.common.db import DBconnector
from .libs import queries_db_migration


def main():
    with closing(DBconnector().connect_epochdb()) as conn, conn.cursor() as cursor:
        for query in queries_db_migration.CREATE_TABLES:
            globals.logger.info(f'EXECUTE SQL:{query}')
            cursor.execute(query)

        conn.commit()

    return 0


if __name__ == '__main__':
    ret = main()
    exit(ret)
