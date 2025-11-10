import numpy as np


def calculate_mrp(geo_paths, paths):
    Q = []
    for i in paths:
        p = paths[i]
        geo = geo_paths[i]
        from_geo = geo[0]
        to_geo = geo[-1]
        from_p = p[0]
        to_p = p[-1]
        th_geo = np.atan2(to_geo[1] - from_geo[1], to_geo[0] - from_geo[0])
        th_p = np.atan2(to_p[1] - from_p[1], to_p[0] - from_p[0])
        Q.append(np.abs(th_geo - th_p))

    return float(np.round(1 - np.mean(Q) / np.pi,3))