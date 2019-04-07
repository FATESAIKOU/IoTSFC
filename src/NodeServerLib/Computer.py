"""
The toolkits for node to do predict.

@author: FATESAIKOU
@date  : 03/18/2019
"""

import os
import signal
import subprocess
import numpy as np

import chainer
import chainer.functions as F
import chainer.links as L
from chainer import serializers

from .Utils import GetTime, SendRequest, GetFile

class Computer:
    global Ava_C_Res
    Ava_C_Res = 100

    global X
    X = chainer.Variable(np.asarray([chainer.datasets.get_mnist()[1][0][0]]))

    env_params = None

    @staticmethod
    def CleanUp():
        pass

    @staticmethod
    def DoCompute(process_obj, debug):
        # Load Ava_C_Res
        c_limit_p = subprocess.Popen("cpulimit -z -l {} -p {}".format(
               Ava_C_Res, os.getpid()), shell=True, start_new_session=True)

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
            process_obj['predict'] = -1

        # Kill cpulimit process
        os.killpg(os.getpgid(c_limit_p.pid), signal.SIGTERM)

        # return result
        return {'process_obj': process_obj}

    @staticmethod
    def SetCLoad(load_config):
        global Ava_C_Res
        Ava_C_Res = load_config['available_c_resources']

        return {'load_config': {'available_c_resources': Ava_C_Res}}

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
