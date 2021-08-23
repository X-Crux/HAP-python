import requests
# import json


def get_response(url, data, log):
    headers = {'Content-Type': 'application/json'}
    session = requests.Session()

    response = session.request(
        method='POST',
        url=url,
        json=data,
        headers=headers,
        timeout=8
    )

    log.debug(f'Response status: {response}')
    log.debug(f'Response data: {response.text}')

    return response.json()  # dict()


# http://192.168.1.1:8080/json.htm?type=command&param=devices_list
#
s = {
    "result":
        [
            {
                "name": "temp hall",
                "value": "5"  # idx
            },
            {
                "name": "\u0412\u043b\u0430\u0436\u043d\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u0437\u0430\u043b",
                "value": "6"  # idx
            }
        ],
    "status": "OK",
    "title": "GetDevicesList"
}

# http://192.168.1.1:8080/json.htm?type=devices&rid=5
#
d = {
    "ActTime": 1629544727,
    "app_version": "2021.1",
    "result":
        [
            {
                "AddjMulti": 1.0,
                "AddjMulti2": 1.0,
                "AddjValue": 0.0,
                "AddjValue2": 0.0,
                "BatteryLevel": 56,
                "CustomImage": 0,
                "Data": "24.3 C",
                # "Data" : "Humidity 51 %",
                "Description": "",
                "Favorite": 0,
                "HardwareDisabled": false,
                "HardwareID": 2,
                "HardwareName": "ZiGate",
                "HardwareType": "Zigate plugin",
                "HardwareTypeVal": 94,
                "HaveTimeout": false,
                "ID": "00158d0005734205",
                "LastUpdate": "2021-08-21 11:15:36",
                "Name": "temp hall",
                "Notifications": "false",
                "PlanID": "0",
                "PlanIDs":
                    [
                        1
                    ],
                "Protected": false,
                "ShowNotifications": true,
                "SignalLevel": 6,
                "SubType": "LaCrosse TX3",
                "Temp": 24.300000000000001,
                "Timers": "false",
                "Type": "Temp",
                "TypeImg": "temperature",
                "Unit": 5,
                "Used": 1,
                "XOffset": "0",
                "YOffset": "0",
                "idx": "5",
                "trend": 0
            }
        ],
    "status": "OK",
    "title": "Devices"
}

