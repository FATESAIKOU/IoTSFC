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
    fig.suptitle(r'$g(x, \mu, \sigma) = e^{-\frac{(x - \mu)^2}{2\sigma^2}}$')

    ax = plt.subplot(111)
    ax.set_ylim([0, 1.1])
    ax.set_xlim([-7, 7])
    for i in param_set:
        xs = np.linspace(-7, 7, 6000)
        ys = np.exp(-np.power(xs - 0, 2.) / (2 * np.power(i, 2.)))
        l = "$\sigma={}$".format(i)
        ax.plot(xs, ys, label=l)

    ax.grid()
    ax.legend()
    ax.set_xlabel('$x$')
    ax.set_ylabel('$y$')

    plt.savefig(save_path)
    plt.close()

if __name__ == '__main__':
    save_path = sys.argv[1]
    param_set = [0.1, 0.7, 1.3, 2.0]

    GenReciprocalGraph(param_set, save_path)
