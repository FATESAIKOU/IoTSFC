"""
The experiment client.

@author: FATESAIKOU
@date: 03/24/2019
@argv[1]: experiment config path
@argv[2]: service config path
@argv[3]: nnlogs path
@argv[4]: env config path
@agrv[5]: env load path
@argv[6]: loop_num
"""

import sys

from ExperimentBackground import LoadConfig, LoadNNLog, GenerateRequestSequence
from ClientLib.Utils import GetExperimentAgent

from pprint import pprint

def main():
    # Load configs
    experiment_config = LoadConfig(sys.argv[1])
    service_config = LoadConfig(sys.argv[2])
    nnlogs = LoadNNLog(sys.argv[3])
    env_config = LoadConfig(sys.argv[4])
    env_loads = LoadConfig(sys.argv[5])
    loop_num = int(sys.argv[6])

    # Generate requests
    request_sequence = GenerateRequestSequence(service_config, nnlogs)

    # Get experiment agent
    exp_agent = GetExperimentAgent(experiment_config, env_config)

    # Do experiment
    exp_agent.DoExperiment(service_config, env_loads, request_sequence, loop_num)

    # Clean up env
    exp_agent.CleanUpEnv()

if __name__ == '__main__':
    main()
