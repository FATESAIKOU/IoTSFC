"""

@author: FATESAIKOU
@date  : 03/09/2019
"""

import numpy as np
import math

from pprint import pprint
from .Utils import Gaussian

class RLAgent():
    global V_Table, C_Table, D_Table
    global V_States, C_States, D_States
    global V_Locked, C_Locked, D_Locked
    global V_Threshold, C_Threshold, D_Threshold
    global V_State_Factor, C_State_Factor, D_State_Factor
    global V_Node_Num, C_Node_Num, D_Node_Num

    global State_Max, State_Step, State_Num

    global LoadFactor_Sigma

    @staticmethod
    def Setup():
        global V_Table, C_Table, D_Table
        global V_States, C_States, D_States
        global V_Locked, C_Locked, D_Locked

        V_Table = np.ones(shape=(State_Num, V_Node_Num))
        V_States = np.array(range(1, State_Max, State_Step))
        V_Locked = set()

        C_Table = np.ones(shape=(State_Num, C_Node_Num))
        C_States = np.array(range(1, State_Max, State_Step))
        C_Locked = set()

        D_Table = np.ones(shape=(State_Num, D_Node_Num))
        D_States = np.array(range(1, State_Max, State_Step))
        D_Locked = set()

    @staticmethod
    def UpdateGlobalParam(init_obj):
        global LoadFactor_Sigma
        LoadFactor_Sigma = init_obj['loadfactor_sigma']

        # Count env.json
        global V_Node_Num, C_Node_Num, D_Node_Num
        V_Node_Num = init_obj['v_node_num']
        C_Node_Num = init_obj['c_node_num']
        D_Node_Num = init_obj['d_node_num']

        global V_State_Factor, C_State_Factor, D_State_Factor
        V_State_Factor = init_obj['v_state_factor']
        C_State_Factor = init_obj['c_state_factor']
        D_State_Factor = init_obj['d_state_factor']

        global V_Threshold, C_Threshold, D_Threshold
        V_Threshold = init_obj['v_threshold']
        C_Threshold = init_obj['c_threshold']
        D_Threshold = init_obj['d_threshold']

        global State_Max, State_Step, State_Num
        State_Max = init_obj['state_max']
        State_Step = init_obj['state_step']
        State_Num = math.ceil((State_Max - 1) / State_Step)

        RLAgent.Setup()

        return {
            'loadfactor_sigma': LoadFactor_Sigma,
            'v_node_num': V_Node_Num,
            'c_node_num': C_Node_Num,
            'd_node_num': D_Node_Num,
            'v_state_factor': V_State_Factor,
            'c_state_factor': C_State_Factor,
            'd_state_factor': D_State_Factor,
            'v_threshold': V_Threshold,
            'c_threshold': C_Threshold,
            'd_threshold': D_Threshold,
            'state_max': State_Max,
            'state_step': State_Step
        }

    @staticmethod
    def GetSFC(request):
        v_state, v_sd, c_state, c_sd, d_state, d_sd = \
            RLAgent.CalculateStateAndSd(request)

        global V_Locked, C_Locked, D_Locked
        v_id = int(RLAgent.SelectNode(V_Table, V_States, V_Locked, V_Threshold, v_state, v_sd))
        c_id = int(RLAgent.SelectNode(C_Table, C_States, C_Locked, C_Threshold, c_state, c_sd))
        d_id = int(RLAgent.SelectNode(D_Table, D_States, D_Locked, D_Threshold, d_state, d_sd))

        if None in [v_id, c_id, d_id]:
            v_id = c_id = d_id = None
        else:
            V_Locked.add(v_id)
            C_Locked.add(c_id)
            D_Locked.add(d_id)

        SFC_desc = {
            'token': '5c9597f3c8245907ea71a89d9d39d08e',
            'V_node': v_id,
            'C_node': c_id,
            'D_node': d_id
        }

        return SFC_desc

    @staticmethod
    def UpdateRL(rewards):
        # TODO Unlock V, C, D table's row in SFC_desc (For concurrent support)
        v_update_value, c_update_value, d_update_value = \
            RLAgent.CalculateUpdateValue(rewards['request_desc'], rewards['event_list'])

        v_state, v_sd, c_state, c_sd, d_state, d_sd = \
            RLAgent.CalculateStateAndSd(rewards['request_desc'])

        global V_Table, V_Locked
        RLAgent.UpdateTable(V_Table, V_States, v_state, v_sd,
            v_update_value, rewards['SFC_desc']['V_node'])
        V_Locked.discard(rewards['SFC_desc']['V_node'])

        global C_Table, C_Locked
        RLAgent.UpdateTable(C_Table, C_States, c_state, c_sd,
            c_update_value, rewards['SFC_desc']['C_node'])
        C_Locked.discard(rewards['SFC_desc']['C_node'])

        global D_Table, D_Locked
        RLAgent.UpdateTable(D_Table, D_States, d_state, d_sd,
            d_update_value, rewards['SFC_desc']['D_node'])
        D_Locked.discard(rewards['SFC_desc']['D_node'])

        from pprint import pprint


        return {'Status': 'success'}

    """ Toolkits """
    @staticmethod
    def CalculateStateAndSd(request):
        v_state = request['std_verification_cost'] * V_State_Factor * request['loadfactor']
        v_sd    = v_state * LoadFactor_Sigma
        c_state = request['std_computing_cost'] * C_State_Factor * request['loadfactor']
        c_sd    = c_state * LoadFactor_Sigma
        d_state = request['model_size'] * D_State_Factor * request['loadfactor']
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

        v_update_value = request['std_verification_cost'] * V_State_Factor / v_cost
        c_update_value = request['std_computing_cost'] * C_State_Factor / c_cost
        d_update_value = request['model_size'] * D_State_Factor / d_cost

        return (v_update_value, c_update_value, d_update_value)

    @staticmethod
    def SelectNode(table, state_list, locked_list, threshold, state, sd):
        # Calculate weights
        weights, filtered_list = RLAgent.FilterWeights(
            Gaussian(np.array(state_list), state, sd),
            locked_list,
            threshold
        )

        # If no node available, return None.
        if weights.shape[0] < 1:
            return None

        # Calculate random number
        sum_raw = np.dot( weights/sum(weights), table )

        sum_weights = 10 / sum_raw
        sum_weights = sum_weights / sum(sum_weights)

        random_id = np.random.choice(sum_weights.shape[0], 1, p=sum_weights)[0]

        # Refine the random_id with filtered_list
        return RLAgent.RefineRandomID(random_id, filtered_list)

    @staticmethod
    def UpdateTable(table, state_list, state, sd, update_value, update_ind):
        weights = Gaussian(np.array(state_list), state, sd)

        table[:, update_ind] = table[:, update_ind] + \
                (np.abs(update_value - state_list) - table[:, update_ind]) * weights

    @staticmethod
    def FilterWeights(weights, locked_list, threshold):
        filtered_list = []
        filtered_weights = []

        for i in range(weights.shape[0]):
            if i in locked_list or weights[i] > threshold:
                filtered_list.append(i)
            else:
                filtered_weights.append(weights[i])

        return np.array(filtered_weights), filtered_list

    @staticmethod
    def RefineRandomID(random_id, filtered_list):
        real_id = random_id

        for i in sorted(filtered_list):
            if real_id >= i:
                real_id += 1
            else:
                break

        return real_id