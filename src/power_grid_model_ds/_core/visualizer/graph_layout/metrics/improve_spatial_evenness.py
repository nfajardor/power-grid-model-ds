import numpy as np


def calculate_mev(nodes):
    m = int(len(nodes) / 10)
    D_v = []
    for i in range(len(nodes)):
        distances = np.hypot(nodes[i][0] - nodes[:, 0], nodes[i][1] - nodes[:, 1])
        distances[i] = np.inf
        D_v.extend(np.sort(distances)[:m])
    D_v = np.asarray(D_v)
    min_d = np.min(D_v)
    max_d = np.max(D_v)
    D_v_norm = (D_v - min_d) * (1 / (max_d - min_d))
    return - float(np.round(np.var(D_v_norm), 3))
