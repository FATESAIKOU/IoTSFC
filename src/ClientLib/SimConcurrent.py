"""
The basic agent for SFC experiment.

@author: FATESAIKOU
@date  : 03/24/2019
"""

import json
import time
import sys
import random

from .Utils import SendRequest, DumpRWLogs

class SimConcurrentAgent:
    def __init__(this, experiment_config, env_config):
        this.v_node_num = this.c_node_num = len(env_config['VC_map'])
        this.d_node_num = len(env_config['T_map'])

        this.vc_map = env_config['VC_map']
        this.t_map = env_config['T_map']
        this.service_helper_url = env_config['service_helper_url']

        this.exp_config = experiment_config
        this.env_config = env_config

        this.req_logs = []

    def DoExperiment(this, service_config, loads_config, request_sequence, loop_num=1) :
        this.InitEnv(service_config, loads_config)

        for i in range(loop_num):
            this.DoRequest(request_sequence.copy(), i)

    def InitEnv(this, service_config, loads_config):
        this.env_load = loads_config

        # init service helper
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

        # load weights
        ret = this.ToServiceHelper('LoadWeights', {'load_config': {
            'dir': this.exp_config['weights_dir'],
            'tag': this.exp_config['tag']
        }})
        print(json.dumps(ret, indent=4), file=sys.stderr)

    def DoRequest(this, request_sequence, loop_cnt):
        # Get pipower log
        with open(this.exp_config['log_filepath'], 'r') as src:
            pipower_log = json.loads(src.read())

        # Shuffle the request sequence
        random.shuffle(request_sequence)

        i = 0
        while len(request_sequence) > 0:
            sfc_descs = []
            for _ in range(this.exp_config['paral_num']):
                if len(request_sequence) == 0:
                    break;

                r = request_sequence.pop(0)
                print("[Round: {}-{} {}]".format(loop_cnt, i, r['service_name']), file=sys.stderr)

                # Get sfc
                sfc_desc = this.ToServiceHelper('GetSFC', {'request_desc': r, 'debug': False})['result']
                # Break out loop while devices are busy
                if -1 in sfc_desc.values():
                    print("[Error] Start Busy! {}".format(r['service_name']))
                    request_sequence.insert(0, r)
                    break;

                # Log sfc_desc for unlock later
                sfc_descs.append(sfc_desc)

                # Get simulated costs
                c_cost, d_cost = this.GetCosts(pipower_log, sfc_desc, r)

                # Gen simulated process_obj
                process_obj = {
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

                # Log rewards
                this.req_logs.append(process_obj)

                i += 1

            # Unlock sfc
            for sfc_desc in sfc_descs:
                update_ret = this.ToServiceHelper('UnlockSFC',
                    {'SFC_desc': sfc_desc, 'debug': False})

        # Dump Rewards
        DumpRWLogs(this.req_logs, "{}/{}_log.json".format(
            this.exp_config['reward_log_dir'], this.exp_config['tag']))

    def CleanUpEnv(this):
        # Clean up Nodes env
        for addr in this.env_config['NodeServerList']:
            SendRequest(addr, 'CleanUp', None)

    def GetCosts(this, pipower_log, sfc_desc, r):
        service_name = r['service_name']
        c_load = 100 - this.env_load[this.vc_map[sfc_desc['C_node']]]['C_AVA']
        d_load = int(this.env_load[this.t_map[sfc_desc['D_node']]['addr']]['D_Load'][:-1])

        c_costs = pipower_log['computing'][str(c_load)][service_name]
        d_costs = pipower_log['transmitting'][str(d_load)][service_name]

        c_cost = sum(c_costs) / len(c_costs)
        d_cost = sum(d_costs) / len(d_costs)

        return c_cost, d_cost

    def ToServiceHelper(this, action, args):
        return SendRequest(this.service_helper_url, action, args)
