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
            'loadfactor_sigma': 0.1,
            'node_num': 3,
            'v_threshold': 10000,
            'c_threshold': 10000,
            'd_threshold': 10000
        },
        'debug': True
    }

    result = OpenUrl('http://localhost:8000', action, args)

    assert result['result'] == {'loadfactor_sigma': 0.1, 'node_num': 3,
                                'v_threshold': 10000, 'c_threshold': 10000,
                                'd_threshold': 10000}

def test_GetSFC():
    action = 'GetSFC'
    args = {
        'request_desc': {
            'service_name': 'WTF',
            'request_ID': 1,
            'loadfactor': 2,
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
        'RL_rewards': {
            'request_desc': {
                'service_name': 'WTF',
                'request_ID': 1,
                'loadfactor': 2,
                'std_verification_cost': 1,
                'std_computing_cost': 10,
                'model_size': 3
            },
            'SFC_desc': {
                'V_node': 1,
                'C_node': 2,
                'D_node': 0,
            },
            'event_list': {
                'Start': 1552376713.307387,
                'GotSFC': 1552376715.307387,
                'GotReq_V': 1552376717.307387,
                'Verified': 1552376719.307387,
                'GotReq_C': 1552376721.307387,
                'GotModel': 1552376723.307387,
                'Computed': 1552376725.307387,
                'GotReturn_V': 1552376727.307387,
                'GotReturn_Client':1552376729.307387
            }
        },
        'debug': True
    }

    result = OpenUrl('http://localhost:8000', action, args)

    # assert result
    assert True

def test_GetLocaltime():
    action = 'GetLocaltime'

    import time
    result = OpenUrl('http://localhost:8000', action, None)
    sample = time.time()

    # assert result
    assert sample - result['result'] < 0.001

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

