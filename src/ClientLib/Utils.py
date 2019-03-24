"""
The utils for Client.

@author: FATESAIKOU
@date  : 03/24/2019
"""

from .Sequential import SequentialAgent
def GetExperimentAgent(experiment_config, env_config):
    if experiment_config['experiment_name'] == 'sequential':
        return SequentialAgent(experiment_config, env_config)
    else:
        return None

