"""
The basic agent for SFC experiment training.

@author: FATESAIKOU
@date  : 03/24/2019
"""

import json
import time
import sys

from .Utils import SendRequest, CalculateTimeout

class GenPiPowerAgent:
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

    """ Train Sequence Utils """
    def InitEnv(this, service_config, loads_config):
        for addr in this.env_config['NodeServerList']:
            # Init Nodes env
            SendRequest(addr, 'InitEnv', {'init_obj': this.env_config})

    def DoRequest(this, request_sequence, loop_cnt):
        # Get sfc and loads
        sfc_desc = this.GetSFC()
        loads = this.GetLoads()

        total = len(loads) * len(request_sequence)
        i = 1
        for l in loads:
            # Set node load
            this.SetLoad(l, sfc_desc)

            for r in request_sequence:
                # Get start time
                event_list = {'Start': this.ToServiceHelper('GetLocaltime', None)['result']}

                # Do request
                print("[Round: {}-{}/{}][Mode: {}][{}]".format(loop_cnt, i, total, this.exp_config['mode'], r['service_name']))
                process_obj = this.ToVNode(sfc_desc['V_node'], 'DoVerify', {
                    'process_obj': {
                        'event_list': event_list,
                        'request_desc': r,
                        'SFC_desc': sfc_desc
                    },
                    'debug': False
                })['process_obj']

                # Write execution time log
                this.WriteToPiLog(process_obj, l)

                i += 1

    def CleanUpEnv(this):
        # Clean up Nodes env
        for addr in this.env_config['NodeServerList']:
            SendRequest(addr, 'CleanUp', None)

    def GetSFC(this):
        return {
            'token': '5c9597f3c8245907ea71a89d9d39d08e',
            'V_node': 0,
            'C_node': 0,
            'D_node': 0
        }

    def GetLoads(this):
        return [ l for l in range(
            this.exp_config['start_load'],
            this.exp_config['end_load'] + 1,
            this.exp_config['load_step']
        )]

    def SetLoad(this, l, sfc_desc):
        if this.exp_config['mode'] == 'C':
            addr = this.vc_map[sfc_desc['C_node']]
            SendRequest(addr, 'SetCLoad', {
                'load_config': {'available_c_resources': 100 - l}})

        elif this.exp_config['mode'] == 'D':
            addr = this.t_map[sfc_desc['D_node']]['addr']
            SendRequest(addr, 'SetDLoad', {
                'load_config': {
                    'network_load': "{}k".format(l),
                    'load_address': 'fatesaikou@192.168.1.9 -p2222'
                }})

    def WriteToPiLog(this, process_obj, load):
        # Try to open pi log
        pi_log = this.TryReadPiLog()

        # Get service name
        service_name = process_obj['request_desc']['service_name']

        # Get load key
        load_key = str(load)

        # Get logging target and value
        if this.exp_config['mode'] == 'C':
            cost = process_obj['event_list']['Computed'] - process_obj['event_list']['GotModel']
            log = pi_log['computing']
        elif this.exp_config['mode'] == 'D':
            cost = process_obj['event_list']['GotModel'] - process_obj['event_list']['GotReq_C']
            log = pi_log['transmitting']

        # Log value to target
        if load_key not in log.keys():
            log[load_key] = {'MLP_' + str(u): [] for u in range(100, 2001, 10)}

        log[load_key][service_name].append(cost)


        # Writeback log
        this.WritePiLog(pi_log)

    """ Other Utils """
    def TryReadPiLog(this):
        try:
            with open(this.exp_config['log_filepath'], 'r') as src:
                pi_log = json.loads(src.read())

            assert set(['computing', 'transmitting']) == pi_log.keys()
            return pi_log
        except:
            return {'computing': {}, 'transmitting': {}}

    def WritePiLog(this, pi_log):
        with open(this.exp_config['log_filepath'], 'w') as dst:
            dst.write(json.dumps(pi_log, indent=4))

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


