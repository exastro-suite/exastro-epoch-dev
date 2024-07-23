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
import signal
import globals

# 終了指示のシグナル受信
process_terminate = False   # SIGTERM or SIGINT signal
process_sigterm = False     # SIGTERM signal (Jobを中断して終了する / Interrupt and end the job)
process_sigint = False      # SIGINT signal (Jobをやり終えて停止する / Finish the job and stop)


def job_manager_main_process():
    """main process
    """
    global process_terminate
    global process_sigterm
    global process_sigint
    process_terminate = False
    process_sigterm = False
    process_sigint = False

    # シグナルのハンドライベント設定 / Signal handler event settings
    signal.signal(signal.SIGTERM, job_manager_process_sigterm_handler)
    signal.signal(signal.SIGINT, job_manager_process_sigint_handler)

    globals.init(main_process=True)
    globals.logger.info('START main process')

    while not process_terminate:
        time.sleep(3)
        globals.logger.debug('main process loop')

    #
    # 終了処理 / End processing
    #
    globals.logger.info('TERMINATING main process')

    globals.logger.info('TERMINATE main process')
    globals.terminate()


def job_manager_process_sigterm_handler(signum, frame):
    """processへの終了指示（SIGTERMシグナル受信） / Termination instruction to process (sigterm signal reception)

    Args:
        signum (_type_): signal handler parameter
        frame (_type_): signal handler parameter
    """
    global process_terminate
    global process_sigterm
    process_terminate = True
    process_sigterm = True
    globals.logger.info('Receved signal : SIGTERM')


def job_manager_process_sigint_handler(signum, frame):
    """processへの終了指示（SIGINTシグナル受信） / Termination instruction to process (sigint signal reception)

    Args:
        signum (_type_): signal handler parameter
        frame (_type_): signal handler parameter
    """
    global process_terminate
    global process_sigint
    process_terminate = True
    process_sigint = True
    globals.logger.info('Receved signal : SIGINT')


if __name__ == '__main__':
    # main processメイン処理
    job_manager_main_process()
