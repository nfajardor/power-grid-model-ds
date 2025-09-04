# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Generator for SourceArray"""
import random

import numpy as np

from power_grid_model_ds._core.data_source.generator.arrays.base import BaseGenerator
from power_grid_model_ds._core.model.arrays import NodeArray, SourceArray
from power_grid_model_ds._core.model.enums.nodes import NodeType


class SourceGenerator(BaseGenerator):
    """Generator for source elements in the grid (substations)"""

    def run(self, amount: int,
            grid_center=None,
            grid_std=None) -> tuple[NodeArray, SourceArray]:
        """Generate nodes in a grid which are sources (substations)"""
        substation_node_array = self.grid.node.__class__.empty(amount)
        substation_node_array.id = 1 + self.grid.max_id + np.arange(amount)
        substation_node_array.u_rated = 10_500
        substation_node_array.node_type = NodeType.SUBSTATION_NODE.value
        if not (grid_center is None):
            np_lat = np.zeros(amount)
            np_lon = np.zeros(amount)
            for i in range(amount):
                np_lon[i] = round(random.normalvariate(mu=grid_center[0], sigma=grid_std[0]), 5)
                np_lat[i] = round(random.normalvariate(mu=grid_center[1], sigma=grid_std[1]), 5)
            substation_node_array.latitude = np_lat
            substation_node_array.longitude = np_lon
        source_array = self.grid.source.__class__.empty(amount)
        source_array.id = 1 + substation_node_array.id.max() + np.arange(amount)
        source_array.node = substation_node_array.id
        source_array.status = 1
        source_array.u_ref = 1

        return substation_node_array, source_array
