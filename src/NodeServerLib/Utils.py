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

