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

import math
def CalculateUpdateFactor(x, system_load):
    return min(max((math.log(x, 10) + system_load) / system_load, 0), 1)


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def Dump2DWeights(table, title, save_path, labels):
    plt.rcParams.update({'font.size': 10})
    linestyles = dict(enumerate([':', '--', '-']))
    fig = plt.figure(dpi=800)
    #fig.suptitle(title)

    ax = plt.subplot(111)
    ax.set_ylim([0, int(table.max()) * 1.1])
    for i in range(table.shape[1]):
        data = table[:, i]
        ax.plot(np.arange(data.shape[0]) * 10, data, label=labels[i], linestyle=linestyles.get(i, '-.'))
        ax.grid()
        ax.legend()

    ax.set_xlabel('complexity')
    ax.set_ylabel('unfitness')

    plt.savefig(save_path)
    plt.close()

def DumpWeights(table, save_path, tag):
    file_name = save_path + '-' + tag + '.weights'
    with open(file_name, 'wb') as dst:
        np.save(dst, table)

    return file_name

def LoadWeights(load_path, tag):
    file_name = load_path + '-' + tag + '.weights'
    with open(file_name, 'rb') as src:
        return np.load(src)

