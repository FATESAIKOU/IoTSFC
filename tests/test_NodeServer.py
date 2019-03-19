"""
A tester program for NodeServer.py

@author: FATESAIKOU
@date  : 05/03/2019
"""

import json

def test_DoVerify():
    action = 'DoVerify'
    args = {
        'process_obj': {
            'event_list': {
                'Start': 1552914354.8102083
                # ...
            },
            'request_desc': {
                'service_name': 'CNN_10',
                'request_ID': 1,
                'loadfactor': 2,
                'std_verification_cost': 1,
                'std_computing_cost': 10,
                'model_size': 3
            },
            'SFC_desc': {
                'token': '5c9597f3c8245907ea71a89d9d39d08e',
                'V_node': 0,
                'C_node': 0,
                'D_node': 0
            }
        },
        'debug': True
    }

    result = OpenUrl('http://localhost:8001', action, args)

    assert 'GotReq_V' in result['process_obj']['event_list'].keys()
    assert 'Verified' in result['process_obj']['event_list'].keys()
    assert 'GotReturn_V' in result['process_obj']['event_list'].keys()

def test_DoCompute():
    action = 'DoCompute'
    args = {
        'process_obj': {
            'event_list': {
                'Start': 1552914354.8102083
                # ...
            },
            'request_desc': {
                'service_name': 'CNN_10',
                'request_ID': 1,
                'loadfactor': 2,
                'std_verification_cost': 1,
                'std_computing_cost': 10,
                'model_size': 3
            },
            'SFC_desc': {
                'token': '5c9597f3c8245907ea71a89d9d39d08e',
                'V_node': 0,
                'C_node': 1,
                'D_node': 2
            }
        },
        'debug': True
    }

    result = OpenUrl('http://localhost:8001', action, args)

    assert 'GotReq_C' in result['process_obj']['event_list'].keys()
    assert 'GotModel' in result['process_obj']['event_list'].keys()
    assert 'Computed' in result['process_obj']['event_list'].keys()

def test_DoTransmit():
    action = 'DoTransmit'
    args = {
        'model_name': 'CNN_10',
        'debug': True
    }

    result = OpenUrl('http://localhost:8001', action, args)

    assert args['model_name'] == result['result']
    assert True


""" Http toolkits """
from urllib import request, parse
def OpenUrl(url_base, action, args):
    # Pack action & args into query url -> send request
    result_raw = request.urlopen(url_base
        + '?action=' + parse.quote(action)
        + '&args=' + parse.quote(json.dumps(args))
    ).read()

    # Load result to json & return
    return json.loads(result_raw)

