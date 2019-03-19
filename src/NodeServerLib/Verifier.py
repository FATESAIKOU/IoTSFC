"""
The toolkits for node to do verify.

@author: FATESAIKOU
@date  : 03/18/2019
"""

from .Utils import GetTime, SendRequest

class Verifier:
    env_params = None

    @staticmethod
    def DoVerify(process_obj, debug):
        # Get timestamp (GotReq_V)
        process_obj['event_list']['GotReq_V'] = \
                GetTime(Verifier.env_params['service_helper_url'])

        # Do verify
        Verifier.Verify(process_obj['SFC_desc']['token'])

        # Get time stamp (Verified)
        process_obj['event_list']['Verified'] = \
                GetTime(Verifier.env_params['service_helper_url'])

        # Do OpenUrl
        if not debug:
            process_obj = Verifier.SendToComputer(process_obj)

        # Get time stamp (GotReturn_V)
        process_obj['event_list']['GotReturn_V'] = \
                GetTime(Verifier.env_params['service_helper_url'])

        # return result
        return {'process_obj': process_obj}

    @staticmethod
    def Verify(token):
        return token == '5c9597f3c8245907ea71a89d9d39d08e'

    @staticmethod
    def SendToComputer(process_obj):
        target_url = Verifier.env_params['VC_map'][
            process_obj['SFC_desc']['C_node']
        ]
        action = 'DoCompute'
        args = {'process_obj': process_obj, 'debug': False}

        return SendRequest(target_url, action, args)['process_obj']

