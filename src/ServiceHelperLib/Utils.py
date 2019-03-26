"""
The utils for SeviceHelper.

@author: FATESAIKOU
@date  : 03/09/2019
"""

import time

def GetLocaltime():
    return time.time()

import numpy as np
def Gaussian(x, mean, sd):
    return np.exp(-np.power(x - mean, 2.) / (2 * np.power(sd, 2.)))


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def Dump2DWeights(table, title, save_path, labels):
    fig = plt.figure()
    fig.suptitle(title)

    ax = plt.subplot(111)
    for i in range(table.shape[1]):
        data = table[:, i]
        ax.plot(np.arange(data.shape[0]), data, label=labels[i])
        ax.set_ylim([0, 15000])
        ax.grid()
        ax.legend()

    plt.savefig(save_path)

