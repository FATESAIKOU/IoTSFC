#!/usr/bin/env python3

import sys
import json
import random
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from pprint import pprint

""" Utils """
def TransformData(rw_log):
    real_data = []
    for r in rw_log:
        real_data.append({
            'service_name': r['request_desc']['service_name'],
            'v_prefer_cost': r['request_desc']['prefer_verification_cost'],
            'c_prefer_cost': r['request_desc']['prefer_computing_cost'],
            'd_prefer_cost': r['request_desc']['prefer_data_cost'],
            'v_node': r['SFC_desc']['V_node'],
            'c_node': r['SFC_desc']['C_node'],
            'd_node': r['SFC_desc']['D_node'],
            'v_perf': r['SFC_desc']['V_perf'],
            'c_perf': r['SFC_desc']['C_perf'],
            'd_perf': r['SFC_desc']['D_perf'],
            'v_cost': r['event_list']['Verified'] - r['event_list']['GotReq_V'],
            'c_cost': r['event_list']['Computed'] - r['event_list']['GotModel'],
            'd_cost': r['event_list']['GotModel'] - r['event_list']['GotReq_C']
        })

    return real_data

def GenTimeDist(rw_log, mode, graph_name):
    data_key = "{}_cost".format(mode)
    node_key = "{}_node".format(mode)

    # Get datas
    datas = []
    for i in range(6):
        datas.append([
            [
                int(r['service_name'][4:]),
                r[data_key]
            ]
            for r in rw_log if r[node_key] == i])

    # Plt data
    plt.close()
    loads = ['Load: 0%', 'Load: 10%', 'Load: 20%', 'Load: 30%', 'Load: 40%', 'Load: 50%']
    for i in range(6):
        xs = [d[0] for d in datas[i]]
        ys = [d[1] for d in datas[i]]
        plt.plot(xs, ys, '.', label=loads[i], alpha=0.1)

    # Plt avg_cost and prefer_cost
    avg_cost = sum([r[data_key] for r in rw_log]) / len(rw_log)
    plt.hlines(avg_cost, xmin=1000, xmax=2000, colors='r', linestyles='solid', label='avg_cost({})'.format(round(avg_cost, 2)))

    prefer_cost_key = "{}_prefer_cost".format(mode)
    prefer_cost = sum([r[prefer_cost_key] for r in rw_log]) / len(rw_log)
    plt.hlines(prefer_cost, xmin=1000, xmax=2000, colors='c', linestyles='--', label='prefer_cost({})'.format(round(prefer_cost, 2)))

    # Other setting
    plt.title('Time Cost')
    plt.xlabel('MLP hidden layer unit number')
    plt.ylabel('time cost')
    plt.ylim(0, 6)
    plt.grid()
    plt.legend()

    plt.savefig(graph_name)

def GenTimesegCnt(rw_log, mode, graph_name):
    data_key = "{}_cost".format(mode)

    # Get datas
    datas = [[] for _ in range(20)]
    for r in rw_log:
        datas[int(r['service_name'][4:]) // 100].append(r[data_key])

    # Plt data
    seg_labels = ["{}-{}".format(1000 + 100 * i, 1000 + 100 * (i+1)) for i in range(10)]
    plt.close()
    plt.boxplot(
        datas[10:],
        vert=True,
        labels=seg_labels,
        patch_artist=True
    )

    # Plt mean
    for i in range(10, 20):
        mean = round(sum(datas[i]) / max(len(datas[i]), 1), 2)
        plt.text(i - 9, 5.7, mean, horizontalalignment='center', color='green')

    # Other setting
    plt.xticks(rotation=30)
    plt.title('Segmented Time Cost')
    plt.xlabel('MLP hidden layer unit number')
    plt.ylabel('time cost')
    plt.ylim(0, 6)
    plt.grid()
    plt.tight_layout()

    plt.savefig(graph_name)

def GenResourceDist(rw_log, mode, graph_name):
    data_key = "{}_perf".format(mode)
    node_key = "{}_node".format(mode)

    # Get datas
    datas = []
    for i in range(6):
        datas.append([
            [
                int(r['service_name'][4:]),
                r[data_key]
            ]
            for r in rw_log if r[node_key] == i])

    # Plt data
    plt.close()
    loads = ['Load: 0%', 'Load: 10%', 'Load: 20%', 'Load: 30%', 'Load: 40%', 'Load: 50%']
    for i in range(6):
        xs = [d[0] for d in datas[i]]
        ys = [d[1] for d in datas[i]]
        plt.plot(xs, ys, '.', label=loads[i], alpha=0.1)

    # Other setting
    plt.title('Resource Cost')
    plt.xlabel('MLP hidden layer unit number')
    plt.ylabel('resource cost')
    plt.grid()
    plt.legend()

    plt.savefig(graph_name)

def GenResourcesegCnt(rw_log, mode, graph_name):
    data_key = "{}_perf".format(mode)
    node_key = "{}_node".format(mode)

    # Get datas
    datas = [[ 0 for i in range(20) ] for _ in range(6)]
    for r in rw_log:
        datas[r[node_key]][int(r['service_name'][4:]) // 100] += 1

    # Plt data
    loads = ['Load: 0%', 'Load: 10%', 'Load: 20%', 'Load: 30%', 'Load: 40%', 'Load: 50%']
    plt.figure(figsize=(12, 5))
    width = 0.8 / 6
    ind = np.arange(10)
    for i in range(6):
        plt.bar(ind + width * (i+1) + (-6 * 0.5 * width), datas[i][10:], width, label=loads[i])

    unit_labels = ["{}-{}".format(1000 + 100 * i, 1000 + 100 * (i+1)) for i in range(10)]
    plt.xticks(ind + width / 2, unit_labels)

    plt.title('Resource Usage')
    plt.xlabel('MLP hidden layer unit number')
    plt.ylabel('resource cost')
    plt.grid()
    plt.legend()
    plt.savefig(graph_name)



""" Complex Sequence """
def GenTimeGraphs(rw_log, mode, graph_tag):
    # Gen dist graph
    GenTimeDist(rw_log, mode, "/home/fatesaikou/Downloads/tmp/{}_timedist.png".format(graph_tag))

    # Gen segmented box graph
    GenTimesegCnt(rw_log, mode, "/home/fatesaikou/Downloads/tmp/{}_timesegcnt.png".format(graph_tag))

def GenResourceGraphs(rw_log, mode, graph_tag):
    # Gen performance dist
    GenResourceDist(rw_log, mode, "/home/fatesaikou/Downloads/tmp/{}_resdist.png".format(graph_tag))

    # Gen resource cost cnt
    GenResourcesegCnt(rw_log, mode, "/home/fatesaikou/Downloads/tmp/{}_ressegdist.png".format(graph_tag))

def GenGraphs(rw_log, mode, graph_tag):
    # Gen time_cost graph
    GenTimeGraphs(rw_log, mode, graph_tag)

    # Gen resoucre_cost graph
    GenResourceGraphs(rw_log, mode, graph_tag)

if __name__ == '__main__':
    rw_log_path = sys.argv[1]
    mode = sys.argv[2]
    graph_tag = sys.argv[3]

    # Load log
    with open(rw_log_path, 'r') as src:
        rw_log = TransformData(json.loads(src.read()))

    # Gen graph
    GenGraphs(rw_log, mode, graph_tag)
