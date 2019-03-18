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
    def Route(action, args):
        if action == 'DoVerify':
            result = Verifier.DoVerify(args['process_obj'])
            return result
        elif action == 'DoCompute':
            result = Computer.DoCompute(args['process_obj'])
            return result
        elif action == 'DoTransmit':
            result = Transmitter.DoTransmit(args['model_name'])
            return result
        else:
            return None

