import numpy as np

def calculate_mor(paths):
    O = []
    for i in paths:
        p = paths[i]
        for i in range(1, len(p)):
            th_e = np.abs(np.atan2(p[i][1] - p[i-1][1], p[i][0] - p[i-1][0]))
            delta_e = min(th_e, np.abs(0.25 * np.pi - th_e), np.abs(0.5 * np.pi - th_e), np.pi - th_e) / (np.pi / 8)
            O.append(delta_e)
    return float(np.round(1 - np.mean(O), 3))

