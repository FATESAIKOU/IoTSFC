"""
The basic agent for SFC experiment training.

@author: FATESAIKOU
@date  : 03/24/2019
"""

import json
import time
import sys

from .Utils import SendRequest, DumpRWLogs

class DummyTrainAgent:
    def __init__(this, experiment_config, env_config):
        this.v_node_num = this.c_node_num = len(env_config['VC_map'])
        this.d_node_num = len(env_config['T_map'])

        this.vc_map = env_config['VC_map']
        this.t_map = env_config['T_map']
        this.service_helper_url = env_config['service_helper_url']

        this.exp_config = experiment_config
        this.env_config = env_config

        this.req_logs = []

    def DoExperiment(this, service_config, loads_config, request_sequence, loop_num=1):
        this.InitEnv(service_config, loads_config)

        this.DoTrain(service_config, request_sequence)

    """ Train Sequence Utils """
    def InitEnv(this, service_config, loads_config):
        this.graph_tag = service_config['graph_tag']
        ret = this.ToServiceHelper('UpdateGlobalParameter', {
            'init_obj': {
                'v_node_num': this.v_node_num,
                'c_node_num': this.c_node_num,
                'd_node_num': this.d_node_num,
                'v_state_factor': service_config['v_state_factor'],
                'c_state_factor': service_config['c_state_factor'],
                'd_state_factor': service_config['d_state_factor'],
                'v_update_width': service_config['v_update_width'],
                'c_update_width': service_config['c_update_width'],
                'd_update_width': service_config['d_update_width'],
                'v_systemload': service_config['v_systemload'],
                'c_systemload': service_config['c_systemload'],
                'd_systemload': service_config['d_systemload'],
                'v_threshold': service_config['v_threshold'],
                'c_threshold': service_config['c_threshold'],
                'd_threshold': service_config['d_threshold'],
                'state_max': service_config['state_max'],
                'state_step': service_config['state_step']
            },
            'debug': False
        })
        print(json.dumps(ret, indent=4), file=sys.stderr)

    def DoTrain(this, service_config, request_sequence):
        # Get rewards
        with open(this.exp_config['log_filepath'], 'r') as src:
            rewards = json.loads(src.read())

        for r in rewards:
            # Update prefer costs
            r['request_desc']['prefer_verification_cost'] = service_config['prefer_v_cost']
            r['request_desc']['prefer_computing_cost'] = service_config['prefer_c_cost']
            r['request_desc']['prefer_data_cost'] = service_config['prefer_d_cost']

            # Update RL
            update_ret = this.ToServiceHelper('UpdateRL',
                {'RL_rewards': r,  'debug': False})

        # Dump Weights
        this.ToServiceHelper('DrawOutTables', {
            'graph_config': {
                'base_title': 'sequential',
                'base_path': '/home/fatesaikou/Downloads/tmp',
                'tag': this.graph_tag,
                'env_labels': {
                    'vc_list': this.vc_map,
                    't_list': [ t['addr'] for t in this.t_map ]
                }
            }
        })

        this.ToServiceHelper('DumpWeights', {'dump_config': {
            'dir': this.exp_config['weights_dir'],
            'tag': this.exp_config['tag']
        }})

    def CleanUpEnv(this):
        pass

    """ Other Utils """
    def ToServiceHelper(this, action, args):
        return SendRequest(this.service_helper_url, action, args)
