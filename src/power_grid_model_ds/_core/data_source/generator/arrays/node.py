# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Generator for NodeArray"""
import random

import numpy as np

from power_grid_model_ds._core.data_source.generator.arrays.base import BaseGenerator
from power_grid_model_ds._core.model.enums.nodes import NodeType


class NodeGenerator(BaseGenerator):
    """Generator for node elements in the grid"""


    def create_from_list(self, bus_list, id_mapping={}, voltage_level: int = 10_500):
        amount = len(bus_list)

        # Create the node array
        node_array = self.grid.node.__class__.zeros(amount)
        node_array.id = 1 + self.grid.max_id + np.arange(amount)
        node_array.u_rated = voltage_level
        node_array.node_type = NodeType.UNSPECIFIED.value

        # Add the coordinates to the node array
        np_lat = np.zeros(amount)
        np_lon = np.zeros(amount)
        for i in range(amount):
            np_lon[i] = bus_list[i]['geometry']['coordinates'][0]
            np_lat[i] = bus_list[i]['geometry']['coordinates'][1]
        node_array.latitude = np_lat
        node_array.longitude = np_lon
        node_array.fdg_lat = np_lat
        node_array.fdg_lon = np_lon
        node_array.sld_lat = np_lat
        node_array.sld_lon = np_lon

        # Store the mapping of the file id to the grid structure id
        for i in range(amount):
            id_mapping[bus_list[i]['properties']['id']] = node_array.id[i]

        load_low_array = self.grid.sym_load.__class__.zeros(amount)
        load_low_array.id = 1 + node_array.id.max() + np.arange(amount)
        load_low_array.node = node_array.id
        load_low_array.status = 1

        load_high_array = self.grid.sym_load.__class__.zeros(amount)
        load_high_array.id = 1 + load_low_array.id.max() + np.arange(amount)
        load_high_array.node = node_array.id
        load_high_array.status = 1

        load_low_array.p_specified = np.round(self.rng.normal(200_000, 150_000, amount))
        load_low_array.q_specified = np.round(self.rng.normal(20_000, 15_000, amount))
        load_high_array.p_specified = np.round(self.rng.normal(-100_000, 350_000, amount))
        load_high_array.q_specified = np.round(self.rng.normal(-5_000, 35_000, amount))

        return node_array, load_low_array, load_high_array, id_mapping

    # pylint: disable=arguments-differ
    def run(self, amount: int, voltage_level: int = 10_500):
        """Generate nodes in a grid with two possible load scenarios"""
        node_array = self.grid.node.__class__.zeros(amount)
        node_array.id = 1 + self.grid.max_id + np.arange(amount)
        node_array.u_rated = voltage_level

        load_low_array = self.grid.sym_load.__class__.zeros(amount)
        load_low_array.id = 1 + node_array.id.max() + np.arange(amount)
        load_low_array.node = node_array.id
        load_low_array.status = 1

        load_high_array = self.grid.sym_load.__class__.zeros(amount)
        load_high_array.id = 1 + load_low_array.id.max() + np.arange(amount)
        load_high_array.node = node_array.id
        load_high_array.status = 1

        # power consumption in Watt
        load_low_array.p_specified = np.round(self.rng.normal(200_000, 150_000, amount))
        load_low_array.q_specified = np.round(self.rng.normal(20_000, 15_000, amount))
        load_high_array.p_specified = np.round(self.rng.normal(-100_000, 350_000, amount))
        load_high_array.q_specified = np.round(self.rng.normal(-5_000, 35_000, amount))

        return node_array, load_low_array, load_high_array
