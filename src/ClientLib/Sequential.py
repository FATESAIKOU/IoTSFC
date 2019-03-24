"""
The basic agent for SFC experiment.

@author: FATESAIKOU
@date  : 03/24/2019
"""

import json

class SequentialAgent:
    def __init__(this, experiment_config, env_config):
        this.v_node_num = this.c_node_num = len(env_config['VC_map'])
        this.d_node_num = len(env_config['T_map'])

        this.vc_map = env_config['VC_map']
        this.service_helper_url = env_config['service_helper_url']

        this.exp_config = experiment_config

        this.req_logs = []

    def DoExperiment(this, service_config, request_sequence) :
        this.InitEnv(service_config)
        this.DoRequest(request_sequence)

    def InitEnv(this, service_config):
        ret = this.ToServiceHelper('UpdateGlobalParameter', {
            'init_obj': {
                'loadfactor_sigma': service_config['loadfactor_sigma'],
                'v_node_num': this.v_node_num,
                'c_node_num': this.c_node_num,
                'd_node_num': this.d_node_num,
                'v_state_factor': service_config['v_state_factor'],
                'c_state_factor': service_config['c_state_factor'],
                'd_state_factor': service_config['d_state_factor'],
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

    def DoRequest(this, request_sequence):
        for r in request_sequence:
            # Init process_obj
            sfc_desc = this.ToServiceHelper('GetSFC', {'request_desc': r, 'debug': False})['result']
            event_list = {'Start': this.ToServiceHelper('GetLocaltime', None)['result']}
            # Do request
            this.req_logs.append(this.ToVNode(sfc_desc['V_node'], {
                'process_obj': {
                    'event_list': event_list,
                    'request_desc': r,
                    'SFC_desc': sfc_desc
                },
                'debug': False
            })['process_obj'])

            # Update RL
            this.ToServiceHelper('UpdateRL',
                    {'RL_rewards': this.req_logs[-1], 'debug': False})

        this.req_logs = rewards

    def DumpLogs(this, log_path):
        with open(log_path, 'w') as log:
            log.write(json.dumps(this.req_logs, indent=4))

    def ToServiceHelper(this, action, args):
        return SendRequest(this.service_helper_url, action, args)

    def ToVNode(this, v_node_id, args) :
        return SendRequest(
            this.vc_map[v_node_id],
            'DoVerify',
            args
        )


""" Utils """
from urllib import request, parse
def SendRequest(target_url, action, args):
    request_url = "{}/?action={}&args={}".format(
        target_url, action, parse.quote(json.dumps(args)))

    result_raw = request.urlopen(request_url).read()

    return json.loads(result_raw.decode('utf-8'))
