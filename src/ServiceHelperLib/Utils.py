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
def Dump2DWeights(table, title, save_path):
    wifi = table[:,0]

    fig = plt.figure()
    fig.suptitle(title)

    ax = plt.subplot(211)
    ax.plot(np.arange(wifi.shape[0]), wifi)
    ax.set_ylim([0, 15000])
    ax.set_title(title + '-wifi')

    #bluetooth = table[:, 1]
    #bx = plt.subplot(212)
    #bx.plot(np.arange(bluetooth.shape[0]), bluetooth)
    #bx.set_ylim([0, 15000])
    #bx.set_title(title + '-bluetooth')

    plt.savefig(save_path)

from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
def DumpWeights(table, title, save_path):
    X, Y = np.meshgrid(np.arange(table.shape[1]), np.arange(table.shape[0]))

    fig = plt.figure()
    fig.suptitle(title)
    ax = fig.gca(projection='3d')

    surf = ax.plot_surface(X, Y, table, cmap=cm.coolwarm,
                            linewidth=0, antialiased=False)

    fig.colorbar(surf, shrink=0.5, aspect=5)

    plt.savefig(save_path)
