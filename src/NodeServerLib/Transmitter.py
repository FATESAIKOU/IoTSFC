"""
The toolkit for node to transmit models.

@author: FATESAIKOU
@date  : 03/18/2019
"""

import base64
import os, signal, subprocess

class Transmitter:
    global d_load_p
    d_load_p = None

    env_params = None

    @staticmethod
    def CleanUp():
        if d_load_p != None:
            os.killpg(os.getpgid(d_load_p.pid), signal.SIGTERM)

    @staticmethod
    def DoTransmit(file_name):
        file_path = Transmitter.env_params['model_dir'] + '/' + file_name

        with open(file_path, 'rb') as src:
            file_encoded = base64.b64encode(src.read()).decode('utf-8')

        return {'result': file_encoded}

    @staticmethod
    def SetDLoad(load_config):
        global d_load_p

        if d_load_p != None:
            os.killpg(os.getpgid(d_load_p.pid), signal.SIGTERM)
            d_load_p = None

        if load_config['network_load'] != '0k':
            command = "cat /dev/zero | pv -q -L {} | ssh {} 'cat >> /dev/null'".format(
                load_config['network_load'],
                load_config['load_address']
            )

            d_load_p = subprocess.Popen(command, shell=True, start_new_session=True)

        return {'load_config': load_config}
