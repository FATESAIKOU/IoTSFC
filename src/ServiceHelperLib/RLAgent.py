"""

@author: FATESAIKOU
@date  : 03/09/2019
"""

class RLAgent():
    V_table = None
    C_table = None
    D_table = None

    tolerance_sigma = 0

    def Setup():
        # init V, C, D_tables and tolerance_sigma
        pass

    def UpdateGlobalParam(self, init_obj):
        # update global parameter for RLAgent
        pass

    def GetSFC(self, request):
        # main logic for selecting SFC
        pass

    def Update(self, rewards):
        # update tables by rewards
        pass
