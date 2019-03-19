"""
The toolkit for node to transmit models.

@author: FATESAIKOU
@date  : 03/18/2019
"""

class Transmitter:
    env_params = None

    @staticmethod
    def DoTransmit(model_name):
        return {'result': model_name}
