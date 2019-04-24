#!/usr/bin/env python3

import sys
import json
import numpy as np

def FilterOutData(pipower_log):
    for mode in ['computing', 'transmitting']:
        for log in pipower_log[mode].values():
            for u in range(100, 2001, 10):
                data = log['MLP_' + str(u)]

                if len(data) < 1:
                    continue

                mean = np.mean(data)
                sd = np.std(data)

                log['MLP_' + str(u)] = [t for t in data if t > mean - 2*sd and t < mean + 2*sd]

    return pipower_log


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as src:
        pipower_log = json.loads(src.read())

    new_pipower_log = FilterOutData(pipower_log)

    with open(sys.argv[2], 'w') as dst:
        dst.write(json.dumps(new_pipower_log, indent=4))

