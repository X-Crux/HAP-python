"""An example of how to setup and start an Accessory.

This is:
1. Create the Accessory object you want.
2. Add it to an AccessoryDriver, which will advertise it on the local network,
    setup a server to answer client queries, etc.
"""
import logging
import signal
import time

import pickledb

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
import pyhap.loader as loader
from pyhap import camera
from pyhap.const import CATEGORY_SENSOR, CATEGORY_HUMIDIFIER

logging.basicConfig(level=logging.DEBUG, format="[%(module)s] %(message)s")
log = logging.getLogger(__name__)


class TemperatureSensor(Accessory):
    """Fake Temperature sensor."""

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temp = 0.0
        self.id = ''
        self.timeout = False

        serv_temp = self.add_preload_service('TemperatureSensor')
        self.char_temp = serv_temp.configure_char('CurrentTemperature')

    def set_id(self, _id):
        self.id = _id

    def current_temp(self, _db):
        access_data = _db.get(self.id)['Temp']
        try:
            self.temp = float(access_data['value'])
        except Exception:
            self.temp = -273.1
            log.debug(f'--- ! --- "value" - wrong type: {type(access_data["value"])}')

    def _timeout(self, _db):
        access_data = _db.get(self.id)['Temp']
        current_time = access_data['current_time']
        timeout = access_data['timeout']

        log.debug(f'{int(current_time)} + {timeout} <= {int(time.time())}')
        log.debug(f'{int(current_time) + timeout} <= {int(time.time())}')

        if (int(current_time) + timeout) <= int(time.time()):
            access_data['active'] = 0
            db_device = _db.get(self.id)
            db_device['Temp'] = access_data
            _db.set(self.id, db_device)
            _db.dump()
            self.timeout = True

    @Accessory.run_at_interval(3)
    async def run(self):
        _db = pickledb.load('data.db', False, True)
        self._timeout(_db)

        if not self.timeout:
            self.current_temp(_db)
            self.char_temp.set_value(self.temp)
        else:
            pass


class HumiditySensor(Accessory):
    """Fake Humidity sensor."""

    category = CATEGORY_HUMIDIFIER

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hum_level = 0.0
        self.id = ''
        self.timeout = False

        serv_humidity = self.add_preload_service('HumiditySensor')
        self.char_level = serv_humidity.configure_char('CurrentRelativeHumidity')

    def set_id(self, _id):
        self.id = _id

    def current_humidity(self, _db):
        access_data = _db.get(self.id)['Humidity']
        log.debug(f'Humidity value: {access_data["value"]}')
        try:
            self.hum_level = float(access_data['value'])
        except Exception:
            self.hum_level = 0.0
            log.debug(f'--- ! --- "value" - wrong type: {type(access_data["value"])}')

    def _timeout(self, _db):
        access_data = _db.get(self.id)['Humidity']
        current_time = access_data['current_time']
        timeout = access_data['timeout']

        log.debug(f'{int(current_time)} + {timeout} <= {int(time.time())}')
        log.debug(f'{int(current_time) + timeout} <= {int(time.time())}')

        if (int(current_time) + timeout) <= int(time.time()):
            access_data['active'] = 0
            db_device = _db.get(self.id)
            db_device['Humidity'] = access_data
            _db.set(self.id, db_device)
            _db.dump()
            self.timeout = True

    @Accessory.run_at_interval(3)
    async def run(self):
        _db = pickledb.load('data.db', False, True)
        self._timeout(_db)

        if not self.timeout:
            self.current_humidity(_db)
            self.char_level.set_value(self.hum_level)
        else:
            pass


def get_bridge(driver):
    """Call this method to get a Bridge instead of a standalone accessory."""
    db = pickledb.load('data.db', False, True)
    keys = list(db.getall())

    for key in keys:
        for _type, _value in db.get(key).items():
            log.debug('>  ' * 35)
            log.debug(f'Acc to add: {key}, {_type}, {_value}')
            log.debug('>  ' * 35)
            if _type == 'Temp':
                temp_sensor = get_temp_sensor(driver, key, db)
                bridge.add_accessory(temp_sensor)
            elif _type == 'Humidity':
                humidity_sensor = get_humidity_sensor(driver, key, db)
                bridge.add_accessory(humidity_sensor)

    return bridge


def get_temp_sensor(driver, acc_id, db):
    name = db.get(acc_id)['Temp']['name']
    model = db.get(acc_id)['Temp']['model']
    access = TemperatureSensor(driver, name)
    access.set_info_service(model=model, serial_number=acc_id)
    access.set_id(_id=acc_id)
    return access


def get_humidity_sensor(driver, acc_id, db):
    name = db.get(acc_id)['Humidity']['name']
    model = db.get(acc_id)['Humidity']['model']
    access = HumiditySensor(driver, name)
    access.set_info_service(model=model, serial_number=acc_id)
    access.set_id(_id=acc_id)
    return access


def get_accessory(driver):
    """Call this method to get a standalone Accessory."""
    return TemperatureSensor(driver, 'MyTempSensor')


# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)
bridge = Bridge(driver, 'Bridge')

# Change `get_accessory` to `get_bridge` if you want to run a Bridge.
driver.add_accessory(accessory=get_bridge(driver))

# We want SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)

# Start it!
driver.start()
