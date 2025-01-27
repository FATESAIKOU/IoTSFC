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
        'v_state_factor': 100,
        'c_state_factor': 100,
        'd_state_factor': 100,
        'v_update_width': 300,
        'c_update_width': 300,
        'd_update_width': 300,
        'v_systemload': 0.1,
        'c_systemload': 1,
        'd_systemload': 0.5,
        'prefer_v_cost': 0.01,
        'prefer_c_cost': 2.02,
        'prefer_d_cost': 1.0,
        'v_threshold': 1000.0,
        'c_threshold': 1000.0,
        'd_threshold': 1000.0,
        'state_max': 1001,
        'state_step': 100,
        'available_c_resources': 50,
        'network_load': '0k',
        'load_address': 'pi@192.168.0.4',
        'graph_tag': 'test'
    }

    assert result == answer

from ExperimentBackground import LoadNNLog
def test_LoadNNLog():
    nnlog_path = '../nnlogs/test_nnlog.json'
    result = LoadNNLog(nnlog_path)

    assert len(result.keys()) == 91

from ExperimentBackground import GenerateRequestSequence
def test_GenerateRequestSequence():
    config_data = LoadConfig('../configs/test_config.json')
    nnlog_data  = LoadNNLog('../nnlogs/test_nnlog.json')

    request_sequence = GenerateRequestSequence(config_data, nnlog_data)

    assert len(request_sequence) == config_data['sequence_length']
