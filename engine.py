import sys
from pyhap.accessory_driver import AccessoryDriver
import json
import logging
import random
import signal
import time
import toml
from forms import convert
from paho.mqtt import client as mqtt_client
from pyhap.accessory import Accessory, Bridge
from pyhap.const import CATEGORY_SENSOR
from domoticz import fresh_list, acc_data
from multiprocessing import Process


data = toml.load("data.toml")
logging.basicConfig(level=logging.DEBUG, format="[%(module)s] %(message)s")
log = logging.getLogger(__name__)


broker = data['mqtt']['broker']
port = data['mqtt']['port']
topic = data['mqtt']['topic']
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = data['mqtt']['username']
password = data['mqtt']['password']
db = {}
# aid_db = {}
idxes_list = []
# idxes_rem = []


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        str_msg = msg.payload.decode()
        dict_msg = json.loads(str_msg)

        dev_id, _form, _type = convert(dict_msg)

        if dev_id:
            _form = {_type: _form}
            access = {dev_id: _form}

            log.debug(f"Added device: {access}")
            db.update(access)

        else:
            log.debug(f"Device not added: "
                      f"id - [{dev_id}], type - [{_type}], form - [{_form}]")

        log.debug(f"All current devices: {db}")

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


class TemperatureSensor(Accessory):
    """Temperature sensor."""

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temp = 0.0
        self.id = ''

        serv_temp = self.add_preload_service('TemperatureSensor')
        self.char_temp = serv_temp.configure_char('CurrentTemperature')

    def set_id(self, _id):
        self.id = _id

    def current_temp(self, value):
        self.temp = float(value)

    @Accessory.run_at_interval(3)
    async def run(self):
        try:
            acc_values = db[self.id]['Temp']
            self.current_temp(acc_values['value'])
        except Exception:
            pass

        self.char_temp.set_value(self.temp)


class HumiditySensor(Accessory):
    """Humidity sensor."""

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hum_level = 0.0
        self.id = ''

        serv_humidity = self.add_preload_service('HumiditySensor')
        self.char_level = serv_humidity.configure_char('CurrentRelativeHumidity')

    def set_id(self, _id):
        self.id = _id

    def current_humidity(self, value):
        self.hum_level = float(value)

    @Accessory.run_at_interval(3)
    async def run(self):
        try:
            acc_values = db[self.id]['Humidity']
            self.current_humidity(acc_values['value'])
        except Exception:
            pass

        self.char_level.set_value(self.hum_level)


def get_bridge(driver, bridge):
    """Call this method to get a Bridge instead of a standalone accessory."""
    _url = data['domoticz']['url']
    ids_list = []
    acc_current = {}

    for idx in idxes_list:
        acc_id, _form, _type = acc_data(_url, idx, log)
        _form = {_type: _form}
        full_acc = {acc_id: _form}

        ids_list.append(acc_id)
        acc_current.update(full_acc)

    # bridge = Bridge(driver, 'Bridge')

    log.debug("* " * 40)
    log.debug(acc_current)
    log.debug("* " * 40)
    for key in ids_list:
        log.debug(f"Add accessory id: {key}")
        for _type, _value in acc_current[key].items():
            log.debug('>  ' * 35)
            log.debug(f'Acc to add (idx {_value["idx"]}): {key}, {_type}, {_value}')
            log.debug('>  ' * 35)
            if _type == 'Temp':
                temp_sensor = get_temp_sensor(driver, key, acc_current)
                bridge.add_accessory(temp_sensor)
            elif _type == 'Humidity':
                humidity_sensor = get_humidity_sensor(driver, key, acc_current)
                bridge.add_accessory(humidity_sensor)

    # for aid, acc_value in bridge.accessories.items():
    #     print(f'{aid} | {acc_value} | {acc_value.display_name}')
    #     for _type in acc_current.values():
    #
    #         for sens in _type.values():
    #
    #             if acc_value.display_name == sens['name']:
    #                 acc = {str(sens['idx']): {"aid": aid, "name": acc_value.display_name}}
    #                 aid_db.update(acc)

    return bridge


def get_temp_sensor(driver, acc_id, acc_current):
    name = acc_current[acc_id]['Temp']['name']
    model = acc_current[acc_id]['Temp']['model']
    serial_number = acc_current[acc_id]['Temp']['idx']
    access = TemperatureSensor(driver, name)
    access.set_info_service(model=model, serial_number=serial_number)
    access.current_temp(acc_current[acc_id]['Temp']['value'])
    access.set_id(_id=acc_id)
    return access


def get_humidity_sensor(driver, acc_id, acc_current):
    name = acc_current[acc_id]['Humidity']['name']
    model = acc_current[acc_id]['Humidity']['model']
    serial_number = acc_current[acc_id]['Humidity']['idx']
    access = HumiditySensor(driver, name)
    access.set_info_service(model=model, serial_number=serial_number)
    access.current_humidity(acc_current[acc_id]['Humidity']['value'])
    access.set_id(_id=acc_id)
    return access


def get_accessory(driver):
    """Call this method to get a standalone Accessory."""
    return TemperatureSensor(driver, 'MyTempSensor')


def start_proc():
    client = connect_mqtt()
    subscribe(client)

    client.loop_forever()
    client.loop_stop()


def start_hk():
    mqtt_proc = Process(target=start_proc, args=(), daemon=True)
    mqtt_proc.start()

    # Start the accessory on port 51826
    driver = AccessoryDriver(port=51826, persist_file='accessory.state')
    bridge = Bridge(driver, 'Bridge')

    # Change `get_accessory` to `get_bridge` if you want to run a Bridge.
    driver.add_accessory(accessory=get_bridge(driver, bridge))
    driver.accessory

    # We want SIGTERM (terminate) to be handled by the driver itself,
    # so that it can gracefully stop the accessory, server and advertising.
    # signal.signal(signal.SIGINT, driver.signal_handler)
    signal.signal(signal.SIGTERM, driver.signal_handler)

    driver.start()

    log.debug(
        f"accessory_id values !!!: > > {bridge.accessories.values()}")

    # accessories = bridge.accessories

    aids = []
    for aid, accessory in bridge.accessories.items():
        aids.append(aid)
        print(f'{aid} | {accessory}')

    for aid in aids:
        bridge.accessories[aid].services.clear()
        bridge.accessories.pop(aid)

    bridge.driver.config_changed()
    driver.accessory = None
    driver.config_changed()
    # aid => accessory.display_name
    # idx => name => aid
    # db = {"1": {"aid": 1, "name": "name_123"}}

    # bridge.accessories.clear()

    # global idxes_rem
    # for idx, value in aid_db.items():
    #     aid = int(value['aid'])
    #
    #     for _idx in idxes_rem:
    #
    #         if _idx == idx:
    #             bridge.accessories.pop(aid)


    # log.debug(f"accessory_id items : > > {bridge.accessories.items()}")

    # idxes_rem.clear()
    mqtt_proc.terminate()


def start():

    global idxes_list
    hk_proc = Process(target=start_hk, args=())
    _url = data['domoticz']['url']

    while True:
        idxes_temp = fresh_list(_url, log)  # idx list()

        restart = False

        for idx in idxes_temp:
            if idx not in idxes_list:
                restart = True

        for idx in idxes_list:
            if idx not in idxes_temp:
                restart = True
                # idxes_rem.append(idx)

        if restart:
            idxes_list = idxes_temp


            # driver.accessory = None
            # driver.config_changed()
            # driver.stop()

            if hk_proc.is_alive():
                try:
                    hk_proc.terminate()
                    time.sleep(1)
                    log.debug("Process is terminating success")
                except Exception:
                    hk_proc.kill()
                    log.debug("Process is killing success")

            hk_proc = Process(target=start_hk, args=())
            hk_proc.start()

        time.sleep(40)


if __name__ == '__main__':

    start()
    sys.exit(0)
