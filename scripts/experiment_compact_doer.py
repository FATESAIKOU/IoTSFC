#!/usr/bin/env python3

import os
import json
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
        "log_filepath": "/home/fatesaikou/testPY/IoTSFC/pipower_logs/pipower.json"
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
        "c_state_factor": 8000 * c_env['prefer_cost'],
        "d_state_factor": 0.001 * d_env['prefer_cost'],
        "prefer_v_cost": 0.01,
        "prefer_c_cost": c_env['prefer_cost'],
        "prefer_d_cost": d_env['prefer_cost'],
        "v_update_width": 300,
        "c_update_width": 150,
        "d_update_width": 150,
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

    print(exe_str)
    os.system(exe_str)

def GenDoExpConfig(req_info):
    base_exp_config = {
        "experiment_name": "",
        "reward_log_dir": "/home/fatesaikou/testPY/IoTSFC/rw_logs",
        "weights_dir": "/home/fatesaikou/testPY/IoTSFC/weights",
        "tag": req_info['rw_log_tag'],
        "log_filepath": "/home/fatesaikou/testPY/IoTSFC/pipower_logs/pipower.json"
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

if __name__ == '__main__':
    DoExperiment(
        {
            'node_num': 3,
            'node_load': [1, 0, 1, 0, 0, 1],
            'prefer_cost': 2.0,
            'systemload': 1.0
        },
        {
            'node_num': 6,
            'node_load': [1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
            'prefer_cost': 4,
            'systemload': 6
        },
        {
            'mode': 'C',
            'rw_log_tag': 'test_compact',
            'concurrent_num': 1
        }
    )
    print("End of test!")
