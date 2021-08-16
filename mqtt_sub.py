import json
import logging
import os
import random
import subprocess
import threading
import signal
import time
import pickledb

from paho.mqtt import client as mqtt_client

db = pickledb.load('data.db', False, True)
logging.basicConfig(level=logging.DEBUG, format="[%(module)s] %(message)s")
logger = logging.getLogger(__name__)


broker = 'lytko.com'
port = 1883
topic = "Grigory/domoticz/#"
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'Grigory'
password = 'GrigoryPass'
PID = []


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        str_msg = msg.payload.decode()
        dict_msg = json.loads(str_msg)
        type_access = dict_msg['dtype']
        model_access = dict_msg['stype']
        name_access = dict_msg['name']
        id_access = dict_msg['id']
        value_access = dict_msg['svalue1']

        restart = False
        if id_access not in db.getall():
            restart = True

        values = {'value': value_access,
                  'type': type_access,
                  'model': model_access,
                  'name': name_access}

        db.set(id_access, values)
        db.dump()

        if restart:
            if len(db.getall()) == 1:
                t = threading.Thread(target=start_proc, args=())
                t.start()

            else:
                os.kill(PID.pop(-1), signal.SIGINT)
                t = threading.Thread(target=start_proc, args=())
                t.start()

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
    PID.append(process.pid)


if __name__ == '__main__':
    if len(db.getall()) != 0:
        t = threading.Thread(target=start_proc, args=())
        t.start()

    client = connect_mqtt()
    subscribe(client)

    client.loop_forever()
