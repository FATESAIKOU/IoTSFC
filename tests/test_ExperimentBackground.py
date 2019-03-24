"""
A tester program for ExperimentBackground.py

@author: FATESAIKOU
@date  : 03/05/2019
"""

import sys
from pprint import pprint

sys.path.insert(0, '../src')

from ExperimentBackground import LoadConfig
def test_LoadConfig():
    config = '../configs/test_config.json'
    result = LoadConfig(config)
    answer = {
        'sequence_length': 100,
        'units_min': 100,
        'units_max': 1000,
        'units_avg': 200,
        'units_sigma': 100,
        'units_step': 10,
        'loadfactor_min': 0.9,
        'loadfactor_max': 1.5,
        'loadfactor_avg': 1,
        'loadfactor_sigma': 0.5,
        'v_state_factor': 100,
        'c_state_factor': 100,
        'd_state_factor': 100,
        'v_threshold': 1000.0,
        'c_threshold': 1000.0,
        'd_threshold': 1000.0,
        'state_max': 1001,
        'state_step': 100
    }

    assert result == answer

from ExperimentBackground import LoadNNLog
def test_LoadNNLog():
    nnlog_path = '../nnlogs/test_nnlog.json'
    result = LoadNNLog(nnlog_path)

    assert len(result.keys()) == 92

from ExperimentBackground import GenerateRequestSequence
def test_GenerateRequestSequence():
    config_data = LoadConfig('../configs/test_config.json')
    nnlog_data  = LoadNNLog('../nnlogs/test_nnlog.json')

    request_sequence = GenerateRequestSequence(config_data, nnlog_data)

    with open('wtf.json', 'w') as dest:
        import json
        dest.write(json.dumps(request_sequence, indent=4))

    assert len(request_sequence) == config_data['sequence_length']
