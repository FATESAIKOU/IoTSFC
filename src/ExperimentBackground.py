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
    request_sequence = []

    for i in range(config_data['sequence_length']):

        aim_units = int(TruncatedNormal(
            config_data['units_avg'],
            config_data['units_sigma'],
            config_data['units_min'],
            config_data['units_max']) // config_data['units_step'] * config_data['units_step'])
        service_name = 'MLP_' + str(aim_units)

        request = {
            'service_name':             service_name,
            'request_ID':               i,
            'std_verification_cost':    nnlog_data['std_verification_cost'],
            'prefer_verification_cost': config_data['prefer_v_cost'],
            'std_computing_cost':       nnlog_data[service_name]['std_computing_cost'],
            'prefer_computing_cost':    config_data['prefer_c_cost'],
            'model_size':               nnlog_data[service_name]['model_size'],
            'prefer_data_cost':         config_data['prefer_d_cost']
        }

        request_sequence.append(request)

    return request_sequence

def GenerateSequentialRequestSequence(config_data, nnlog_data):
    request_sequence = []
    i = 0

    for aim_units in range(config_data['units_min'], config_data['units_max'], config_data['units_step']):
        service_name = 'MLP_' + str(aim_units)

        request = {
            'service_name':             service_name,
            'request_ID':               i,
            'std_verification_cost':    nnlog_data['std_verification_cost'],
            'prefer_verification_cost': config_data['prefer_v_cost'],
            'std_computing_cost':       nnlog_data[service_name]['std_computing_cost'],
            'prefer_computing_cost':    config_data['prefer_c_cost'],
            'model_size':               nnlog_data[service_name]['model_size'],
            'prefer_data_cost':         config_data['prefer_d_cost']
        }

        request_sequence.append(request)
        i += 1

    return request_sequence

""" Toolkits """
def TruncatedNormal(mean, sigma, low, upp):
    return truncnorm(
        (low - mean) / sigma, (upp - mean) / sigma, loc=mean, scale=sigma).rvs()
