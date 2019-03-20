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
    timestamp = json.loads(result_raw)['result']

    return timestamp

def SendRequest(target_url, action, args):
    request_url = "{}/?action={}&args={}".format(
        target_url, action, parse.quote(json.dumps(args)))

    result_raw = request.urlopen(request_url).read()

    return json.loads(result_raw)

def GetFile(target_info, file_name):
    if target_info['type'] == 'wifi':
        file_raw = SendRequest(
            target_info['addr'],
            'DoTransmit',
            file_name
        )
    elif target_info['type'] == 'bluetooth':
        file_raw = GetBluetoothFile(target_info['addr'], file_name)

    return MakeTempFile(file_raw)

from PyOBEX import client
def GetBluetoothFile(bluetooth_addr, file_name):
    mac_addr, port = bluetooth_addr.rsplit(':', 1)

    c = client.Client(mac_addr, int(port))
    c.connect()
    file_raw = c.get(file_name)
    c.disconnect()

    return file_raw[1]

import tempfile
def MakeTempFile(file_raw):
    tmp_filename = tempfile.mktemp()

    with open(tmp_filename, 'wb') as tmp:
        tmp.write(file_raw)

    return tmp_filename
