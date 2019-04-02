"""
The basic agent for SFC experiment.

@author: FATESAIKOU
@date  : 03/24/2019
"""

import json
import time
import sys

class SequentialAgent:
    def __init__(this, experiment_config, env_config):
        this.v_node_num = this.c_node_num = len(env_config['VC_map'])
        this.d_node_num = len(env_config['T_map'])

        this.vc_map = env_config['VC_map']
        this.t_map = env_config['T_map']
        this.service_helper_url = env_config['service_helper_url']

        this.exp_config = experiment_config

        this.req_logs = []

    def DoExperiment(this, service_config, request_sequence, loop_num=1) :
        this.InitEnv(service_config)

        for i in range(loop_num):
            this.DoRequest(request_sequence, i)

    def InitEnv(this, service_config):
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
        from pprint import pprint
        pprint(ret)

        # Init C loads
        for i in range(len(this.vc_map)):
            this.ToCNode(i, 'SetCLoad', {
                'load_config': {
                    'available_c_resources': service_config['available_c_resources']
                }})

    def DoRequest(this, request_sequence, loop_cnt):
        # Only for logging
        i = 0
        for r in request_sequence:
            # Init process_obj
            sfc_desc = this.ToServiceHelper('GetSFC', {'request_desc': r, 'debug': False})['result']
            event_list = {'Start': this.ToServiceHelper('GetLocaltime', None)['result']}
            # Do request
            try:
                this.req_logs.append(this.ToVNode(sfc_desc['V_node'], 'DoVerify', {
                    'process_obj': {
                        'event_list': event_list,
                        'request_desc': r,
                        'SFC_desc': sfc_desc
                    },
                    'debug': False
                })['process_obj'])
            except Exception as e:
                print("[Error!]: {}".format(e), file=sys.stderr)

            # Update RL
            update_ret = this.ToServiceHelper('UpdateRL',
                    {'RL_rewards': this.req_logs[-1], 'debug': False})

            # Only for logging
            i += 1
            log_str = '{' +'"service_name": {}, "C_Factor": 4000, "C_Cost": {}, "C_State": {}, "C_Value": {}'.format(
                r['service_name'],
                this.req_logs[-1]['event_list']['Computed'] - this.req_logs[-1]['event_list']['GotModel'],
                update_ret['result']['states'][1],
                update_ret['result']['update_values'][1]
            ) + '},'
            print(log_str)
            print("[Round: {}-{}] {}]".format(loop_cnt, i, log_str), file=sys.stderr)

            # Dump Weights
            this.ToServiceHelper('DrawOutTables', {
                'graph_config': {
                    'base_title': 'sequential',
                    'base_path': '/home/fatesaikou/Downloads/tmp',
                    'tag': 'sequential',
                    'env_labels': {
                        'vc_list': this.vc_map,
                        't_list': [ t['addr'] for t in this.t_map ]
                    }
                }
            })


    def DumpLogs(this, log_path):
        with open(log_path, 'w') as log:
            log.write(json.dumps(this.req_logs, indent=4))

    def ToServiceHelper(this, action, args):
        return SendRequest(this.service_helper_url, action, args)

    def ToVNode(this, v_node_id, action, args):
        return SendRequest(
            this.vc_map[v_node_id],
            action,
            args
        )

    def ToCNode(this, c_node_id, action, args):
        return SendRequest(
            this.vc_map[c_node_id],
            action,
            args
        )

    def ToDNode(this, d_node_id, action, agrs):
        return SendRequest(
            this.d_map[d_node_id],
            action,
            args
        )


""" Utils """
from urllib import request, parse
def SendRequest(target_url, action, args):
    request_url = "{}/?action={}&args={}".format(
        target_url, action, parse.quote(json.dumps(args)))

    result_raw = request.urlopen(request_url).read()

    return json.loads(result_raw.decode('utf-8'))
