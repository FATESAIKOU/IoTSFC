#!/usr/bin/env python3

import sys
import json
import random
import numpy as np

import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pprint import pprint

""" Utils """
def TransformData(pipower_log):
    datas = [[] for _ in range(20)]
    for sn in pipower_log.keys():
        ind = int(sn[4:]) // 100

        if ind < 20:
            datas[ind].extend(pipower_log[sn])

    return datas

def GenPiPowerGraph(pipower_log, mode, target, graph_name):
    t_max = 6 if mode == 'c' else 12
    datas = TransformData(pipower_log[target])

    # Plt data
    seg_labels = ["{}-{}".format(1000 + 100 * i, 1000 + 100 * (i+1)) for i in range(10)]
    plt.close()
    plt.boxplot(
        datas[10:],
        vert=True,
        labels=seg_labels,
        patch_artist=True,
        showfliers=False
    )

    # Plt mean
    for i in range(10, 20):
        mean = round(sum(datas[i]) / max(len(datas[i]), 1), 2)
        std = round(statistics.stdev(datas[i]), 2)
        plt.text(i - 9, t_max * 0.95, mean, horizontalalignment='center', color='green')
        plt.text(i - 9, t_max * 0.88, std, horizontalalignment='center', color='brown')

    # Other setting
    plt.xticks(rotation=30)
    plt.title('{} Time Cost Destribution'.format('Computing' if mode == 'c' else 'Transmitting'))
    plt.xlabel('MLP hidden layer unit number')
    plt.ylabel('Time Cost (second)')
    plt.ylim(0, t_max)
    plt.grid()
    plt.tight_layout()

    plt.savefig(graph_name)

""" Complex Sequence """
def GenGraphs(pipower, graph_tag):
    GenPiPowerGraph(pipower['computing'], 'c', '0', "/home/fatesaikou/Downloads/tmp/{}_pipower_c0_segdist.png".format(graph_tag))
    GenPiPowerGraph(pipower['computing'], 'c', '30', "/home/fatesaikou/Downloads/tmp/{}_pipower_c30_segdist.png".format(graph_tag))
    GenPiPowerGraph(pipower['computing'], 'c', '60', "/home/fatesaikou/Downloads/tmp/{}_pipower_c60_segdist.png".format(graph_tag))
    GenPiPowerGraph(pipower['computing'], 'c', '90', "/home/fatesaikou/Downloads/tmp/{}_pipower_c90_segdist.png".format(graph_tag))

    GenPiPowerGraph(pipower['transmitting'], 'd', '0', "/home/fatesaikou/Downloads/tmp/{}_pipower_d0_segdist.png".format(graph_tag))
    GenPiPowerGraph(pipower['transmitting'], 'd', '3072', "/home/fatesaikou/Downloads/tmp/{}_pipower_d3072_segdist.png".format(graph_tag))
    GenPiPowerGraph(pipower['transmitting'], 'd', '5120', "/home/fatesaikou/Downloads/tmp/{}_pipower_d5120_segdist.png".format(graph_tag))
    GenPiPowerGraph(pipower['transmitting'], 'd', '6144', "/home/fatesaikou/Downloads/tmp/{}_pipower_d6144_segdist.png".format(graph_tag))

if __name__ == '__main__':
    pipower_path = sys.argv[1]
    graph_tag = sys.argv[2]

    # Load log
    with open(pipower_path, 'r') as src:
        pipower = json.loads(src.read())

    # Gen graph
    GenGraphs(pipower, graph_tag)
