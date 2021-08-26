import os
import signal
import subprocess
import threading
import time
import logging
import toml

from domoticz import fresh_list, acc_data


logging.basicConfig(level=logging.DEBUG, format="[%(module)s] %(message)s")
log = logging.getLogger(__name__)
data = toml.load("data.toml")
pid = []


def _start_hk():
    time.sleep(1)
    process = subprocess.Popen(['python3', 'run_hk.py'])
    pid.append(process.pid)
    while len(pid) > 1:
        pid.pop(0)
    # pid = process.pid


def start():
    ids_list = []

    while True:
        _url = data['domoticz']['url']
        idxes_list = fresh_list(_url, log)
        ids_temp = []

        for idx in idxes_list:
            acc_id, _form, _type = acc_data(_url, idx, log)
            _form = {_type: _form}

            ids_temp.append(acc_id)

        restart = False
        for _id in ids_temp:
            if _id not in ids_list:
                restart = True
                break

        for _id in ids_list:
            if _id not in ids_temp:
                restart = True
                break

        if restart:
            ids_list = ids_temp

            try:
                log.debug(f"PID: {pid}")
                if pid:
                    os.kill(pid[0], signal.SIGTERM)
            except Exception as exp:
                log.error(exp, exc_info=True)

            t = threading.Thread(target=_start_hk, args=())
            t.start()

        time.sleep(60)


if __name__ == '__main__':
    start()
