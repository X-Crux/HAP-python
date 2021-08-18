import os
import time

import pickledb

PID = pickledb.load('pid.db', False, True)

os.system('python "mqtt_sub.py"')
time.sleep(1)
quit()
