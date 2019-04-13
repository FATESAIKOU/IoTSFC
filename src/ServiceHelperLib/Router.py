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
    def Route(action, args):
        if action == 'UpdateGlobalParameter':
            result = RLAgent.UpdateGlobalParam(args['init_obj'])
            return {'result': result}
        elif action == 'GetSFC':
            result = RLAgent.GetSFC(args['request_desc'])
            return {'result': result}
        elif action == 'UpdateRL':
            result = RLAgent.UpdateRL(args['RL_rewards'])
            return result
        if action == 'DrawOutTables':
            result = RLAgent.DrawOutTables(args['graph_config'])
            return {'result': result}
        if action == 'DumpWeights':
            result = RLAgent.DumpWeights(args['dump_config'])
            return {'result': result}
        if action == 'LoadWeights':
            result = RLAgent.LoadWeights(args['load_config'])
            return {'result': result}
        if action == 'GetLocaltime':
            return {'result': GetLocaltime()}
        else:
            return None

