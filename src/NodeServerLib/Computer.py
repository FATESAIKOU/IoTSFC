"""
The toolkits for node to do predict.

@author: FATESAIKOU
@date  : 03/18/2019
"""

import numpy as np

import chainer
import chainer.functions as F
import chainer.links as L
from chainer import serializers

from .Utils import GetTime, SendRequest

class Computer:
    env_params = None

    @staticmethod
    def DoCompute(process_obj, debug):
        # Get timestamp (GotReq_C)
        process_obj['event_list']['GotReq_C'] = \
                GetTime(Computer.env_params['service_helper_url'])

        # Get model (wifi or bluetooth)
        service_name = 'MLP_4000'

        # Get timestamp (GotModel)
        process_obj['event_list']['GotModel'] = \
                GetTime(Computer.env_params['service_helper_url'])

        # Load model
        model = Computer.LoadModel(service_name)

        # Get data & Predict
        process_obj['predict'] = Computer.Predict(model)

        # Get timestamp (Computed)
        process_obj['event_list']['Computed'] = \
                GetTime(Computer.env_params['service_helper_url'])

        # return result
        return {'process_obj': process_obj}

    @staticmethod
    def LoadModel(service_name):
        unit_num = int(service_name[service_name.find('_') + 1:])
        model_path = '/home/fatesaikou/testPY/IoTSFC/models/{}.model'.format(service_name)

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
