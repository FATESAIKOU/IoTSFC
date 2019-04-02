"""
The program for NodeServer to route the reuqest

@author: FATESAIKOU
@date  : 03/18/2019
"""

import json

from .Verifier import Verifier
from .Computer import Computer
from .Transmitter import Transmitter

class Router():
    @staticmethod
    def InitEnv(init_obj):
        Verifier.env_params = init_obj
        Computer.env_params = init_obj
        Transmitter.env_params = init_obj

    @staticmethod
    def Route(action, args):
        if action == 'DoVerify':
            result = Verifier.DoVerify(
                args['process_obj'], args.get('debug', False))

            return result
        elif action == 'DoCompute':
            result = Computer.DoCompute(
                args['process_obj'], args.get('debug', False))

            return result
        elif action == 'DoTransmit':
            result = Transmitter.DoTransmit(args['file_name'])
            return result

        elif action == 'SetCLoad':
            result = Computer.SetCLoad(args['load_config'])
            return result
        else:
            return None

