"""
The utils for NodeServer.

@author: FATESAIKOU
@date  : 03/19/2019
"""

import json

from urllib import request, parse
def GetTime(service_helper_url):
    request_url = "{}/?action={}".format(
        service_helper_url, 'GetLocaltime')

    result_raw = request.urlopen(request_url).read()
    timestamp = json.loads(result_raw.decode('utf-8'))['result']

    return timestamp

def SendRequest(target_url, action, args):
    request_url = "{}/?action={}&args={}".format(
        target_url, action, parse.quote(json.dumps(args)))

    result_raw = request.urlopen(request_url).read()

    return json.loads(result_raw.decode('utf-8'))

def SendToTangle(target_url, command):
    stringified = json.dumps(command)
    headers = {
        'content-type': 'application/json',
        'X-IOTA-API-Version': '1'
    }

    req = request.Request(target_url, data=bytes(stringified, 'utf-8'), headers=headers)
    ret = request.urlopen(req).read().decode('utf-8')

    return json.loads(ret)


import base64
def GetFile(target_info, file_name):
    if target_info['type'] == 'wifi':
        file_encoded = SendRequest(
            target_info['addr'],
            'DoTransmit',
            {'file_name': file_name}
        )['result']

        file_raw = base64.b64decode(file_encoded)
    elif target_info['type'] == 'bluetooth':
        file_raw = GetBluetoothFile(target_info['addr'], file_name, target_info['restart_addr'])

    return MakeTempFile(file_raw)

import time
from PyOBEX import client
def GetBluetoothFile(bluetooth_addr, file_name, restart_addr):
    mac_addr, port = bluetooth_addr.rsplit(':', 1)

    for i in range(1):
        try:
            c = client.Client(mac_addr, int(port))
            c.connect()
            file_raw = c.get(file_name)
            c.disconnect()
            break
        except OSError as e:
            print("Retry! [{}][{}][{}]".format(i + 1, type(e).__name__, e))
            RestartBluetooth(bluetooth_addr, restart_addr)
            file_raw = [None, None]

        time.sleep(1)

    return file_raw[1]

import tempfile
def MakeTempFile(file_raw):
    tmp_filename = tempfile.mktemp()

    with open(tmp_filename, 'wb') as tmp:
        tmp.write(file_raw)

    return tmp_filename

import subprocess
def RestartBluetooth(bluetooth_addr, restart_addr):
    command = "ssh {} 'sudo killall -9 obexpushd; \
            sudo obexpushd -B {} -o ~/testPY/IoTSFC/models -n \
            -t FTP >/dev/null 2>&1 &'".format(
                restart_addr, bluetooth_addr
            )

    p = subprocess.Popen(command, shell=True)
