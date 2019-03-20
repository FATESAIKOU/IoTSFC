"""

@author: FATESAIKOU
@date  : 03/09/2019
"""

import numpy as np

from pprint import pprint
from .Utils import Gaussian

class RLAgent():
    global V_Table, C_Table, D_Table
    global V_States, C_States, D_States

    global LoadFactor_Sigma
    global Node_Num

    @staticmethod
    def Setup():
        global V_Table, C_Table, D_Table
        global V_States, C_States, D_States

        V_Table = np.ones(shape=(10, Node_Num))
        V_States = np.array(range(1, 1001, 100))

        C_Table = np.ones(shape=(10, Node_Num))
        C_States = np.array(range(1, 1001, 100))

        D_Table = np.ones(shape=(10, Node_Num))
        D_States = np.array(range(1, 1001, 100))

    @staticmethod
    def UpdateGlobalParam(init_obj):
        global LoadFactor_Sigma
        global Node_Num

        LoadFactor_Sigma = init_obj['loadfactor_sigma']
        Node_Num  = init_obj['node_num']

        RLAgent.Setup()

        return {
                'loadfactor_sigma': LoadFactor_Sigma,
            'node_num': Node_Num
        }

    @staticmethod
    def GetSFC(request):
        SFC_desc = {
            'token': '5c9597f3c8245907ea71a89d9d39d08e',
            'V_node': -1,
            'C_node': -1,
            'D_node': -1
        }

        v_state, v_sd, c_state, c_sd, d_state, d_sd = \
            RLAgent.CalculateStateAndSd(request)

        SFC_desc['V_node'] = int(RLAgent.SelectNode(
                V_Table, V_States, v_state, v_sd))
        SFC_desc['C_node'] = int(RLAgent.SelectNode(
                C_Table, C_States, c_state, c_sd))
        SFC_desc['D_node'] = int(RLAgent.SelectNode(
                D_Table, D_States, d_state, d_sd))
        # TODO Lock V, C, D table's row in SFC_desc (For concurrent support)

        return SFC_desc

    @staticmethod
    def UpdateRL(rewards):
        # TODO Unlock V, C, D table's row in SFC_desc (For concurrent support)
        v_update_value, c_update_value, d_update_value = \
            RLAgent.CalculateUpdateValue(rewards['request_desc'], rewards['event_list'])

        v_state, v_sd, c_state, c_sd, d_state, d_sd = \
            RLAgent.CalculateStateAndSd(rewards['request_desc'])


        global V_Table
        RLAgent.UpdateTable(V_Table, V_States, v_state, v_sd,
            v_update_value, rewards['SFC_desc']['V_node'])

        global C_Table
        RLAgent.UpdateTable(C_Table, C_States, c_state, c_sd,
            c_update_value, rewards['SFC_desc']['C_node'])

        global D_Table
        RLAgent.UpdateTable(D_Table, D_States, d_state, d_sd,
            d_update_value, rewards['SFC_desc']['D_node'])

        return {'Status': 'success'}

    """ Toolkits """
    @staticmethod
    def CalculateStateAndSd(request):
        # TODO define V, C, D state coeificient
        v_state = request['std_verification_cost'] * 100.0 * request['loadfactor']
        v_sd    = v_state * LoadFactor_Sigma
        c_state = request['std_computing_cost'] * 100.0 * request['loadfactor']
        c_sd    = c_state * LoadFactor_Sigma
        d_state = request['model_size'] * 100.0 * request['loadfactor']
        d_sd    = d_state * LoadFactor_Sigma

        return [
            v_state, v_sd,
            c_state, c_sd,
            d_state, d_sd
        ]

    @staticmethod
    def CalculateUpdateValue(request, event_list):
        v_cost = event_list['Verified'] - event_list['GotReq_V']
        c_cost = event_list['Computed'] - event_list['GotModel']
        d_cost = event_list['GotModel'] - event_list['GotReq_C']

        v_update_value = request['std_verification_cost'] * 100.0 / v_cost
        c_update_value = request['std_computing_cost'] * 100.0 / c_cost
        d_update_value = request['model_size'] * 100.0 / d_cost

        return (v_update_value, c_update_value, d_update_value)

    @staticmethod
    def SelectNode(table, state_list, state, sd):
        weights = Gaussian(np.array(state_list), state, sd)
        # TODO Filter out the locked rows (for concurrent support)

        sum_raw = np.dot( weights/sum(weights), table )

        sum_weights = 1 / (sum_raw / 10)
        sum_weights = sum_weights / sum(sum_weights)

        return np.random.choice(Node_Num, 1, p=sum_weights)[0]
        # TODO Recalculate the real id with lock_list (for concurrent support)

    @staticmethod
    def UpdateTable(table, state_list, state, sd, update_value, update_ind):
        weights = Gaussian(np.array(state_list), state, sd)

        table[:, update_ind] = table[:, update_ind] + \
                (np.abs(update_value - state_list) - table[:, update_ind]) * weights
