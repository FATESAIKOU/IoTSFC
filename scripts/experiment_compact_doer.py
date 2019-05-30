#!/usr/bin/env python3

import os
import json
import time
import numpy as np

def WriteConfig(data, path):
    with open(path, 'w') as dst:
        dst.write(json.dumps(data, indent=4))

def GenEnvConfig(c_env, d_env, tag):
    base_env = {
        "service_helper_url": "http://192.168.1.2:8000",
        "tangle_node": "http://testnet140.tangle.works:443",
        "model_dir": "../models",
        "NodeServerList": [],
        "VC_map": [],
        "T_map": []
    }

    for i in range(c_env['node_num']):
        base_env['NodeServerList'].append('C' + str(i))
        base_env['VC_map'].append('C' + str(i))

    for i in range(d_env['node_num']):
        base_env['NodeServerList'].append('D' + str(i))
        base_env['T_map'].append({
            'type': 'wifi',
            'addr': 'D' + str(i)
        })

    WriteConfig(base_env, '/home/fatesaikou/testPY/IoTSFC/envs/' + tag + '.json')

def GenEnvLoads(c_env, d_env, tag):
    base_loads = {}

    c_loads = gen_node_loads(c_env['node_num'], c_env['node_load'])
    for i in range(c_env['node_num']):
        base_loads['C' + str(i)] = {
            "C_AVA": 100 - c_loads[i] * 10,
            "D_Load": "0k",
            "D_Load_To": "hedy@192.168.1.2 -p55555"
        }

    d_loads = gen_node_loads(d_env['node_num'], d_env['node_load'])
    for i in range(d_env['node_num']):
        base_loads['D' + str(i)] = {
            "C_AVA": 100,
            "D_Load": str(d_loads[i] * 1024) + 'k',
            "D_Load_To": "hedy@192.168.1.2 -p55555"
        }

    WriteConfig(base_loads, '/home/fatesaikou/testPY/IoTSFC/loads/' + tag + '.json')

def gen_node_loads(node_num, load_dist):
    load_acc = np.array([sum(load_dist[:i+1]) for i in range(len(load_dist))])
    load_acc = (load_acc / sum(load_dist)) * node_num

    now = 0
    loads = []
    while now < len(load_acc):
        if len(loads) + 1 > load_acc[now]:
            now += 1
        else:
            loads.append(now)

    return loads

def GenWeightExpConfig(req_info):
    weight_exp_config = {
        "experiment_name": "gen_weights",
        "weights_dir": "/home/fatesaikou/testPY/IoTSFC/weights",
        "tag": req_info['rw_log_tag'],
        "mode": req_info['mode'],
        "log_filepath": "/home/fatesaikou/testPY/IoTSFC/pipower_logs/pipower_cm.json",
        "ava_seq_persent": req_info['ava_seq_persent']
    }

    WriteConfig(weight_exp_config, '/home/fatesaikou/testPY/IoTSFC/experiment_configs/' + req_info['rw_log_tag'] + '_gw.json')

def GenServiceConfig(c_env, d_env, tag):
    base_config = {
        "sequence_length": 100,
        "units_min": 1000,
        "units_max": 2000,
        "units_avg": 500,
        "units_sigma": 1500,
        "units_step": 10,
        "v_state_factor": 1,
        "c_state_factor": 5000 * (c_env['prefer_cost'] / 0.5),
        "d_state_factor": 0.0012 * d_env['prefer_cost'],
        "prefer_v_cost": 0.01,
        "prefer_c_cost": c_env['prefer_cost'],
        "prefer_d_cost": d_env['prefer_cost'],
        "v_update_width": 300,
        "c_update_width": c_env['updatewidth'],
        "d_update_width": d_env['updatewidth'],
        "v_systemload": 0.1,
        "c_systemload": c_env['systemload'],
        "d_systemload": d_env['systemload'],
        "v_threshold": 10000000.0,
        "c_threshold": 10000000.0,
        "d_threshold": 10000000.0,
        "state_max": 25001,
        "state_step": 10,
        "graph_tag": "compact_test-sequential"
    }

    WriteConfig(base_config, '/home/fatesaikou/testPY/IoTSFC/configs/' + tag + '.json')

def RunExperiment(exp_name, tag):
    configs_base = "/home/fatesaikou/testPY/IoTSFC/"
    srv_c = configs_base + "configs/" + tag + ".json"
    nnlog_c = configs_base + "nnlogs/0_2000_nnlog.json"
    env_c = configs_base + "envs/" + tag + ".json"
    load_c = configs_base + "loads/" + tag + ".json"

    if exp_name == 'gen_weights':
        exp_c = configs_base + "experiment_configs/" + tag + "_gw.json"
        loop_time = 1
    else:
        exp_c = configs_base + "experiment_configs/" + tag + ".json"
        loop_time = 10

    exe_str = "python3 -u /home/fatesaikou/testPY/IoTSFC/src/Client_seq.py {} {} {} {} {} {}". format(exp_c, srv_c, nnlog_c, env_c, load_c, loop_time)

    os.system(exe_str)

def GenDoExpConfig(req_info):
    base_exp_config = {
        "experiment_name": "",
        "reward_log_dir": "/home/fatesaikou/testPY/IoTSFC/rw_logs",
        "weights_dir": "/home/fatesaikou/testPY/IoTSFC/weights",
        "tag": req_info['rw_log_tag'],
        "log_filepath": "/home/fatesaikou/testPY/IoTSFC/pipower_logs/pipower_cm.json"
    }

    if req_info['concurrent_num'] == 1:
        base_exp_config['experiment_name'] = 'sim_sequential'
    else:
        base_exp_config['experiment_name'] = 'sim_concurrent'
        base_exp_config['paral_num'] = req_info['concurrent_num']

    WriteConfig(base_exp_config, '/home/fatesaikou/testPY/IoTSFC/experiment_configs/' + req_info['rw_log_tag'] + '.json')

def DoExperiment(c_env, d_env, req_info):
    # Gen env_config (c_env, d_env)
    GenEnvConfig(c_env, d_env, req_info['rw_log_tag'])

    # Gen env_loads (c_env, d_env)
    GenEnvLoads(c_env, d_env, req_info['rw_log_tag'])

    # Gen gen_weight_experiment_config
    GenWeightExpConfig(req_info)

    # Gen service_config (c_env, d_env)
    GenServiceConfig(c_env, d_env, req_info['rw_log_tag'])

    # Call weights generator
    RunExperiment('gen_weights', req_info['rw_log_tag'])

    # Gen do_experiment_config
    GenDoExpConfig(req_info)

    # Call experiment doer
    # (Client or Client_seq with env_config, env_load and service_config)
    RunExperiment('real_exp', req_info['rw_log_tag'])

    # Remove all of the internal files
    os.system("cd /home/fatesaikou/testPY/IoTSFC; find -name {}* -not -path './rw_logs/*' -delete".format(req_info['rw_log_tag']))

"""
config
- mode [C, D, M]
- tag_base
- node_num_min
- node_num_max
- node_num_step
- concurrent true or false
- c_prefer_cost
- c_systemload
- d_prefer_cost
- d_systemload
"""
def DoGridExperiment(config):
    load_dists = [
        [1, 0, 0, 1, 0, 1],
        [1, 1, 1, 1, 1, 1]
        #[1, 1, 0, 0, 0, 0],
        #[0, 0, 1, 1, 0, 0],
        #[0, 0, 0, 0, 1, 1],
    ]

    for node_num in range(config['node_num_min'], config['node_num_max'] + 1, config['node_num_step']):
        for i in range(1, len(load_dists)):
            for concurrent_num in [1, 2, 4, 6]:
                c_env = {
                    'node_num': node_num,
                    'node_load': load_dists[i],
                    'prefer_cost': config['c_prefer_cost'],
                    'systemload': config['c_systemload'],
                    'updatewidth': config['c_updatewidth']
                }
                d_env = {
                    'node_num': node_num,
                    'node_load': load_dists[i],
                    'prefer_cost': config['d_prefer_cost'],
                    'systemload': config['d_systemload'],
                    'updatewidth': config['d_updatewidth']
                }
                req_info = {
                    'mode': config['mode'],
                    'rw_log_tag': "{}_{}_n{}_p{}_cl{}_{}{}{}_dl{}_{}{}{}_ava{}".format(
                        config['tag_base'],
                        config['mode'],
                        node_num, concurrent_num,
                        i,
                        str(int(config['c_prefer_cost'] * 10)).zfill(3),
                        str(int(config['c_systemload'] * 10)).zfill(3),
                        str(int(config['c_updatewidth'])).zfill(4),
                        i,
                        str(int(config['d_prefer_cost'] * 10)).zfill(3),
                        str(int(config['d_systemload'] * 10)).zfill(3),
                        str(int(config['d_updatewidth'])).zfill(4),
                        str(config['ava_seq_persent'])
                    ),
                    'concurrent_num': concurrent_num,
                    'ava_seq_persent': config['ava_seq_persent']
                }

                DoExperiment(c_env, d_env, req_info)

                if not config['concurrent']:
                    break

if __name__ == '__main__':
    #for uw in [165, 825, 1650]:
    for uw in [3300]:
        grid_config = {
            'mode': 'M',
            'tag_base': 'tg',
            'node_num_min': 6,
            'node_num_max': 6,
            'node_num_step': 1,
            'concurrent': False,
            'c_prefer_cost': 2.0,
            'c_systemload': 10.0,
            'c_updatewidth': uw,
            'd_prefer_cost': 4.0,
            'd_systemload': 10.0,
            'd_updatewidth': uw,
            'ava_seq_persent': 10,
        }
        DoGridExperiment(grid_config)
    print("End of test!")
