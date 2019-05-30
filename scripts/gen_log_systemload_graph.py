#!/usr/bin/env python3
import sys
import numpy as np
import matplotlib
matplotlib.rcParams['text.usetex'] = True
matplotlib.rcParams['text.latex.unicode'] = True
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def GenReciprocalGraph(param_set, save_path):
    plt.rcParams.update({'font.size': 20})

    fig = plt.figure(figsize=(12, 6), dpi=800)
    fig.suptitle(r'$y = \frac{log(x) + L}{L}$')

    ax = plt.subplot(111)
    ax.set_ylim([0, 3])
    ax.set_xlim([-0.1, 1.2])
    for i in param_set:
        xs = np.linspace(0.000001, 1.2, 6000)
        ys = (np.log(xs) + i) / i
        l = "$L={}$".format(i)
        ax.plot(xs, ys, label=l)

    ax.grid()
    ax.legend()
    ax.set_xlabel(r'$x$')
    ax.set_ylabel(r'$y$')

    plt.savefig(save_path)
    plt.close()

if __name__ == '__main__':
    save_path = sys.argv[1]
    param_set = [10, 5, 2.5, 1]

    GenReciprocalGraph(param_set, save_path)
