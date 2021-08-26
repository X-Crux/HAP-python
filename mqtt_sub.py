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
from forms import convert
from paho.mqtt import client as mqtt_client

data = toml.load("data.toml")
PID = pickledb.load('pid.db', False, True)
# db = pickledb.load('data.db', False, True)
logging.basicConfig(level=logging.DEBUG, format="[%(module)s] %(message)s")
log = logging.getLogger(__name__)


broker = data['mqtt']['broker']
port = data['mqtt']['port']
topic = data['mqtt']['topic']
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = data['mqtt']['username']
password = data['mqtt']['password']
# db = {}


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        str_msg = msg.payload.decode()
        dict_msg = json.loads(str_msg)
        # type_access = dict_msg['dtype']
        # model_access = dict_msg['stype']
        # name_access = dict_msg['name']
        # id_access = dict_msg['id']
        # value_access = dict_msg['svalue1']

        dev_id, _form, _type = convert(dict_msg)
        log.debug(f'Inner dev_id: {dev_id}')
        log.debug(f'Inner _type: {_type}')
        log.debug(f'Inner _form: {_form}')

        if dev_id:
            db = pickledb.load('data.db', False, True)
            ids = list(db.getall())
            # ids = list(db.keys())
            restart = False
            log.debug('/ ' * 40)

            if dev_id not in ids:
                # db[dev_id] = {_type: _form}
                _form = {_type: _form}
                db.set(dev_id, _form)
                db.dump()
                restart = True
            else:
                acc_data = db.get(dev_id)

                if _type not in list(acc_data.keys()):
                    restart = True

                acc_data[_type] = _form
                db.set(dev_id, acc_data)
                db.dump()

                # _form = {_type: _form}
                # db[dev_id].update(_form)
                # if _type not in list(db[dev_id].keys()):
                #     db[dev_id][_type] = _form
                #     restart = True

            log.debug(f'dev_id: {dev_id}')
            log.debug(f'ids: {ids}')

            for _id in ids:
                # acc_data = db[_id]
                acc_data = db.get(_id)

                for _type, _value in acc_data.items():

                    if not _value['active']:
                        log.debug(f'--- ! --- Deleted TYPE: {_id} {_type}')
                        new_data = acc_data
                        new_data.pop(_type)
                        # db[_id].pop(_type)
                        # if len(db[_id]) == 0:

                        if len(new_data) == 0:
                            log.debug(f'--- ! --- Deleted ID: {_id} {new_data}')
                            # log.debug(f'--- ! --- Deleted ID: {_id} {db[_id]}')
                            # db.pop(_id)
                            db.rem(_id)
                            db.dump()

                        else:
                            db.set(_id, new_data)
                            db.dump()

                        restart = True

            # current_time = int(time.time())
            # values = {'value': value_access,
            #           'type': type_access,
            #           'model': model_access,
            #           'name': name_access,
            #           'current_time': str(current_time),
            #           'timeout': 80,
            #           'active': 1}

            # db_s = pickledb.load('data.db', False, True)
            # db_s = db
            # db_s.set(id_access, values)
            # db_s.dump()

            # db_x = pickledb.load('data.db', False, True)

            if restart:
                try:
                    pid = PID.get('PID')
                    if pid:
                        os.kill(pid, signal.SIGINT)
                except Exception:
                    pass
                t = threading.Thread(target=start_proc, args=())
                t.start()

            log.debug('/ ' * 40)

    client.subscribe(topic)
    client.on_message = on_message


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            log.info("Connected to MQTT Broker!")
        else:
            log.error("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def start_proc():
    time.sleep(1)
    process = subprocess.Popen(['python3', 'hk_runner.py'])
    PID.set('PID', process.pid)
    PID.dump()


if __name__ == '__main__':
    db = pickledb.load('data.db', False, True)
    if len(list(db.getall())) != 0:
        try:
            pid = PID.get('PID')
            if pid:
                os.kill(pid, signal.SIGINT)
        except Exception:
            pass
        t = threading.Thread(target=start_proc, args=())
        t.start()

    client = connect_mqtt()
    subscribe(client)

    client.loop_forever()
