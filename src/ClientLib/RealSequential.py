"""
The basic agent for SFC experiment.

@author: FATESAIKOU
@date  : 03/24/2019
"""

import json
import time
import sys

from .Utils import SendRequest, CalculateTimeout, CheckAndRestartBluetooth, DumpRWLogs

class RealSequentialAgent:
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
            this.DoRequest(request_sequence, i)

    def InitEnv(this, service_config, loads_config):
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

        for addr in this.env_config['NodeServerList']:
            # Init Nodes env
            SendRequest(addr, 'InitEnv', {'init_obj': this.env_config})

            # Init Loads
            load = loads_config[addr]
            print("Limit {} {}".format(addr, load))
            SendRequest(addr, 'SetCLoad', {
                'load_config': {'available_c_resources': load['C_AVA']}})
            SendRequest(addr, 'SetDLoad', {
                'load_config': {
                    'network_load': load['D_Load'],
                    'load_address': load['D_Load_To']
                }})

    def DoRequest(this, request_sequence, loop_cnt):
        i = 0
        for r in request_sequence:
            # Get sfc
            sfc_desc = this.ToServiceHelper('GetSFC', {'request_desc': r, 'debug': False})['result']

            # Do request
            print("[Round: {}-{}] {}]".format(loop_cnt, i, sfc_desc), file=sys.stderr)
            try:
                event_list = {'Start': this.ToServiceHelper('GetLocaltime', None)['result']}
                process_obj = this.ToVNode(sfc_desc['V_node'], 'DoVerify', {
                    'process_obj': {
                        'event_list': event_list,
                        'request_desc': r,
                        'SFC_desc': sfc_desc
                    },
                    'debug': False
                })['process_obj']
            except Exception as e:
                if 'time' in str(e):
                    CheckAndRestartBluetooth(this.env_config['T_map'][sfc_desc['D_node']])
                    time.sleep(1)

                print("[ErrorBreak {}]".format(e), file=sys.stderr)
                break

            # update for unlock
            update_ret = this.ToServiceHelper('UnlockSFC',
                {'SFC_desc': process_obj['SFC_desc'], 'debug': False})

            # Log rewards
            this.req_logs.append(process_obj)

            i += 1

        # Dump Rewards
        DumpRWLogs(this.req_logs, "{}/{}_log.json".format(
            this.exp_config['reward_log_dir'], this.exp_config['tag']))

    def CleanUpEnv(this):
        # Clean up Nodes env
        for addr in this.env_config['NodeServerList']:
            SendRequest(addr, 'CleanUp', None)

    def ToServiceHelper(this, action, args):
        return SendRequest(this.service_helper_url, action, args)

    def ToVNode(this, v_node_id, action, args):
        return SendRequest(
            this.vc_map[v_node_id],
            action,
            args,
            timeout=CalculateTimeout(args['process_obj'])
        )

    def ToCNode(this, c_node_id, action, args):
        return SendRequest(
            this.vc_map[c_node_id],
            action,
            args
        )

    def ToDNode(this, d_node_id, action, args):
        return SendRequest(
            this.t_map[d_node_id]['addr'],
            action,
            args
        )


