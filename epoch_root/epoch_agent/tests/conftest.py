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

import pytest

import os
import os.path

from common_library.common import multi_lang
from common_resources.en import language


@pytest.fixture(scope='session', autouse=True)
def check_pytest_ini():
    app_root_dir = os.path.dirname(os.path.dirname(__file__))
    if not os.path.isfile(os.path.join(app_root_dir, 'pytest.ini')):
        raise Exception('Not Exists pytest.ini')


@pytest.fixture(scope='function', autouse=True)
def data_initalize():
    """データー初期化

    """
    pass


@pytest.fixture(autouse=True)
def multi_lang_get_text(mocker):
    """multi_lang.get_textモック
        unit testではLanguage textが登録されていない場合、エラーを引き起こします

    Args:
        mocker (obj): mocker

    Returns:
        _type_: _description_
    """
    multi_lang_get_text = multi_lang.get_text

    def mocked_function(text_id, origin_text, *args):
        if text_id is not None and text_id != '000-00000':
            assert text_id in language.LanguageList.lang_array, f'Check lang_array Text id : {text_id}'
        return multi_lang_get_text(text_id, origin_text, *args)

    mocker.patch.object(multi_lang, 'get_text', side_effect=mocked_function)
