"""
The toolkit for node to transmit models.

@author: FATESAIKOU
@date  : 03/18/2019
"""

import base64

class Transmitter:
    env_params = None

    @staticmethod
    def DoTransmit(file_name):
        file_path = Transmitter.env_params['model_dir'] + '/' + file_name

        with open(file_path, 'rb') as src:
            file_encoded = base64.b64encode(src.read()).decode('utf-8')

        return {'result': file_encoded}
