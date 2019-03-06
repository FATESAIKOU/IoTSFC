"""
The toolkit for initialize experiment background parameter.

@author: FATESAIKOU
@date  : 03/06/2019
"""

import json
import random
from scipy.stats import truncnorm

def LoadConfig(config_path):
    with open(config_path) as src:
        return json.loads(src.read())

def LoadNNLog(nnlog_path):
    with open(nnlog_path) as src:
        return json.loads(src.read())

def GenerateRequestSequence(config_data, nnlog_data):
    parallel_request_num = config_data['parallel_request_num']
    request_sequence = []

    for i in range(config_data['sequence_length']):
        service_name = random.choice(config_data['service_name_pool'])

        request = {
            'service_name': service_name,
            'request_ID': i,
            'tolerance': TruncatedNormal(
                config_data['tolerance_avg'],
                config_data['tolerance_sigma'],
                config_data['tolerance_min'],
                config_data['tolerance_max']
            ),
            'std_verification_cost': nnlog_data[service_name]['std_verification_cost'],
            'std_computing_cost': nnlog_data[service_name]['std_computing_cost'],
            'model_size': nnlog_data[service_name]['model_size']
        }

        request_sequence.append(request)

    return (parallel_request_num, request_sequence)

""" Toolkits """
def TruncatedNormal(mean, sigma, low, upp):
    return truncnorm(
        (low - mean) / sigma, (upp - mean) / sigma, loc=mean, scale=sigma).rvs()
