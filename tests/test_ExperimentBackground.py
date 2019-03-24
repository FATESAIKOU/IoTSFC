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
        'parallel_request_num': 10,
        'sequence_length': 100,
        'service_name_pool': [
            'MLP_600',
            'MLP_500',
            'MLP_400',
            'MLP_300',
            'MLP_200',
            'MLP_100'
        ],
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
    answer = {
        "std_verification_cost":  1,
        "MLP_600": {
            "std_computing_cost": 10,
            "model_size": 20
        },
        "MLP_500": {
            "std_computing_cost": 8.3,
            "model_size": 8.5
        },
        "MLP_400": {
            "std_computing_cost": 6.7,
            "model_size": 14
        },
        "MLP_300": {
            "std_computing_cost": 5,
            "model_size": 10
        },
        "MLP_200": {
            "std_computing_cost": 3.3,
            "model_size": 7
        },
        "MLP_100": {
            "std_computing_cost": 2,
            "model_size": 3
        }
    }

    assert result == answer

from ExperimentBackground import GenerateRequestSequence
def test_GenerateRequestSequence():
    config_data = LoadConfig('../configs/test_config.json')
    nnlog_data  = LoadNNLog('../nnlogs/test_nnlog.json')

    request_sequence = GenerateRequestSequence(config_data, nnlog_data)

    assert len(request_sequence) == config_data['sequence_length']
