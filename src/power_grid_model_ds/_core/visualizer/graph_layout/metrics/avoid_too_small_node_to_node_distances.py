import numpy as np


def calculate_mnd(nodes):
    D = np.zeros(len(nodes[:,0]))
    for i in range(len(nodes)):
        distances = np.hypot(nodes[i][0] - nodes[:, 0], nodes[i][1] - nodes[:,1])
        distances[i] = np.inf
        D[i] = np.min(distances)
    return float(np.round(np.min(D) / np.mean(D), decimals=3))
