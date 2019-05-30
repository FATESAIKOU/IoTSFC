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
    fig.suptitle(r'$y = \frac{w}{x}$')

    ax = plt.subplot(111)
    ax.set_ylim([0, 10])
    ax.set_xlim([-1, 10])
    for i in param_set:
        xs = np.linspace(0.000001, 15, 6000)
        ys = i / (xs)
        l = "$w={}$".format(i)
        ax.plot(xs, ys, label=l)

    ax.grid()
    ax.legend()
    ax.set_xlabel('$x$')
    ax.set_ylabel('$y$')

    plt.savefig(save_path)
    plt.close()

if __name__ == '__main__':
    save_path = sys.argv[1]
    param_set = [1, 5, 10]

    GenReciprocalGraph(param_set, save_path)
