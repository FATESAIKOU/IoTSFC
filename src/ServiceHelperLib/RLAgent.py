"""

@author: FATESAIKOU
@date  : 03/09/2019
"""

import numpy as np

from pprint import pprint

class RLAgent():
    global V_Table
    global C_Table
    global D_Table
    global V_States
    global C_States
    global D_States

    global Tolerance_Sigma
    global Node_Num

    @staticmethod
    def Setup():
        global V_Table
        global C_Table
        global D_Table
        global V_States
        global C_States
        global D_States

        V_Table = np.ones(shape=(10, Node_Num))
        V_States = range(1, 1001, 100)

        C_Table = np.ones(shape=(10, Node_Num))
        C_States = range(1, 1001, 100)

        D_Table = np.ones(shape=(10, Node_Num))
        D_States = range(1, 1001, 100)

    @staticmethod
    def UpdateGlobalParam(init_obj):
        global Tolerance_Sigma
        global Node_Num

        Tolerance_Sigma = init_obj['tolerance_sigma']
        Node_Num  = init_obj['node_num']

        RLAgent.Setup()

        return {
            'tolerance_sigma': Tolerance_Sigma,
            'node_num': Node_Num
        }

    @staticmethod
    def GetSFC(request):
        SFC_info = {
            'token': '5c9597f3c8245907ea71a89d9d39d08e',
            'V_node': -1,
            'C_node': -1,
            'D_node': -1
        }

        v_state, v_sd, \
        c_state, c_sd, \
        d_state, d_sd = RLAgent.CalculateStateAndSd(request)

        SFC_info['V_node'] = int(RLAgent.SelectNode(
                V_Table, V_States, v_state, v_sd))
        SFC_info['C_node'] = int(RLAgent.SelectNode(
                C_Table, C_States, c_state, c_sd))
        SFC_info['D_node'] = int(RLAgent.SelectNode(
                D_Table, D_States, d_state, d_sd))

        return SFC_info

    @staticmethod
    def UpdateRL(rewards):
        # update tables by rewards
        pass

    """ Toolkits """
    @staticmethod
    def CalculateStateAndSd(request):
        # TODO define V, C, D state coeificient
        v_state = request['std_verification_cost'] * 100 / request['tolerance']
        v_sd    = v_state * Tolerance_Sigma
        c_state = request['std_computing_cost'] * 100 / request['tolerance']
        c_sd    = c_state * Tolerance_Sigma
        d_state = request['model_size'] * 100 / request['tolerance']
        d_sd    = d_state * Tolerance_Sigma

        return [
            v_state, v_sd,
            c_state, c_sd,
            d_state, d_sd
        ]

    @staticmethod
    def SelectNode(table, state_list, state, sd):
        weights = RLAgent.Gaussian(np.array(state_list), state, sd)
        sum_raw = np.dot( weights/sum(weights), table )

        sum_weights = 1 / (sum_raw / 10)
        sum_weights = sum_weights / sum(sum_weights)

        return np.random.choice(Node_Num, 1, p=sum_weights)[0]


    """ Utils """
    @staticmethod
    def Gaussian(x, mean, sd):
        return np.exp(-np.power(x - mean, 2.) / (2 * np.power(sd, 2.)))
