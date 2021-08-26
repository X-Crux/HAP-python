import requests
import json
from forms import convert_dom


def get_response(url, log):
    headers = {'Content-Type': 'application/json'}
    session = requests.Session()

    # response = session.request(
    #     method='POST',
    #     url=url,
    #     json=data,
    #     headers=headers,
    #     timeout=8
    # )

    response = session.request(
        method='GET',
        url=url,
        headers=headers,
        timeout=8
    )

    log.debug(f'Response status: {response}')

    return response.json()  # dict()


def acc_data(_url, idx, log):
    url = f'http://{_url}/json.htm?type=devices&rid={idx}'
    acc_info = get_response(url, log)['result'][0]
    _id, _form, _type = convert_dom(acc_info)
    return _id, _form, _type


def fresh_list(_url, log):
    url = f'http://{_url}/json.htm?type=command&param=devices_list'
    new_list_idxes = []
    fresh_info = get_response(url, log)

    for acc in fresh_info['result']:
        new_list_idxes.append(acc['value'])

    return new_list_idxes


# http://192.168.1.1:8080/json.htm?type=command&param=devices_list
#
# s = {
#     "result":
#         [
#             {
#                 "name": "temp hall",
#                 "value": "5"  # idx
#             },
#             {
#                 "name": "\u0412\u043b\u0430\u0436\u043d\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u0437\u0430\u043b",
#                 "value": "6"  # idx
#             }
#         ],
#     "status": "OK",
#     "title": "GetDevicesList"
# }

# http://192.168.1.1:8080/json.htm?type=devices&rid=5
#
# d = {
#     "ActTime": 1629544727,
#     "app_version": "2021.1",
#     "result":
#         [
#             {
#                 "AddjMulti": 1.0,
#                 "AddjMulti2": 1.0,
#                 "AddjValue": 0.0,
#                 "AddjValue2": 0.0,
#                 "BatteryLevel": 56,
#                 "CustomImage": 0,
#                 "Data": "24.3 C",
#                 # "Data" : "Humidity 51 %",
#                 "Description": "",
#                 "Favorite": 0,
#                 "HardwareDisabled": false,
#                 "HardwareID": 2,
#                 "HardwareName": "ZiGate",
#                 "HardwareType": "Zigate plugin",
#                 "HardwareTypeVal": 94,
#                 "HaveTimeout": false,
#                 "ID": "00158d0005734205",
#                 "LastUpdate": "2021-08-21 11:15:36",
#                 "Name": "temp hall",
#                 "Notifications": "false",
#                 "PlanID": "0",
#                 "PlanIDs":
#                     [
#                         1
#                     ],
#                 "Protected": false,
#                 "ShowNotifications": true,
#                 "SignalLevel": 6,
#                 "SubType": "LaCrosse TX3",
#                 "Temp": 24.300000000000001,
#                 "Timers": "false",
#                 "Type": "Temp",
#                 "TypeImg": "temperature",
#                 "Unit": 5,
#                 "Used": 1,
#                 "XOffset": "0",
#                 "YOffset": "0",
#                 "idx": "5",
#                 "trend": 0
#             }
#         ],
#     "status": "OK",
#     "title": "Devices"
# }

# acces = [{'aid': 1, 'services': [{'iid': 1, 'type': '3E', 'characteristics': [
#     {'iid': 2, 'type': '14', 'perms': ['pw'], 'format': 'bool'},
#     {'iid': 3, 'type': '20', 'perms': ['pr'], 'format': 'string', 'value': ''},
#     {'iid': 4, 'type': '21', 'perms': ['pr'], 'format': 'string', 'value': ''},
#     {'iid': 5, 'type': '23', 'perms': ['pr'], 'format': 'string',
#      'value': 'Bridge'},
#     {'iid': 6, 'type': '30', 'perms': ['pr'], 'format': 'string',
#      'value': 'default'},
#     {'iid': 7, 'type': '52', 'perms': ['pr'], 'format': 'string',
#      'value': ''}]}, {'iid': 8, 'type': 'A2', 'characteristics': [
#     {'iid': 9, 'type': '37', 'perms': ['pr', 'ev'], 'format': 'string',
#      'value': '01.01.00'}]}]}, {'aid': 2, 'services': [{'iid': 1, 'type': '3E',
#                                                         'characteristics': [
#                                                             {'iid': 2,
#                                                              'type': '14',
#                                                              'perms': ['pw'],
#                                                              'format': 'bool'},
#                                                             {'iid': 3,
#                                                              'type': '20',
#                                                              'perms': ['pr'],
#                                                              'format': 'string',
#                                                              'value': ''},
#                                                             {'iid': 4,
#                                                              'type': '21',
#                                                              'perms': ['pr'],
#                                                              'format': 'string',
#                                                              'value': 'LaCrosse TX3'},
#                                                             {'iid': 5,
#                                                              'type': '23',
#                                                              'perms': ['pr'],
#                                                              'format': 'string',
#                                                              'value': 'Tem2'},
#                                                             {'iid': 6,
#                                                              'type': '30',
#                                                              'perms': ['pr'],
#                                                              'format': 'string',
#                                                              'value': '14053'},
#                                                             {'iid': 7,
#                                                              'type': '52',
#                                                              'perms': ['pr'],
#                                                              'format': 'string',
#                                                              'value': ''}]},
#                                                        {'iid': 8, 'type': '8A',
#                                                         'characteristics': [
#                                                             {'iid': 9,
#                                                              'type': '11',
#                                                              'perms': ['pr',
#                                                                        'ev'],
#                                                              'format': 'float',
#                                                              'minStep': 0.1,
#                                                              'minValue': -273.1,
#                                                              'unit': 'celsius',
#                                                              'maxValue': 1000,
#                                                              'value': 0.0}]}]},
#          {'aid': 3, 'services': [{'iid': 1, 'type': '3E', 'characteristics': [
#              {'iid': 2, 'type': '14', 'perms': ['pw'], 'format': 'bool'},
#              {'iid': 3, 'type': '20', 'perms': ['pr'], 'format': 'string',
#               'value': ''},
#              {'iid': 4, 'type': '21', 'perms': ['pr'], 'format': 'string',
#               'value': 'LaCrosse TX3'},
#              {'iid': 5, 'type': '23', 'perms': ['pr'], 'format': 'string',
#               'value': 'TempSensor'},
#              {'iid': 6, 'type': '30', 'perms': ['pr'], 'format': 'string',
#               'value': '14051'},
#              {'iid': 7, 'type': '52', 'perms': ['pr'], 'format': 'string',
#               'value': ''}]}, {'iid': 8, 'type': '8A', 'characteristics': [
#              {'iid': 9, 'type': '11', 'perms': ['pr', 'ev'], 'format': 'float',
#               'minStep': 0.1, 'minValue': -273.1, 'unit': 'celsius',
#               'maxValue': 1000, 'value': 0.0}]}]}]
#
# bytes_code = b'HTTP/1.1 200 OK\r\nContent-Type: application/hap+json\r' \
#              b'\nContent-Length: 1899\r\n\r\n' \
#              b'{"accessories":' \
#              b'[{"aid":1,"services":' \
#                  b'[{"iid":1,"type":"3E","characteristics":' \
#                  b'[{"iid":2,"type":"14","perms":["pw"],"format":"bool"},' \
#                  b'{"iid":3,"type":"20","perms":["pr"],"format":"string","value":""},' \
#                  b'{"iid":4,"type":"21","perms":["pr"],"format":"string","value":""},' \
#                  b'{"iid":5,"type":"23","perms":["pr"],"format":"string","value":"Bridge"},' \
#                  b'{"iid":6,"type":"30","perms":["pr"],"format":"string","value":"default"},' \
#                  b'{"iid":7,"type":"52","perms":["pr"],"format":"string","value":""}]},' \
#                  b'{"iid":8,"type":"A2",' \
#                  b'"characteristics":' \
#                  b'[{"iid":9,"type":"37","perms":["pr","ev"],"format":"string","value":"01.01.00"}]}]},' \
#              b'{"aid":2,"services":' \
#              b'[{"iid":1,"type":"3E","characteristics":' \
#              b'[{"iid":2,"type":"14","perms":["pw"],"format":"bool"},' \
#              b'{"iid":3,"type":"20","perms":["pr"],"format":"string","value":""},' \
#              b'{"iid":4,"type":"21","perms":["pr"],"format":"string","value":"LaCrosse TX3"},' \
#              b'{"iid":5,"type":"23","perms":["pr"],"format":"string","value":"Tem2"},' \
#              b'{"iid":6,"type":"30","perms":["pr"],"format":"string","value":"14053"},' \
#              b'{"iid":7,"type":"52","perms":["pr"],"format":"string","value":""}]},' \
#              b'{"iid":8,"type":"8A",' \
#              b'"characteristics":' \
#              b'[{"iid":9,"type":"11","perms":["pr","ev"],"format":"float",' \
#              b'"minStep":0.1,"minValue":-273.1,"unit":"celsius",' \
#              b'"maxValue":1000,"value":0.0}]}]},{"aid":3,' \
#              b'"services":' \
#              b'[{"iid":1,"type":"3E","characteristics":' \
#              b'[{"iid":2,"type":"14","perms":["pw"],"format":"bool"},' \
#              b'{"iid":3,"type":"20","perms":["pr"],"format":"string","value":""},' \
#              b'{"iid":4,"type":"21","perms":["pr"],"format":"string","value":"LaCrosse TX3"},' \
#              b'{"iid":5,"type":"23","perms":["pr"],"format":"string","value":"TempSensor"},' \
#              b'{"iid":6,"type":"30","perms":["pr"],"format":"string","value":"14051"},' \
#              b'{"iid":7,"type":"52","perms":["pr"],"format":"string","value":""}]},' \
#              b'{"iid":8,"type":"8A",' \
#              b'"characteristics":' \
#              b'[{"iid":9,"type":"11","perms":["pr","ev"],"format":"float",' \
#              b'"minStep":0.1,"minValue":-273.1,"unit":"celsius",' \
#              b'"maxValue":1000,"value":0.0}]}]}]}'


