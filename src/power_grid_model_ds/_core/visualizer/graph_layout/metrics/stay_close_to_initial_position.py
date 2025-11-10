import numpy as np


def calculate_mip(nodes, geo):
    X = np.hypot(nodes[:, 0] - geo[:, 0], nodes[:, 1] - geo[:, 1])
    return - float(np.round(np.min(X) / np.mean(X), decimals=3))
