"""
The toolkits for node to do predict.

@author: FATESAIKOU
@date  : 03/18/2019
"""

import os
import signal
import subprocess
import time
import numpy as np

import chainer
import chainer.functions as F
import chainer.links as L
from chainer import serializers

from .Utils import GetTime, SendRequest, GetFile

class Computer:
    global c_stress_p, c_limit_p
    c_limit_p = None
    c_stress_p = None

    global X
    X = chainer.Variable(np.asarray([chainer.datasets.get_mnist()[1][0][0]]))

    env_params = None

    @staticmethod
    def CleanUp():
        pass

    @staticmethod
    def DoCompute(process_obj, debug):
        try:
            # Get timestamp (GotReq_C)
            process_obj['event_list']['GotReq_C'] = \
                    GetTime(Computer.env_params['service_helper_url'])

            # Get model
            model_path = Computer.RequestModel(process_obj)

            # Get timestamp (GotModel)
            process_obj['event_list']['GotModel'] = \
                    GetTime(Computer.env_params['service_helper_url'])

            # Load model
            model = Computer.LoadModel(
                process_obj['request_desc']['service_name'],
                model_path
            )

            # Get data & Predict
            process_obj['predict'] = Computer.Predict(model)

            # Get timestamp (Computed)
            process_obj['event_list']['Computed'] = \
                    GetTime(Computer.env_params['service_helper_url'])

            # Env cleanup
            os.remove(model_path)
        except Exception as e:
            print("[Error][{}]".format(e))
            process_obj['predict'] = -1

        # return result
        return {'process_obj': process_obj}

    @staticmethod
    def SetCLoad(load_config):
        c_ava = load_config['available_c_resources']

        global c_stress_p, c_limit_p

        # control stress-ng process
        if c_ava == 100:
            if c_limit_p != None:
                os.killpg(os.getpgid(c_limit_p.pid), signal.SIGTERM)
                c_limit_p = None

            if c_stress_p != None:
                os.killpg(os.getpgid(c_stress_p.pid), signal.SIGTERM)
                c_stress_p = None
        else:
            if c_stress_p == None:
                c_stress_p = subprocess.Popen("stress-ng -c 1 --taskset 0",
                    shell=True, start_new_session=True)
                time.sleep(1)

            if c_limit_p != None:
                os.killpg(os.getpgid(c_limit_p.pid), signal.SIGTERM)

            c_limit_p = subprocess.Popen('cpulimit -z -l {} -p $( pidof -o {} stress-ng )'.format(
                100 - c_ava, c_stress_p.pid), shell=True, start_new_session=True)

        return {'load_config': {'available_c_resources': c_ava}}

    @staticmethod
    def RequestModel(process_obj):
        target_info = Computer.env_params['T_map'][
            process_obj['SFC_desc']['D_node']
        ]

        service_name = process_obj['request_desc']['service_name']
        model_path = GetFile(target_info, service_name + '.model')

        return model_path

    @staticmethod
    def LoadModel(service_name, model_path):
        unit_num = int(service_name[service_name.find('_') + 1:])

        model = L.Classifier(MLP(unit_num, 10))
        serializers.load_npz(model_path, model)

        return model

    @staticmethod
    def Predict(model):
        y = model.predictor(X)

        return int(F.argmax(y, axis=1)[0].data)

# Network definition
class MLP(chainer.Chain):
    def __init__(self, n_units, n_out):
        super(MLP, self).__init__()
        with self.init_scope():
            self.l1 = L.Linear(None, n_units)
            self.l2 = L.Linear(None, n_units)
            self.l3 = L.Linear(None, n_out)

    def forward(self, x):
        h1 = F.relu(self.l1(x))
        h2 = F.relu(self.l2(h1))
        return self.l3(h2)
