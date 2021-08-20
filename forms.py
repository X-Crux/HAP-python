import time


# data = {
#         'id': {
#             'Temp': {
#                 'idx': 5,
#                 'name': get_name(dev_data['name']),
#                 'type': dev_data['dtype'],
#                 'model': dev_data['stype'],
#                 'value': dev_data['svalue1'],
#                 'current_time': str(current_time),
#                 'timeout': 80,
#                 'active': 1
#             },
#             'Humidity': {
#                 'idx': 6,
#                 'name': get_name(dev_data['name']),
#                 'type': dev_data['dtype'],
#                 'model': dev_data['stype'],
#                 'value': dev_data['svalue1'],
#                 'current_time': str(current_time),
#                 'timeout': 80,
#                 'active': 1
#             }
#         }
#     }


def get_name(name):
    name = name.split(' ')
    name = name[-1]
    name = name.split('-')
    name = name[0]
    return name


def form(acc_info):
    current_time = int(time.time())
    _form = {
        'idx': 5,
        'name': get_name(acc_info['name']),
        'type': acc_info['dtype'],
        'model': acc_info['stype'],
        'value': acc_info['svalue1'],
        'current_time': str(current_time),
        'timeout': 80,
        'active': 1
    }
    return _form


def convert(dev_data):
    dev_id = dev_data['id']
    _type = dev_data['dtype']

    if _type in ['Temp', 'Humidity']:
        _form = form(dev_data)
        return dev_id, _form, _type
    else:
        return None, None, None


# {
#     "Battery": 59, -
#     "RSSI": 5, -
#     "description": "",
#     "dtype": "Humidity", +
#     "hwid": "2", -
#     "id": "00158d0005734205", +
#     "idx": 6, +
#     "name": "ZiGate - lumi.weather_Humi-00158d0005734205-01", +
#     "nvalue": 72,
#     "stype": "LaCrosse TX3",
#     "svalue1": "3",
#     "unit": 6
# }
#
# {
#     "Battery": 59,
#     "RSSI": 5,
#     "description": "",
#     "dtype": "Temp",
#     "hwid": "2",
#     "id": "00158d0005734205",
#     "idx": 5,
#     "name": "ZiGate - lumi.weather_Temp-00158d0005734205-01",
#     "nvalue": 24,
#     "stype": "LaCrosse TX3",
#     "svalue1": "24.3",
#     "unit": 5
# }