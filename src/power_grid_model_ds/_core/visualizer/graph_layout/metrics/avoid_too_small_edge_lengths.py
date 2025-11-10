import numpy as np

def calculate_mel(paths):
    L = []
    for i in paths:
        p = paths[i]
        cur_length = 0
        for i in range(1,len(p)):
            cur_length += np.hypot(p[i][0] - p[i-1][0], p[i][1] - p[i-1][1])
        L.append(cur_length)
    L = np.asarray(L)
    return float(np.round(np.min(L) / np.mean(L), decimals=3))