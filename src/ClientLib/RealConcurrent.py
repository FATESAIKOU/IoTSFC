"""
The concurrent sender for SFC experiment

@author: FATESAIKOU
@date  : 04/14/2019
"""

import sys
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor

from .Utils import SendRequest, CalculateTimeout, DumpRWLogs

class RealConcurrentAgent:
    # Init class variable
    def __init__(this, exp_config, env_config):
        this.v_node_num = this.c_node_num = len(env_config['VC_map'])
        this.d_node_num = len(env_config['T_map'])

        this.vc_map = env_config['VC_map']
        this.t_map = env_config['T_map']
        this.service_helper_url = env_config['service_helper_url']

        this.exp_config = exp_config
        this.env_config = env_config

        this.req_logs = []

    # Main method for doing experiment
    def DoExperiment(this, service_config, loads_config, request_sequence, loop_num=1):
        this.InitEnv(service_config, loads_config)

        data = []
        for i in range(loop_num):
            data.extend( this.DoRequest(request_sequence.copy(), this.exp_config['paral_num'], i) )

            data = sorted(data, key=lambda l: l['event_list']['Start'])
            DumpRWLogs(data, "{}/{}_log.json".format(
                this.exp_config['reward_log_dir'], this.exp_config['tag']))

    """ Concurrent Experiment Utils """
    # Prepare enviroment with provided configs
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

        # init node server
        for addr in this.env_config['NodeServerList']:
            SendRequest(addr, 'InitEnv', {'init_obj': this.env_config})
            load = loads_config[addr]
            print("Limit {} {}".format(addr, load))
            SendRequest(addr, 'SetCLoad', {
                'load_config': {'available_c_resources': load['C_AVA']}})
            SendRequest(addr, 'SetDLoad', {
                'load_config': {
                    'network_load': load['D_Load'],
                    'load_address': load['D_Load_To']
                }})

    # Do request concurrently
    def DoRequest(this, request_sequence, paral_num, loop_cnt):
        # Init parallel sending environment
        p = ThreadPoolExecutor(max_workers=paral_num)
        req_list = request_sequence
        wait_list = []
        mutex = threading.Lock()

        # Send request
        token = [paral_num]
        ts = []
        data = []
        i = 0
        while len(req_list) > 0:
            token[0] -= 1
            req = req_list.pop()
            time.sleep(0.1)
            t = p.submit(this.PerformRequest, req, req_list, wait_list, i, loop_cnt, mutex)
            ts.append(t)
            while token[0] == 0:
                token[0] = paral_num
                data.extend([t.result() for t in ts])
                ts = []

            i += 1

        # Collect reward logs
        data = [d for d in data if d['predict'] != -1]

        return data

    # Clean up the environment
    def CleanUpEnv(this):
        for addr in this.env_config['NodeServerList']:
            SendRequest(addr, 'CleanUp', None)

    """ Other Utils """
    def PerformRequest(this, req, req_list, wait_list, round_cnt, loop_cnt, mutex):
        # Do request
        try:
            # get sfc
            sfc_desc = this.ToServiceHelper('GetSFC', {'request_desc': req, 'debug': False})['result']
            if -1 in sfc_desc.values():
                raise OSError("Resource is busy")

            print("[Round: {}-{}]: {}-{}-{} {}".format(loop_cnt, round_cnt,
                sfc_desc['V_node'], sfc_desc['C_node'], sfc_desc['D_node'], req['service_name'], indent=4), file=sys.stderr)

            # get start event time
            event_list = {'Start': this.ToServiceHelper('GetLocaltime', None)['result']}

            # send request
            process_obj = this.ToVNode(sfc_desc['V_node'], 'DoVerify', {
                'process_obj': {
                    'event_list': event_list,
                    'request_desc': req,
                    'SFC_desc': sfc_desc
                },
                'debug': False
            })['process_obj']

            # update for unlock
            update_ret = this.ToServiceHelper('UnlockSFC',
                {'SFC_desc': process_obj['SFC_desc'], 'debug': False})

            # raise exception while prediction is not correct
            if process_obj['predict'] == -1:
                raise RuntimeError("Bad prediction value")

            # if finished normally, merge wait_list and req_list
            mutex.acquire()
            req_list.extend(wait_list)
            wait_list.clear() # instead of wait_list = []
            mutex.release()
        except Exception as e:
            # if failed, push req into wait_list
            print("[Error] {}".format(e))
            wait_list.append(req)
            process_obj = {
                'predict': -1,
                'SFC_desc': sfc_desc
            }

        # return log
        return process_obj

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

    def ToDNode(this, d_node_id, action, args):
        return SendRequest(
            this.vc_map[d_node_id]['addr'],
            action,
            args
        )
