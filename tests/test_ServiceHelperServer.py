"""
A tester program for ServiceHelperServer.py

@author: FATESAIKOU
@date  : 03/05/2019
"""

import json


def test_UpdateGlobalParameter():
    action = 'UpdateGlobalParameter'
    args = {
        'tolerance_sigma': 0.1,
        'debug': True
    }

    result = OpenUrl('http://localhost:8000', action, args)

    assert result['args'] == args

def test_GetSFC():
    action = 'GetSFC'
    args = {
        'request_desc': None
        # ...
    }

    result = OpenUrl('http://localhost:8000', action, args)

    # assert result
    assert True

def test_UpdateRL():
    action = 'UpdateRL'
    args = {
        # ...
    }

    result = OpenUrl('http://localhost:8000', action, args)

    # assert result
    assert True

def test_GetLocalTime():
    action = 'GetLocalTime'
    args = {
        # ...
    }

    result = OpenUrl('http://localhost:8000', action, args)

    # assert result
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

