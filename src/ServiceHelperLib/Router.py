"""
The program for ServiceHelper to route the reuqest

@author: FATESAIKOU
@date  : 03/09/2019
"""

import json

from .RLAgent import RLAgent
from .Utils import GetLocaltime

class Router():
    @staticmethod
    def InitializeEnv():
        RLAgent.Setup()

    @staticmethod
    def Route(action, args):
        if action == 'GetLocaltime':
            return {'result': GetLocaltime()}
        else:
            return args

