"""
The utils for Client.

@author: FATESAIKOU
@date  : 03/24/2019
"""

def GetExperimentAgent(experiment_config, env_config):
    from .Sequential import SequentialAgent
    from .RealSequential import RealSequentialAgent
    from .Concurrent import ConcurrentAgent
    from .RealConcurrent import RealConcurrentAgent
    from .TrainSeq import TrainSeqAgent
    from .DummyTrain import DummyTrainAgent
    from .GenPiPower import GenPiPowerAgent
    from .GenWeights import GenWeightsAgent

    if experiment_config['experiment_name'] == 'sequential':
        return SequentialAgent(experiment_config, env_config)
    elif experiment_config['experiment_name'] == 'concurrent':
        return ConcurrentAgent(experiment_config, env_config)
    elif experiment_config['experiment_name'] == 'real_sequential':
        return RealSequentialAgent(experiment_config, env_config)
    elif experiment_config['experiment_name'] == 'real_concurrent':
        return RealConcurrentAgent(experiment_config, env_config)
    elif experiment_config['experiment_name'] == 'train_seq':
        return TrainSeqAgent(experiment_config, env_config)
    elif experiment_config['experiment_name'] == 'dummy_train':
        return DummyTrainAgent(experiment_config, env_config)
    elif experiment_config['experiment_name'] == 'gen_pi_power':
        return GenPiPowerAgent(experiment_config, env_config)
    elif experiment_config['experiment_name'] == 'gen_weights':
        return GenWeightsAgent(experiment_config, env_config)
    else:
        return None

import json
from urllib import request, parse
def SendRequest(target_url, action, args, timeout=150):
    request_url = "{}/?action={}&args={}".format(
        target_url, action, parse.quote(json.dumps(args)))

    result_raw = request.urlopen(request_url, timeout=timeout).read()

    return json.loads(result_raw.decode('utf-8'))

def CalculateTimeout(process_obj):
    return (process_obj['request_desc']['model_size'] / 20480) * 5

import subprocess
def CheckAndRestartBluetooth(d_node_info):
    if d_node_info['type'] == 'wifi':
        return None

    print("[Restart bt][{}][{}]".format(
        d_node_info['restart_addr'], d_node_info['addr']))

    command = "ssh {} 'sudo killall -9 obexpushd; \
            sudo obexpushd -B {} -o ~/testPY/IoTSFC/models -n \
            -t FTP >/dev/null 2>&1 &'".format(
                d_node_info['restart_addr'], d_node_info['addr']
            )

    p = subprocess.Popen(command, shell=True)

    time.sleep(1)

def DumpRWLogs(rw_logs, log_path):
    with open(log_path, 'w') as log:
        log.write(json.dumps(rw_logs, indent=4))

