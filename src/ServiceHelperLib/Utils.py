"""

@author: FATESAIKOU
@date  : 03/09/2019
"""

import time

def GetLocaltime():
    return time.time()

import numpy as np
def Gaussian(x, mean, sd):
    return np.exp(-np.power(x - mean, 2.) / (2 * np.power(sd, 2.)))
