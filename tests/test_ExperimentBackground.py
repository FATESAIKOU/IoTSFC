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
    config = '../config/test_config.json'
    result = LoadConfig(config)
    answer = {
        'parallel_request_num': 10,
        'sequence_length': 100,
        'service_name_pool': [
            'CNN_600x600',
            'CNN_500x500',
            'CNN_400x400',
            'CNN_300x300',
            'CNN_200x200',
            'CNN_100x100'
        ],
        'tolerance_min': 0.9,
        'tolerance_max': 1.5,
        'tolerance_avg': 1,
        'tolerance_sigma': 0.5
    }
    assert result == answer

from ExperimentBackground import LoadNNLog
def test_LoadNNLog():
    nnlog_path = '../nnlog/test_nnlog.json'
    result = LoadNNLog(nnlog_path)
    answer = {
        "CNN_600x600": {
            "std_verification_cost":  1,
            "std_computing_cost": 10,
            "model_size": 20
        },
        "CNN_500x500": {
            "std_verification_cost":  1,
            "std_computing_cost": 8.3,
            "model_size": 8.5
        },
        "CNN_400x400": {
            "std_verification_cost":  1,
            "std_computing_cost": 6.7,
            "model_size": 14
        },
        "CNN_300x300": {
            "std_verification_cost":  1,
            "std_computing_cost": 5,
            "model_size": 10
        },
        "CNN_200x200": {
            "std_verification_cost":  1,
            "std_computing_cost": 3.3,
            "model_size": 7
        },
        "CNN_100x100": {
            "std_verification_cost":  1,
            "std_computing_cost": 2,
            "model_size": 3
        }
    }

    assert result == answer

from ExperimentBackground import GenerateRequestSequence
def test_GenerateRequestSequence():
    config_data = LoadConfig('../config/test_config.json')
    nnlog_data  = LoadNNLog('../nnlog/test_nnlog.json')

    parallel_request_num, request_sequence = GenerateRequestSequence(config_data, nnlog_data)

    assert parallel_request_num == 10
    assert len(request_sequence) == config_data['sequence_length']
