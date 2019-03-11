"""
A tester program for ServiceHelperServer.py

@author: FATESAIKOU
@date  : 03/05/2019
"""

import json


def test_UpdateGlobalParameter():
    action = 'UpdateGlobalParameter'
    args = {
        'init_obj': {
            'tolerance_sigma': 0.1,
            'node_num': 3
        },
        'debug': True
    }

    result = OpenUrl('http://localhost:8000', action, args)

    assert result['result'] == {'tolerance_sigma': 0.1, 'node_num': 3}

def test_GetSFC():
    action = 'GetSFC'
    args = {
        'request_desc': {
            'service_name': 'WTF',
            'request_ID': 1,
            'tolerance': 0.5,
            'std_verification_cost': 1,
            'std_computing_cost': 10,
            'model_size': 3
        },
        'debug': True
    }

    result = OpenUrl('http://localhost:8000', action, args)

    # assert result
    assert result['result']['token'] == '5c9597f3c8245907ea71a89d9d39d08e'
    assert 'V_node' in result['result'].keys()
    assert 'C_node' in result['result'].keys()
    assert 'D_node' in result['result'].keys()

def test_UpdateRL():
    action = 'UpdateRL'
    args = {
        'RL_rewards': None
        # ...
    }

    result = OpenUrl('http://localhost:8000', action, args)

    # assert result
    assert True

def test_GetLocaltime():
    action = 'GetLocaltime'

    result = OpenUrl('http://localhost:8000', action, None)

    # assert result
    import time
    assert time.time() - result['result'] < 0.001

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

