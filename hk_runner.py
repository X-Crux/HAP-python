"""An example of how to setup and start an Accessory.

This is:
1. Create the Accessory object you want.
2. Add it to an AccessoryDriver, which will advertise it on the local network,
    setup a server to answer client queries, etc.
"""
import logging
import signal
import pickledb

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver
import pyhap.loader as loader
from pyhap import camera
from pyhap.const import CATEGORY_SENSOR

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")
db = pickledb.load('data.db', False, True)


class TemperatureSensor(Accessory):
    """Fake Temperature sensor, measuring every 3 seconds."""

    category = CATEGORY_SENSOR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temp = 0.0
        self.id = ''

        serv_temp = self.add_preload_service('TemperatureSensor')
        self.char_temp = serv_temp.configure_char('CurrentTemperature')

    def set_id(self, _id):
        self.id = _id

    def current_temp(self):
        _db = pickledb.load('data.db', False, True)
        access_data = _db.get(self.id)
        self.temp = float(access_data['value'])

    @Accessory.run_at_interval(3)
    async def run(self):
        self.current_temp()
        self.char_temp.set_value(self.temp)


def get_bridge(driver):
    """Call this method to get a Bridge instead of a standalone accessory."""
    bridge = Bridge(driver, 'Bridge')

    keys = db.getall()

    for key in keys:
        temp_sensor = get_temp_sensor(driver, key)
        bridge.add_accessory(temp_sensor)

    return bridge


def get_temp_sensor(driver, acc_id):
    access = TemperatureSensor(driver, db.get(acc_id)['name'])
    access.set_info_service(model=db.get(acc_id)['model'], serial_number=acc_id)
    access.set_id(_id=acc_id)
    return access


def get_accessory(driver):
    """Call this method to get a standalone Accessory."""
    return TemperatureSensor(driver, 'MyTempSensor')


# Start the accessory on port 51826
driver = AccessoryDriver(port=51826)

# Change `get_accessory` to `get_bridge` if you want to run a Bridge.
driver.add_accessory(accessory=get_bridge(driver))

# We want SIGTERM (terminate) to be handled by the driver itself,
# so that it can gracefully stop the accessory, server and advertising.
signal.signal(signal.SIGTERM, driver.signal_handler)

# Start it!
driver.start()
