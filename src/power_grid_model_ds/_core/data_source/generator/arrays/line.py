# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Generator for LineArray"""

import numpy as np

from power_grid_model_ds._core import fancypy as fp
from power_grid_model_ds._core.data_source.generator.arrays.base import BaseGenerator
from power_grid_model_ds._core.model.arrays import LineArray, TransformerArray
from power_grid_model_ds._core.model.grids.base import Grid

AVERAGE_ROUTE_SIZE = 20


class LineGenerator(BaseGenerator):
    """Generator for line elements in the grid"""

    def __init__(self, grid: Grid, seed: int) -> None:
        super().__init__(grid=grid, seed=seed)
        self.connected_nodes: list = []
        self.unconnected_nodes: list = []
        self.line_array: LineArray = self.grid.line.__class__()
        self.trafo_array: TransformerArray = self.grid.transformer.__class__()

    # pylint: disable=arguments-differ
    def run(self, amount: int, number_of_routes: int | None = None) -> LineArray:
        """Generate routes, lines and normally open points (NOPs)"""

        self.trafo_array = self.grid.transformer
        if number_of_routes is None:
            number_of_routes = self.determine_number_of_routes()
        if number_of_routes > 0:
            self.create_routes(number_of_routes)
        else:
            self.line_array = self.grid.line

        # while not all connected, add lines from a connected node to an unconnected node
        self.set_unconnected_nodes()
        while any(self.unconnected_nodes):
            self.connect_nodes()
            self.set_unconnected_nodes()

        number_of_nops = amount
        if number_of_nops > 0:
            self.create_nop_lines(number_of_nops)

        return self.line_array

    def get_next_nodes(self, line, current_node):
        if current_node == line['properties']['start_node_id']:
            return line['properties']['end_node_id'], line['geometry']['coordinates']
        return line['properties']['start_node_id'], line['geometry']['coordinates'][::-1]


    def create_from_list(self, line_list, substations, id_mapping={}):
        line_array = self.grid.line.__class__()
        status = {}
        lines = {}
        next_nodes = []
        cur_line_id = self.grid.max_id + 1
        # print(f"Starting id = {cur_line_id} - {type(cur_line_id)}")
        paths = {}
        # print("Adding the substations")

        for s in substations:
            s_id = s['properties']['id']
            # print(f"Adding substation {s}")
            status[s_id] = True
            current_lines = [l for l in line_list if (l['properties']['start_node_id'] == s_id or l['properties']['end_node_id'] == s_id)]
            # print(f"Substation {s_id} has {len(current_lines)} lines")
            for l in current_lines:
                # print(f"Adding line:\n{l}\n____________")
                next_node, path = self.get_next_nodes(l, s_id)
                if next_node not in status:
                    # print(f"Line {l['properties']['id']} connects to a new node")
                    new_line = self.create_single_line(
                        from_node=id_mapping[s_id],
                        to_node=id_mapping[next_node],
                        feeder_node=id_mapping[s_id],
                        is_feeder=True,
                        line_id=cur_line_id,
                        feeder_branch=cur_line_id,
                        is_open=False,
                        # geometry=path
                        )
                    line_array = fp.concatenate(line_array, new_line)
                    status[next_node] = True
                    lines[(s_id, next_node)] = True
                    lines[(next_node, s_id)] = True
                    paths[cur_line_id] = path
                    next_nodes.append({"next": next_node, "feeder_node": id_mapping[s_id], "feeder_branch": cur_line_id})
                    cur_line_id += 1
                elif (s_id, next_node) not in lines:
                    # print(f"Line {l['properties']['id']} connects to an old node")
                    new_line = self.create_single_line(
                        from_node=id_mapping[s_id],
                        to_node=id_mapping[next_node],
                        feeder_node=id_mapping[s_id],
                        is_feeder=True,
                        line_id=cur_line_id,
                        feeder_branch=cur_line_id,
                        is_open=True,
                        # geometry=path
                    )
                    line_array = fp.concatenate(line_array, new_line)
                    lines[s, next_node] = True
                    lines[next_node, s] = True
                    paths[cur_line_id] = path
                    cur_line_id += 1
                # else:
                #     print(f"Line {l['properties']['id']} is an already existing path")
        # print("Starting with the edges")
        counter = 0
        while len(next_nodes) > 0:
            # if counter % (5 * int(len(line_list)/100)) == 0:
            #     print(f"{counter} - {int(100 * float(counter)/len(line_list))}% done")
            # counter += 1
            # print(f"evaluating the list now: {len(next_nodes)}")
            current_node = next_nodes.pop(0)
            # print(f"Current node: {current_node}")
            cur_id = current_node['next']
            cur_feeder_node = current_node['feeder_node']
            cur_feeder_line = current_node['feeder_branch']
            adjacent_lines = [l for l in line_list
                              if (l['properties']['start_node_id'] == cur_id or
                                  l['properties']['end_node_id'] == cur_id)]
            # print(f"{cur_id} has {len(adjacent_lines)} adjacent lines")
            for l in adjacent_lines:
                # print(f"Adding line:\n{l}\n____________")
                next_node, path = self.get_next_nodes(l, cur_id)
                if next_node not in status:
                    # print(f"Line {l['properties']['id']} connects to a new node")
                    new_line = self.create_single_line(
                        from_node=id_mapping[cur_id],
                        to_node=id_mapping[next_node],
                        feeder_node = cur_feeder_node,
                        is_feeder=False,
                        line_id=cur_line_id,
                        feeder_branch=cur_feeder_line,
                        is_open=False,
                        # geometry=path
                    )
                    line_array = fp.concatenate(line_array, new_line)
                    status[next_node] = True
                    lines[(cur_id, next_node)] = True
                    lines[(next_node, cur_id)] = True
                    paths[cur_line_id] = path
                    next_nodes.append({"next": next_node, "feeder_node": cur_feeder_node, "feeder_branch": cur_feeder_line})
                    cur_line_id += 1
                elif (cur_id, next_node) not in lines:
                    # print(f"Line {l['properties']['id']} connects to an old node")
                    new_line = self.create_single_line(
                        from_node=id_mapping[cur_id],
                        to_node=id_mapping[next_node],
                        feeder_node = cur_feeder_node,
                        is_feeder=False,
                        line_id=cur_line_id,
                        feeder_branch=cur_feeder_line,
                        is_open=True,
                        # geometry=path
                    )
                    line_array = fp.concatenate(line_array, new_line)
                    lines[cur_id, next_node] = True
                    lines[next_node, cur_id] = True
                    paths[cur_line_id] = path
                    cur_line_id += 1
                # else:
                #     print(f"Line {l['properties']['id']} connects to an already existing path")
        return line_array, paths, id_mapping

    def create_routes(self, number_of_routes: int):
        """Create a number of lines from the substation to unconnected nodes"""
        # each source should have at least one route
        number_of_sources = len(self.grid.source)
        from_nodes = self.rng.choice(self.grid.source.node, number_of_routes - number_of_sources, replace=True)
        not_source_mask = ~np.isin(self.grid.node.id, self.grid.source.node)
        to_nodes = self.rng.choice(self.grid.node.id[not_source_mask], number_of_routes, replace=False)
        capacities = 100 + self.rng.exponential(200, number_of_routes)
        line_array = self.grid.line.__class__.zeros(number_of_routes)
        line_array.id = 1 + self.grid.max_id + np.arange(number_of_routes)
        line_array.from_node = np.concatenate((self.grid.source.node, from_nodes))
        line_array.to_node = to_nodes
        line_array.from_status = [1] * number_of_routes
        line_array.to_status = [1] * number_of_routes
        line_array.r1 = self.rng.exponential(0.2, number_of_routes)
        line_array.x1 = self.rng.exponential(0.02, number_of_routes)
        line_array.i_n = capacities
        self.line_array = line_array

    def determine_number_of_routes(self) -> int:
        """Decide on a number of routes based on expected route-size"""
        expected_number_of_routes = int(np.ceil(len(self.grid.node) / AVERAGE_ROUTE_SIZE))
        number_of_sources = len(self.grid.source)
        # The number of routes is the max of the number of sources
        # and the expected number based on size
        return max(expected_number_of_routes, number_of_sources)

    def connect_nodes(self):
        """Add a new line between an active and inactive line"""
        to_node = self.rng.choice(self.unconnected_nodes)
        to_voltage = self.grid.node[self.grid.node.id == to_node].u_rated[0]
        same_voltage_mask = self.grid.node.u_rated == to_voltage
        same_voltage_nodes = self.grid.node[same_voltage_mask]
        options_mask = np.isin(self.connected_nodes, same_voltage_nodes.id)
        from_node = self.rng.choice(np.array(self.connected_nodes)[options_mask])
        capacity = 100 + self.rng.exponential(200, 1)
        new_line = self.grid.line.__class__.zeros(1)
        new_line.id = 1 + max(max(self.line_array.id), self.grid.max_id)  # pylint: disable=nested-min-max
        new_line.from_node = from_node
        new_line.to_node = to_node
        new_line.from_status = [1]
        new_line.to_status = [1]
        new_line.r1 = self.rng.exponential(0.2, 1)
        new_line.x1 = self.rng.exponential(0.02, 1)
        new_line.i_n = capacity
        self.line_array = fp.concatenate(self.line_array, new_line)

    def connect_geo_nodes(self, clusters) -> LineArray:
        lines = self.grid.line.__class__()
        cluster_origins = [c for c in clusters if c['level'] == 0]
        next_id = 1 + self.grid.max_id
        for c in cluster_origins:
            feeder_line = self.create_single_line(from_node=c['feeder_id'], to_node=c['id'], feeder_node=c['feeder_id'],is_feeder=True,line_id=next_id)
            c['feeder_branch'] = next_id
            lines = fp.concatenate(lines, feeder_line)
            next_id += 1

        next_nodes = []
        for c in cluster_origins:
            next_nodes.extend(c['children'])
            for cc in c['children']:
                clusters[cc]['feeder_branch'] = c['feeder_branch']
            while len(next_nodes) >0:
                current = next_nodes.pop(0)
                cur_cluster = clusters[current]
                for cc in cur_cluster['children']:
                    clusters[cc]['feeder_branch'] = cur_cluster['feeder_branch']
                next_nodes.extend(cur_cluster['children'])
                new_line = self.create_single_line(from_node=cur_cluster['parent'], to_node=cur_cluster['id'], feeder_node=cur_cluster['feeder_id'], is_feeder=False,line_id=next_id, feeder_branch=cur_cluster['feeder_branch'])
                lines = fp.concatenate(lines, new_line)
                next_id += 1
        self.line_array = lines

        
        self.set_unconnected_nodes()
        while any(self.unconnected_nodes):
            self.connect_nodes()
            self.set_unconnected_nodes()

        number_of_nops = 5
        if number_of_nops > 0:
            self.create_nop_lines(number_of_nops)
        return self.line_array, lines

    def create_single_line(self, from_node, to_node, feeder_node, is_feeder, line_id, feeder_branch=None, is_open=False, geometry=[]):
        line = self.grid.line.__class__.zeros(1)
        capacity = 100 + self.rng.exponential(200, 1)

        line.from_status = [1]
        line.to_status = [1]
        if is_open:
            line.to_status = [0]
        line.r1 = self.rng.exponential(0.2, 1)
        line.x1 = self.rng.exponential(0.02, 1)
        line.i_n = capacity
        line.from_node = from_node
        line.to_node = to_node
        line.id = line_id
        line.feeder_node_id = feeder_node
        line.is_feeder = is_feeder
        # line.geometry = geometry
        if feeder_branch is not None:
            line.feeder_branch_id = feeder_branch
        return line
    def create_nop_lines(self, number_of_nops: int):
        """Create the inactive lines between different routes (Normally Open Points)"""
        nops = [self.rng.choice(self.grid.node.id, 2, replace=False) for _ in range(number_of_nops)]
        from_nodes = [nop[0] for nop in nops]
        to_nodes = [nop[1] for nop in nops]
        capacities = 100 + self.rng.exponential(200, number_of_nops)
        nop_lines = self.grid.line.__class__.zeros(number_of_nops)
        nop_lines.id = 1 + self.line_array.id.max() + np.arange(number_of_nops)
        nop_lines.from_node = from_nodes
        nop_lines.to_node = to_nodes
        nop_lines.from_status = [1] * number_of_nops
        nop_lines.to_status = [0] * number_of_nops
        nop_lines.r1 = self.rng.exponential(0.2, number_of_nops)
        nop_lines.x1 = self.rng.exponential(0.02, number_of_nops)
        nop_lines.i_n = capacities
        self.line_array = fp.concatenate(self.line_array, nop_lines)

    def set_unconnected_nodes(self) -> None:
        """From a line array and total set of nodes determine which are not yet connected"""
        connected_link_mask = np.logical_or(
            np.isin(self.grid.node.id, self.line_array.from_node),
            np.isin(self.grid.node.id, self.line_array.to_node),
        )
        connected_trafo_mask = np.logical_or(
            np.isin(self.grid.node.id, self.trafo_array.from_node),
            np.isin(self.grid.node.id, self.trafo_array.to_node),
        )
        connected_mask = np.logical_or(
            connected_link_mask,
            connected_trafo_mask,
        )
        connected_nodes = self.grid.node.id[connected_mask]
        unconnected_nodes = self.grid.node.id[~connected_mask]

        self.unconnected_nodes = unconnected_nodes.tolist()
        self.connected_nodes = connected_nodes.tolist()
