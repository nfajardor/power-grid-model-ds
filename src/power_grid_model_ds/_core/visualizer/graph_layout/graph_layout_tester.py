
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.graph_layout.layout_algorithms import (fdg_birchfield_2018)
import power_grid_model_ds._core.visualizer.graph_layout.metrics as metrics
import numpy as np


class LayoutTester():
    def __init__(self, grid: Grid, paths):
        self.grid = grid
        self.paths = paths
        self.fdg_paths = {}
        self.sld_paths = {}
        for l in self.grid.line:
            cur_id = l.id[0]
            from_id = l.from_node
            to_id = l.to_node
            from_lat = self.grid.node['fdg_lat'][self.grid.node.id == from_id][0]
            from_lon = self.grid.node['fdg_lon'][self.grid.node.id == from_id][0]
            to_lat = self.grid.node['fdg_lat'][self.grid.node.id == to_id][0]
            to_lon = self.grid.node['fdg_lon'][self.grid.node.id == to_id][0]
            new_path = [
                [from_lat, from_lon],
                [to_lat, to_lon]
            ]
            self.fdg_paths[cur_id] = new_path
            self.sld_paths[cur_id] = new_path


    def add_fdg(self):
        lons = np.asarray(self.grid.node['longitude'])
        lats = np.asarray(self.grid.node['latitude'])
        node_array = np.column_stack((lons, lats))
        fdg = fdg_birchfield_2018.test_fdg_birchfield_2018(node_array)
        for i in range(len(self.grid.node)):
            self.grid.node['fdg_lon'][i] = fdg[i][0]
            self.grid.node['fdg_lat'][i] = fdg[i][1]
        for l in self.grid.line:
            cur_id = l.id
            from_id = l.from_node
            to_id = l.to_node
            from_lat = self.grid.node['fdg_lat'][self.grid.node.id == from_id][0]
            from_lon = self.grid.node['fdg_lon'][self.grid.node.id == from_id][0]
            to_lat = self.grid.node['fdg_lat'][self.grid.node.id == to_id][0]
            to_lon = self.grid.node['fdg_lon'][self.grid.node.id == to_id][0]
            new_path = []
            short_path = [
                [from_lat, from_lon],
                [to_lat, to_lon]
            ]
            for i in range(len(self.paths['fdg'][cur_id[0]])):
                t = i / (len(self.paths['fdg'][cur_id[0]]) - 1)
                new_lon = (1 - t) * from_lon + t * to_lon
                new_lat = (1 - t) * from_lat + t * to_lat
                new_path.append([new_lat, new_lon])
            self.paths['fdg'][cur_id[0]] = new_path
            self.fdg_paths[cur_id[0]] = short_path
        return self.grid, self.paths
    def add_sld(self):
        lons = np.asarray(self.grid.node['fdg_lon'])
        lats = np.asarray(self.grid.node['fdg_lat'])
        sld_lons = lons + 0.001 * lons
        sld_lats = lats + 0.001 * lats
        for i in range(len(self.grid.node)):
            self.grid.node['sld_lon'][i] = sld_lons[i]
            self.grid.node['sld_lat'][i] = sld_lats[i]
        sld_paths = {}
        for l in self.grid.line:
            cur_id = l.id
            from_id = l.from_node
            to_id = l.to_node
            from_lat = self.grid.node['sld_lat'][self.grid.node.id == from_id][0]
            from_lon = self.grid.node['sld_lon'][self.grid.node.id == from_id][0]
            to_lat = self.grid.node['sld_lat'][self.grid.node.id == to_id][0]
            to_lon = self.grid.node['sld_lon'][self.grid.node.id == to_id][0]
            new_path = []
            short_path = [
                [from_lat, from_lon],
                [to_lat, to_lon]
            ]
            for i in range(len(self.paths['sld'][cur_id[0]])):
                t = i / (len(self.paths['sld'][cur_id[0]]) - 1)
                new_lon = (1 - t) * from_lon + t * to_lon
                new_lat = (1 - t) * from_lat + t * to_lat
                new_path.append([new_lat, new_lon])
            self.paths['sld'][cur_id[0]] = new_path
            self.sld_paths[cur_id[0]] = short_path
        return self.grid, self.paths

    def evaluate_metrics(self):
        return metrics.calculate(self.grid, self.paths['geo'], self.fdg_paths, self.sld_paths)



    def grid_to_string(self):
        print(f"Nodes: {len(self.grid.node)}\nSources: {len(self.grid.source)}\nSym Load: {len(self.grid.sym_load)}\nLines: {len(self.grid.line)}")