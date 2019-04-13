"""

@author: FATESAIKOU
@date  : 03/09/2019
"""

import numpy as np
import math

from pprint import pprint
from .Utils import Gaussian, Dump2DWeights, DumpWeights, LoadWeights, CalculateUpdateFactor

class RLAgent():
    global V_Table, C_Table, D_Table
    global V_States, C_States, D_States
    global V_Locked, C_Locked, D_Locked
    global V_Threshold, C_Threshold, D_Threshold
    global V_State_Factor, C_State_Factor, D_State_Factor
    global V_Node_Num, C_Node_Num, D_Node_Num
    global V_Update_Width, C_Update_Width, D_Update_Width
    global V_Systemload, C_Systemload, D_Systemload

    global State_Max, State_Step, State_Num

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
        # Count env.json
        global V_Node_Num, C_Node_Num, D_Node_Num
        V_Node_Num = init_obj['v_node_num']
        C_Node_Num = init_obj['c_node_num']
        D_Node_Num = init_obj['d_node_num']

        global V_State_Factor, C_State_Factor, D_State_Factor
        V_State_Factor = init_obj['v_state_factor']
        C_State_Factor = init_obj['c_state_factor']
        D_State_Factor = init_obj['d_state_factor']

        global V_Update_Width, C_Update_Width, D_Update_Width
        V_Update_Width = init_obj['v_update_width']
        C_Update_Width = init_obj['c_update_width']
        D_Update_Width = init_obj['d_update_width']

        global V_Systemload, C_Systemload, D_Systemload
        V_Systemload = init_obj['v_systemload']
        C_Systemload = init_obj['c_systemload']
        D_Systemload = init_obj['d_systemload']

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
            'v_node_num': V_Node_Num,
            'c_node_num': C_Node_Num,
            'd_node_num': D_Node_Num,
            'v_state_factor': V_State_Factor,
            'c_state_factor': C_State_Factor,
            'd_state_factor': D_State_Factor,
            'v_update_width': V_Update_Width,
            'c_update_width': C_Update_Width,
            'd_update_width': D_Update_Width,
            'v_systemload': V_Systemload,
            'c_systemload': C_Systemload,
            'd_systemload': D_Systemload,
            'v_threshold': V_Threshold,
            'c_threshold': C_Threshold,
            'd_threshold': D_Threshold,
            'state_max': State_Max,
            'state_step': State_Step
        }

    @staticmethod
    def GetSFC(request):
        v_state, c_state, d_state = RLAgent.CalculateState(request)

        global V_Locked, C_Locked, D_Locked
        v_id = int(RLAgent.SelectNode(V_Table, V_States, V_Locked, V_Threshold, v_state, V_Update_Width))
        c_id = int(RLAgent.SelectNode(C_Table, C_States, C_Locked, C_Threshold, c_state, C_Update_Width))
        d_id = int(RLAgent.SelectNode(D_Table, D_States, D_Locked, D_Threshold, d_state, D_Update_Width))

        if None in [v_id, c_id, d_id]:
            v_id = c_id = d_id = None
        else:
            V_Locked.add(v_id)
            C_Locked.add(c_id)
            D_Locked.add(d_id)
            print("[Lock][{}, {}, {}]".format(v_id, c_id, d_id))

        SFC_desc = {
            'token': '5c9597f3c8245907ea71a89d9d39d08e',
            'V_node': v_id,
            'C_node': c_id,
            'D_node': d_id
        }

        return SFC_desc

    @staticmethod
    def UpdateRL(rewards):
        global V_Locked, C_Locked, D_Locked
        V_Locked.discard(rewards['SFC_desc']['V_node'])
        C_Locked.discard(rewards['SFC_desc']['C_node'])
        D_Locked.discard(rewards['SFC_desc']['D_node'])


        if rewards['predict'] != -1:
            v_state, c_state, d_state = RLAgent.CalculateState(rewards['request_desc'])
            v_update_value, c_update_value, d_update_value = \
                RLAgent.CalculateUpdateValue(rewards['request_desc'], rewards['event_list'])

            global V_Table, C_Table, D_Table
            RLAgent.UpdateTable(V_Table, V_States, v_state, V_Update_Width,
                v_update_value, rewards['SFC_desc']['V_node'])
            RLAgent.UpdateTable(C_Table, C_States, c_state, C_Update_Width,
                c_update_value, rewards['SFC_desc']['C_node'])
            RLAgent.UpdateTable(D_Table, D_States, d_state, D_Update_Width,
                d_update_value, rewards['SFC_desc']['D_node'])
        else:
            v_update_value = c_update_value = d_update_value = -1
            v_state = c_state = d_state = -1

        return {'result':{
            'update_values': [v_update_value, c_update_value, d_update_value],
            'states': [v_state, c_state, d_state]
        }}

    @staticmethod
    def DrawOutTables(graph_config):
        base_title = graph_config['base_title']
        base_path = graph_config['base_path']
        env_labels = graph_config['env_labels']
        tag = graph_config.get('tag', None)

        Dump2DWeights(V_Table, 'V_Table-' + base_title, base_path + '/v_table-' + tag + '.png', env_labels['vc_list'])
        Dump2DWeights(C_Table, 'C_Table-' + base_title, base_path + '/c_table-' + tag + '.png', env_labels['vc_list'])
        Dump2DWeights(D_Table, 'D_Table-' + base_title, base_path + '/d_table-' + tag + '.png', env_labels['t_list'])

    @staticmethod
    def DumpWeights(dump_config):
        dir_base = dump_config['dir'] + '/' + dump_config['tag']
        return {
            'v_table': DumpWeights(V_Table, dir_base, 'v_table'),
            'v_states': DumpWeights(V_States, dir_base, 'v_states'),
            'c_table': DumpWeights(C_Table, dir_base, 'c_table'),
            'c_states': DumpWeights(C_States, dir_base, 'c_states'),
            'd_table': DumpWeights(D_Table, dir_base, 'd_table'),
            'd_states': DumpWeights(D_States, dir_base, 'd_states')
        }

    @staticmethod
    def LoadWeights(load_config):
        dir_base = load_config['dir'] + '/' + load_config['tag']

        global V_Table, C_Table, D_Table
        global V_States, C_States, D_States

        V_Table = LoadWeights(dir_base, 'v_table')
        V_States = LoadWeights(dir_base, 'v_states')
        C_Table = LoadWeights(dir_base, 'c_table')
        C_States = LoadWeights(dir_base, 'c_states')
        D_Table = LoadWeights(dir_base, 'd_table')
        D_States = LoadWeights(dir_base, 'd_states')

        return {
            'v_table': dir_base + '-v_table.weights',
            'v_states': dir_base + '-v_states.weights',
            'c_table': dir_base + '-c_table.weights',
            'c_states': dir_base + '-c_states.weights',
            'd_table': dir_base + '-d_table.weights',
            'd_states': dir_base + '-d_states.weights'
        }

    """ Toolkits """
    @staticmethod
    def CalculateState(request):
        # TODO set parameter interface for setting v, c, d sd value
        v_state = request['std_verification_cost'] * V_State_Factor / request['prefer_verification_cost']
        c_state = request['std_computing_cost'] * C_State_Factor / request['prefer_computing_cost']
        d_state = request['model_size'] * D_State_Factor / request['prefer_data_cost']

        print("[Model][State: {}, {}, {}]".format(v_state, c_state, d_state))

        return [ v_state, c_state, d_state ]

    @staticmethod
    def CalculateUpdateValue(request, event_list):
        v_cost = event_list['Verified'] - event_list['GotReq_V']
        c_cost = event_list['Computed'] - event_list['GotModel']
        d_cost = event_list['GotModel'] - event_list['GotReq_C']

        v_update_value = (request['std_verification_cost'] * V_State_Factor / v_cost) * \
                CalculateUpdateFactor(v_cost / request['prefer_verification_cost'], V_Systemload)
        c_update_value = (request['std_computing_cost'] * C_State_Factor / c_cost) * \
                CalculateUpdateFactor(c_cost / request['prefer_computing_cost'], C_Systemload)
        d_update_value = (request['model_size'] * D_State_Factor / d_cost) * \
                CalculateUpdateFactor(d_cost / request['prefer_data_cost'], D_Systemload)

        return (v_update_value, c_update_value, d_update_value)

    @staticmethod
    def SelectNode(table, state_list, locked_list, threshold, state, sd):
        # Calculate state weights
        weights = Gaussian(np.array(state_list), state, sd)

        # Calculate random number
        sum_raw = np.dot( weights/sum(weights), table )

        # Filter out sum_weights
        sum_weights, filtered_list = RLAgent.FilterWeights(
            sum_raw,
            locked_list,
            threshold
        )

        # If no node available, return None.
        if sum_weights.shape[0] < 1:
            return None

        sum_weights = 10000 / sum_raw
        sum_weights = sum_weights / sum(sum_weights)

        # Random choice
        random_id = np.random.choice(sum_weights.shape[0], 1, p=sum_weights)[0]

        # Refine the random_id with filtered_list
        return RLAgent.RefineRandomID(random_id, filtered_list)

    @staticmethod
    def UpdateTable(table, state_list, state, sd, update_value, update_ind):
        weights = Gaussian(np.array(state_list), state, sd)

        table[:, update_ind] = table[:, update_ind] + \
                (np.abs(update_value - state_list) - table[:, update_ind]) * weights

    @staticmethod
    def FilterWeights(sum_weights, locked_list, threshold):
        filtered_list = []
        filtered_sum_weights = []

        for i in range(sum_weights.shape[0]):
            if i in locked_list or sum_weights[i] > threshold:
                filtered_list.append(i)
            else:
                filtered_sum_weights.append(sum_weights[i])

        return np.array(filtered_sum_weights), filtered_list

    @staticmethod
    def RefineRandomID(random_id, filtered_list):
        real_id = random_id

        for i in sorted(filtered_list):
            if real_id >= i:
                real_id += 1
            else:
                break

        return real_id
