from ..util import to_lonlat, to_web_mercator
import numpy as np
from power_grid_model_ds._core.model.grids.base import Grid
import itertools
import random
def test_fdg_birchfield_2018(nodes, R=100, C1=1, C2=1, M=100,C3=0.1):


    return fdg_birchfield_2018(nodes, R, C1 * R, C2 * R, C3 * R, M)



def fdg_birchfield_2018(nodes, R, C1, C2, C3, M):
    nodes_mercator = to_web_mercator(nodes).astype(np.float64)
    X_0 = nodes_mercator[:, 0].astype(np.float64)
    Y_0 = nodes_mercator[:, 1].astype(np.float64)
    max_step = R / 5
    # Initialize nodes
    X = X_0.copy()
    Y = Y_0.copy()

    X_paths = []
    Y_paths = []
    plot_mercater = True
    if plot_mercater:
        X_paths.append(X.copy())
        Y_paths.append(Y.copy())
    else:
        X_paths.append(nodes[:, 0])
        Y_paths.append(nodes[:, 1])

    for m in range(M):
        # Hooke initial position
        F_X = C1 * (X_0 - X)
        F_Y = C1 * (Y_0 - Y)

        for i in range(len(X)):

            # Coulomb
            dX, dY = X - X[i], Y - Y[i]
            distances = np.maximum(np.hypot(dX, dY), 1e-6)
            ids_in_range = np.where((distances > 0) & (distances < (6 * R)))[0]
            for j in ids_in_range:
                if i != j:
                    F_mag = C2 / distances[j]
                    F_angle = np.atan2(Y[i] - Y[j], X[i] - X[j])
                    F_X[i] += F_mag * np.cos(F_angle)
                    F_Y[i] += F_mag * np.sin(F_angle)



        step_X = C3 * F_X
        step_Y = C2 * F_Y
        displacement_mags = np.minimum(np.hypot(step_Y, step_X), max_step)
        angles = np.arctan2(step_Y, step_X)
        step_X = displacement_mags * np.cos(angles)
        step_Y = displacement_mags * np.sin(angles)
        # Sum the forces
        X += step_X
        Y += step_Y

        deg_paths = np.column_stack((X, Y)) if plot_mercater else to_lonlat(np.column_stack((X, Y)))
        X_paths.append(deg_paths[:, 0])
        Y_paths.append(deg_paths[:, 1])

    fdg_mercator = np.column_stack((X, Y))
    return to_lonlat(fdg_mercator)