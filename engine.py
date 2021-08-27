import sys
import time
import logging
import toml
from multiprocessing import Process
from domoticz import fresh_list
from run_hk import start_hk


logging.basicConfig(level=logging.DEBUG, format="[%(module)s] %(message)s")
log = logging.getLogger(__name__)
data = toml.load("data.toml")


def start():
    idxes_list = []
    t = Process(target=start_hk, args=(idxes_list,))

    while True:
        _url = data['domoticz']['url']
        idxes_temp = fresh_list(_url, log)  # idx list()

        restart = False

        for idx in idxes_temp:
            if idx not in idxes_list:
                restart = True

        for idx in idxes_list:
            if idx not in idxes_temp:
                restart = True

        if restart:
            idxes_list = idxes_temp

            if t.is_alive():
                try:
                    t.terminate()
                    log.debug("Process is terminating success")
                except Exception:
                    t.kill()
                    log.debug("Process is killing success")

            t = Process(target=start_hk, args=(idxes_list,))
            t.start()

        time.sleep(30)


if __name__ == '__main__':
    start()
    sys.exit(0)
