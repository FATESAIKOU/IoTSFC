"""
The toolkits for node to do predict.

@author: FATESAIKOU
@date  : 03/18/2019
"""

from .Utils import GetTime, SendRequest

class Computer:
    env_params = None

    @staticmethod
    def DoCompute(process_obj, debug):
        # Get timestamp (GotReq_C)
        process_obj['event_list']['GotReq_C'] = \
                GetTime(Computer.env_params['service_helper_url'])

        # Get model (wifi or bluetooth)

        # Get timestamp (GotModel)
        process_obj['event_list']['GotModel'] = \
                GetTime(Computer.env_params['service_helper_url'])

        # Load model & data
        # Predict

        # Get timestamp (Computed)
        process_obj['event_list']['Computed'] = \
                GetTime(Computer.env_params['service_helper_url'])

        # return result
        return {'process_obj': process_obj}
