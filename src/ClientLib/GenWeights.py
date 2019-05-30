"""
The basic agent for SFC experiment training.

@author: FATESAIKOU
@date  : 03/24/2019
"""

import json
import time
import sys
import random

from .Utils import SendRequest, DumpRWLogs

class GenWeightsAgent:
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
        this.env_load = loads_config
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
        # Get avaliable req number
        ava_seq_len = int(len(request_sequence) * int(this.exp_config.get('ava_seq_persent', 100)) / 100)

        # Get pipower log
        with open(this.exp_config['log_filepath'], 'r') as src:
            pipower_log = json.loads(src.read())

        # Generate sfc combinations
        sfc_descs = this.GetSFCs()

        # Generate rewards & update model
        for sfc_desc in sfc_descs:
            random.shuffle(request_sequence)
            for r in request_sequence[:ava_seq_len]:
                c_cost, d_cost = this.GetCosts(pipower_log, sfc_desc, r)

                reward = {
                    'request_desc': r,
                    'SFC_desc': sfc_desc,
                    'predict': 7,
                    'event_list': {
                        'Start': 0,
                        'GotReq_V': 0,
                        'Verified': 1,
                        'GotReq_C': 1,
                        'GotModel': 1 + d_cost,
                        'Computed': 1 + d_cost + c_cost,
                        'GotReturn_V': 1 + d_cost + c_cost
                    }
                }

                # Update RL
                update_ret = this.ToServiceHelper('UpdateRL',
                    {'RL_rewards': reward,  'debug': False})

        # Dump Weights
        this.ToServiceHelper('DrawOutTables', {
            'graph_config': {
                'base_title': 'weights',
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

    def GetSFCs(this):
        if this.exp_config['mode'] == 'C':
            return [{
                'token': '5c9597f3c8245907ea71a89d9d39d08e',
                'V_node': i,
                'C_node': i,
                'D_node': i
            } for i in range(len(this.vc_map))]
        elif this.exp_config['mode'] == 'D':
            return [{
                'token': '5c9597f3c8245907ea71a89d9d39d08e',
                'V_node': 0,
                'C_node': 0,
                'D_node': i
            } for i in range(len(this.t_map))]
        elif this.exp_config['mode'] == 'M':
            return [{
                'token': '5c9597f3c8245907ea71a89d9d39d08e',
                'V_node': i,
                'C_node': i,
                'D_node': i
            } for i in range(len(this.vc_map))]

    def GetCosts(this, pipower_log, sfc_desc, r):
        service_name = r['service_name']
        c_load = 100 - this.env_load[this.vc_map[sfc_desc['C_node']]]['C_AVA']
        d_load = int(this.env_load[this.t_map[sfc_desc['D_node']]['addr']]['D_Load'][:-1])

        c_costs = pipower_log['computing'][str(c_load)][service_name]
        d_costs = pipower_log['transmitting'][str(d_load)][service_name]

        c_cost = sum(c_costs) / len(c_costs)
        d_cost = sum(d_costs) / len(d_costs)

        return c_cost, d_cost

    """ Other Utils """
    def ToServiceHelper(this, action, args):
        return SendRequest(this.service_helper_url, action, args)
