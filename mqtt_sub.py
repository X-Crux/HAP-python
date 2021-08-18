import json
import logging
import os
import random
import subprocess
import threading
import signal
import time
import toml
import pickledb

from paho.mqtt import client as mqtt_client

data = toml.load("data.toml")
PID = pickledb.load('pid.db', False, True)
logging.basicConfig(level=logging.DEBUG, format="[%(module)s] %(message)s")
logger = logging.getLogger(__name__)


broker = data['default']['broker']
port = data['default']['port']
topic = data['default']['topic']
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = data['default']['username']
password = data['default']['password']
# PID = []


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        str_msg = msg.payload.decode()
        dict_msg = json.loads(str_msg)
        type_access = dict_msg['dtype']
        model_access = dict_msg['stype']
        name_access = dict_msg['name']
        id_access = dict_msg['id']
        value_access = dict_msg['svalue1']

        db = pickledb.load('data.db', False, True)
        ids = list(db.getall())
        restart = False
        print('/ ' * 70)
        if id_access not in ids:
            restart = True
        print('id_access:', id_access)
        print('ids:', ids)
        # for _id in ids:
        #     access_data = db.get(_id)
        #     print('access_data:', access_data)
        #     if not access_data['active']:
        #         print('--- ! --- Deleted:', _id)
        #         db.rem(_id)
        #         db.dump()
        #         restart = True

        current_time = int(time.time())
        values = {'value': value_access,
                  'type': type_access,
                  'model': model_access,
                  'name': name_access,
                  'current_time': str(current_time),
                  'timeout': 80,
                  'active': 1}

        db.set(id_access, values)
        db.dump()

        if restart:
            if len(list(db.getall())) == 1:
                t = threading.Thread(target=start_proc, args=())
                t.start()

            else:
                pid = PID.get('PID')
                os.kill(pid, signal.SIGINT)
                t = threading.Thread(target=start_proc, args=())
                t.start()
        print('/ ' * 70)

    client.subscribe(topic)
    client.on_message = on_message


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def start_proc():
    time.sleep(1)
    process = subprocess.Popen(['python', 'hk_runner.py'])
    PID.set('PID', process.pid)
    PID.dump()
    # PID.append(process.pid)


if __name__ == '__main__':
    db = pickledb.load('data.db', False, True)
    if len(list(db.getall())) != 0:
        try:
            pid = PID.get('PID')
            os.kill(pid, signal.SIGINT)
        except Exception:
            pass

        t = threading.Thread(target=start_proc, args=())
        t.start()

    client = connect_mqtt()
    subscribe(client)

    client.loop_forever()
