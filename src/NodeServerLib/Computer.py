"""
The toolkits for node to do predict.

@author: FATESAIKOU
@date  : 03/18/2019
"""

import os
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
    env_params = None

    @staticmethod
    def DoCompute(process_obj, debug):
        # Load Ava_C_Res
        p = subprocess.Popen(["cpulimit", "-p", str(os.getpid()), "-l", str(Ava_C_Res)])

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

        # Kill cpulimit process
        p.terminate()

        # Env cleanup
        os.remove(model_path)

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
        train, test = chainer.datasets.get_mnist()
        x = chainer.Variable(np.asarray([test[0][0]]))

        y = model.predictor(x)

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
