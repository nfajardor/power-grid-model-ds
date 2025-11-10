# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Generators for the grid"""
import math
import random
from typing import Generic, Type, TypeVar

import numpy as np

from power_grid_model_ds._core.data_source.generator.arrays.line import LineGenerator
from power_grid_model_ds._core.data_source.generator.arrays.node import NodeGenerator
from power_grid_model_ds._core.data_source.generator.arrays.source import SourceGenerator
from power_grid_model_ds._core.data_source.generator.arrays.transformer import TransformerGenerator
from power_grid_model_ds._core.model.enums.nodes import NodeType
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel
from power_grid_model_ds._core.model.graphs.models.rustworkx import RustworkxGraphModel
from power_grid_model_ds._core.model.grids.base import Grid

import json
import time

# pylint: disable=too-few-public-methods,too-many-arguments,too-many-positional-arguments

T = TypeVar("T", bound=Grid)



class RadialGridGenerator(Generic[T]):
    """Generates a random but structurally correct radial grid with the given specifications"""



    def __init__(
            self,
            grid_class: Type[T],
            nr_nodes: int = 100,
            nr_sources: int = 2,
            nr_nops: int = 10,
            graph_model: type[BaseGraphModel] = RustworkxGraphModel,
    ):
        self.grid_class = grid_class
        self.graph_model = graph_model
        self.nr_nodes = nr_nodes
        self.nr_sources = nr_sources
        self.nr_nops = nr_nops

    def fdg_palcement_birchfield(
            self,
            edges,
            vertices
            ):
        fdg = []

        M = 10000
        R = 0.00002
        C1 = R
        C2 = R
        C3 = 0.1 * R
        # Initialize each node
        for v in vertices:
            fdg.append({'id': v['id'], 'lat': v['lat'], 'lon': v['lon'], 'fdg_lat': v['lat'], 'fdg_lon': v['lon']})

        for m in range(M):
            #hooke
            F_lat = {}
            F_lon = {}
            for v in fdg:
                F_lat[str(v['id'])] = C1 * (v['lat'] - v['fdg_lat'])
                F_lon[str(v['id'])] = C1 * (v['lon'] - v['fdg_lon'])
            for v1 in fdg:
                for v2 in fdg:
                    if v1['id'] != v2['id']:
                        denom = math.sqrt( math.pow(v1['lat'] - v2['lat'], 2) + math.pow(v1['lon'] - v2['lon'], 2) )
                        if denom == 0:
                            denom = R/1E-6
                        F_mag = C2 / denom
                        F_angle = math.atan2(v1['lat'] - v2['lat'], v1['lon'] - v2['lon'])
                        F_lat[str(v1['id'])] += F_mag * math.sin(F_angle)
                        F_lon[str(v1['id'])] += F_mag * math.cos(F_angle)

            if m % 5 == 0:
                print(f"m={m}")
                print(f"F_lat={F_lat[str(fdg[0]['id'])]}; F_lon={F_lon[str(fdg[0]['id'])]}")
                print(f"Before: {fdg[0]}")
                print(f"F_lat:{round(C3 * F_lat[str(fdg[0]['id'])], 5)}")
                print(f"F_lon:{round(C3 * F_lon[str(fdg[0]['id'])], 5)}")
            for v in range(len(fdg)):
                fdg[v]['fdg_lat'] += round(C3 * F_lat[str(fdg[v]['id'])], 5)
                fdg[v]['fdg_lon'] += round(C3 * F_lon[str(fdg[v]['id'])], 5)
            if m % 5 == 0:
                print(f"After: {fdg[0]}")

        print('FDG\n_________')
        for f in fdg:
            print(f)
        return fdg


    def log_timed_message(self, start_time, end_time, message, log_status=False):
        if log_status:
            print(f"{round((end_time-start_time) * 1000, 3)}ms - {message}")

    def log_list(self, list_to_log, name, log_status=True):
        if log_status:
            print(f"______________\n{name}:")
            for e in list_to_log:
                print(e)

    def log_dict(self, dict, name, log_status=True):
        if log_status:
            print("______________\n{name}:")
            for s in dict:
                print(f"{s} -> {dict[s]}")

    def send_grid_to_geosjon(self, grid, path, name):
        geojson = {}
        nodes = grid.node
        sources = grid.source
        load = grid.sym_load
        # self.log_list(nodes,"NODES", True)
        # self.log_list(sources, "SOURCES", True)
        # self.log_list(load,"LOAD", True)
        lines = grid.line
        geo_path = path['geo']
        fdg_path = path['fdg']
        sld_path = path['sld']
        # self.log_list(lines, "Lines", True)
        # self.log_dict(geo_path, "Path", True)
        geojson['type'] = 'FeatureCollection'
        geojson['features'] = []
        geojson['name'] = name

        node_start_parsing = time.perf_counter()
        # Parse the nodes
        # counter = 0
        # print('parsing the nodes')
        # for s in sources:
        #     n = nodes[nodes['id'] == s['node']]
        #     print(n)
        for n in nodes:
            # if counter % int(len(nodes) / 10) == 0:
            #     print(f"{counter} - {int((counter / len(nodes)) * 100)}%")
            # counter += 1
            feat = {
                'type': 'Feature',
                'properties': {
                    'id': int(n['id'][0]),
                    'u_rated': float(n['u_rated'][0]),
                    'feeder_branch_id': int(n['feeder_branch_id'][0]),
                    'feeder_node_id': int(n['feeder_node_id'][0]),
                    'coordinates': {
                        'geo': {
                            'lat': float(n['latitude'][0]),
                            'lon': float(n['longitude'][0]),
                        },
                        'fdg': {
                            'lat': float(n['fdg_lat'][0]),
                            'lon': float(n['fdg_lon'][0]),
                        },
                        'sld': {
                            'lat': float(n['sld_lat'][0]),
                            'lon': float(n['sld_lon'][0]),
                        }
                    },
                    'type_props': {

                    }
                },
                'geometry': {
                    "type": "Point",
                    "coordinates": [float(n['longitude'][0]), float(n['latitude'][0])],
                }
            }
            if n['node_type'] == NodeType.SUBSTATION_NODE:
                feat['properties']['type_props']['type'] = 'SUBSTATION'
                the_substation = sources[sources['node'] == n['id']][0]
                feat['properties']['type_props']['u_ref'] = float(the_substation['u_ref'][0])

            else:
                feat['properties']['type_props']['type'] = 'BUS'
                the_load = load[load['node'] == n['id']][0]
                feat['properties']['type_props']['p_specified'] = float(the_load['p_specified'][0])
                feat['properties']['type_props']['q_specified'] = float(the_load['q_specified'][0])
            geojson['features'].append(feat)

        node_end_parsing = time.perf_counter()
        self.log_timed_message(node_start_parsing, node_end_parsing, f"Parsed nodes to geojson")

        # Parse the lines
        line_start_parsing = time.perf_counter()
        # counter = 0
        # print('parsing the lines')
        for lin in lines:
            # if counter % int(len(lines) / 10) == 0:
            #     print(f"{counter} - {int((counter / len(lines)) * 100)}%")
            # counter += 1
            lin_id = lin['id'][0]
            cur_geo_path = geo_path[lin_id]
            cur_fdg_path = fdg_path[lin_id]
            cur_sld_path = sld_path[lin_id]
            feat = {
                'type': 'Feature',
                "properties": {
                    'id': int(lin_id),
                    'from_node': int(lin['from_node'][0]),
                    'to_node': int(lin['to_node'][0]),
                    'open': True if lin['to_status'][0] == 0 else False,
                    'feeder_branch_id': int(lin['feeder_branch_id'][0]),
                    'feeder_node_id': int(lin['feeder_node_id'][0]),
                    'is_feeder': bool(lin['is_feeder'][0]),
                    'r1': float(lin['r1'][0]),
                    'x1': float(lin['x1'][0]),
                    'c1': float(lin['c1'][0]),
                    'tan1': float(lin['tan1'][0]),
                    'i_n': float(lin['i_n'][0]),
                    'paths': {
                        'geo': cur_geo_path,
                        'sld': cur_sld_path,
                        'fdg': cur_fdg_path
                    }
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": cur_geo_path
                }
            }
            geojson['features'].append(feat)
        line_end_parsing = time.perf_counter()
        self.log_timed_message(line_start_parsing,line_end_parsing,"Parsed lines")

        start_time = time.perf_counter()
        folder = "./assets/parsed_geojson/"
        full_path = f'{folder}{name}.json'
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)
        end_time = time.perf_counter()
        self.log_timed_message(start_time=start_time,end_time=end_time,message="Time to save the geojson")
    def create_from_geojson(
            self,
            node_path: str,
            edge_path: str,
            file_path: str,
            seed=None,
            start_time=0
    ):
        grid = self.grid_class.empty(graph_model=self.graph_model)

        nodes = None
        edges = None

        node_types = ["LOW_VOLTAGE_DISTRIBUTION", "SUBSTATION", "MEDIUM_VOLTAGE_INSTALLATION"]
        edge_types = ["LOW_VOLTAGE_CABLE", "MEDIUM_VOLTAGE_CABLE", "HIGH_VOLTAGE_CABLE"]

        print(f"Loading files:\n{node_path}\n{edge_path}")

        loading_start_time = time.perf_counter()
        with open(node_path, "r") as f:
            nodes = json.load(f)
        with open(edge_path, "r") as f:
            edges = json.load(f)

        loading_end_time = time.perf_counter()
        self.log_timed_message(start_time=loading_start_time,end_time=loading_end_time,message="File loading time")

        substations = [n for n in nodes['features'] if n['properties']['type'] == node_types[1]]
        buses = [n for n in nodes['features'] if n['properties']['type'] != node_types[1]]
        lines = [e for e in edges['features']]

        self.log_list(substations, "SUBSTATIONS")

        src_gen_start_time = time.perf_counter()
        # Add the sources to the grid
        source_generator = SourceGenerator(grid=grid, seed=seed)
        substation_nodes, sources, id_mapping = source_generator.create_from_list(substations)
        src_gen_end_time = time.perf_counter()
        self.log_timed_message(start_time=src_gen_start_time,end_time=src_gen_end_time,message="Created the sources")
        grid.append(substation_nodes)
        grid.append(sources)

        self.log_list(substation_nodes, "SUBSTATION NODES")
        self.log_list(sources,'SOURCES')
        self.log_list(buses, "BUSES")

        bus_creation_start_time = time.perf_counter()
        # Add the buses to the grid
        node_generator = NodeGenerator(grid=grid, seed=seed)
        bus_nodes, low_loads, high_loads, id_mapping = node_generator.create_from_list(buses, id_mapping)
        bus_creation_end_time = time.perf_counter()
        self.log_timed_message(start_time=bus_creation_start_time,end_time=bus_creation_end_time,message="Creation of buses")

        grid.append(bus_nodes)
        grid.append(high_loads)

        self.log_list(bus_nodes, "BUS NODES")
        self.log_list(low_loads, "LOW_LOADS")
        self.log_list(high_loads, "HIGH_LOADS")
        self.log_list(lines, "LINES")

        paths = {}
        line_creation_start_time = time.perf_counter()
        line_generator = LineGenerator(grid=grid, seed=seed)
        line_array, geo_paths, id_mapping = line_generator.create_from_list(lines, substations, id_mapping)
        line_creation_end_time = time.perf_counter()
        self.log_timed_message(start_time=line_creation_start_time,end_time=line_creation_end_time,message="Line creation")
        grid.append(line_array)

        paths['geo'] = {g: [[latlng[1], latlng[0]] for latlng in geo_paths[g]] for g in geo_paths}
        paths['fdg'] = {g: [[latlng[1], latlng[0]] for latlng in geo_paths[g]] for g in geo_paths}
        paths['sld'] = {g: [[latlng[1], latlng[0]] for latlng in geo_paths[g]] for g in geo_paths}
        # Log the first element of each path:

        # Calculate the FDG positions


        self.log_list(line_array, "LINE ARRAY")
        self.log_dict(paths['geo'], "PATHS")
        self.log_dict(id_mapping, "IDS")

        # self.send_grid_to_geosjon(grid, paths,file_path)
        return grid, paths

    def load_from_geojson(self, path: str):
        print(path)
        grid = self.grid_class.empty(graph_model=self.graph_model)
        paths = {}
        with open(path, "r") as f:
            geojson = json.load(f)
        nodes = [n for n in geojson['features'] if n['geometry']['type'] == 'Point']

        buses = [n for n in nodes if n['properties']['type_props']['type'] == 'BUS']
        substations = [n for n in nodes if n['properties']['type_props']['type'] == 'SUBSTATION']
        lines = [n for n in geojson['features'] if n['geometry']['type'] == 'LineString']
        source_generator = SourceGenerator(grid=grid, seed=None)
        print("Creating substations")
        substation_nodes, sources, id_mapping = source_generator.create_from_geojson(substations)
        for s in substation_nodes:
            print(s)
        for s in sources:
            print(s)

        return grid, paths

    def create_radial_geographic(
            self,
            grid_center=None,
            grid_std=None,
            levels=0,
            children_mean=0,
            children_std=0,
            n_clusters=0,
            seed=None
    ):
        if grid_std is None:
            grid_std = [0.0, 0.0]
        if grid_center is None:
            grid_center = [0.0, 0.0]
        grid = self.grid_class.empty(graph_model=self.graph_model)

        # Add the sources in random points under a normal distribution around the grid_center with std grid_std
        source_generator = SourceGenerator(grid=grid, seed=seed)
        src_nodes, sources = source_generator.run(amount=self.nr_sources, grid_center=grid_center, grid_std=grid_std)
        grid.append(src_nodes)
        grid.append(sources)

        node_generator = NodeGenerator(grid=grid, seed=seed)
        nodes, l_load, h_load = node_generator.run(amount=self.nr_nodes)
        clusters = []
        current_node = 0
        depth = 0
        src_children = {}
        for j in range(self.nr_sources):
            src_lat = src_nodes[j].latitude
            src_lon = src_nodes[j].longitude

            src_id = src_nodes[j].id
            src_children[str(src_id)] = []
            for i in range(n_clusters):
                this_children = int(random.normalvariate(mu=children_mean, sigma=children_std))
                cluster_lon = round(random.normalvariate(mu=src_lon[0], sigma=grid_std[0]), 5)
                cluster_lat = round(random.normalvariate(mu=src_lat[0], sigma=grid_std[1]), 5)
                clusters.append({
                    'index': len(clusters),
                    'level': depth,
                    'id': nodes[current_node].id,
                    'center': [cluster_lon, cluster_lat],
                    'std': [grid_std[0]/this_children,grid_std[1]/this_children],
                    'parent': src_id,
                    'feeder_id': src_id,
                    'n_children': this_children,
                    'longitude': cluster_lon,
                    'latitude': cluster_lat,
                    'children': []
                })
                nodes.longitude[current_node] = cluster_lon
                nodes.latitude[current_node] = cluster_lat
                nodes.parent_id[current_node] = src_id
                nodes.feeder_node_id[current_node] = src_id
                current_node += 1
                src_children[str(src_id)].append(len(clusters) - 1)

        print("SOURCE CHILDREN:")
        print(src_children)

        candidates = [c['index'] for c in clusters if c['level'] == depth]
        depth += 1
        j = 0
        while current_node < len(nodes):
            # print(f"Beginning of loop Candidates has length {len(candidates)}, j is {j}")
            current = candidates[j]
            current_cluster = clusters[current]
            if len(current_cluster['children']) < current_cluster['n_children']:
                this_children = int(random.normalvariate(mu=children_mean, sigma=children_std))
                clusters[current]['children'].append(current_node)
                par_center = clusters[current]['center']
                par_std = clusters[current]['std']
                cur_lon = round(random.normalvariate(mu=par_center[0], sigma=par_std[0]), 5)
                cur_lat = round(random.normalvariate(mu=par_center[1], sigma=par_std[1]), 5)
                new_std = [par_std[0]/(float(clusters[current]['n_children'])), par_std[1]/(float(clusters[current]['n_children']))]
                new_node = {
                    'index': current_node,
                    'level': depth,
                    'id': nodes[current_node].id,
                    'center': [cur_lon, cur_lat],
                    'std': new_std,
                    'parent': clusters[current]['id'],
                    'feeder_id': clusters[current]['feeder_id'],
                    'n_children': this_children,
                    'longitude': cur_lon,
                    'latitude': cur_lat,
                    'children': []
                }
                clusters.append(new_node)
                nodes.longitude[current_node] = cur_lon
                nodes.latitude[current_node] = cur_lat
                nodes.parent_id[current_node] = clusters[current]['id']
                nodes.feeder_node_id[current_node] = clusters[current]['feeder_id']
                current_node += 1
                j += 1
                if j >= len(candidates):
                    j = 0
            else:
                c = candidates.pop(j)
                if j >= len(candidates):
                    j -= 1

            if len(candidates) <= 0:
                candidates = [c['index'] for c in clusters if c['level'] == depth]
                depth += 1
                # print(f"Candidates has length {len(candidates)}, j is {j}, depth is {depth}")
                # print(f"Current candidates: {candidates}")
                j = 0

        # FDG
        ids = [int(n.id[0]) for n in src_nodes]
        ids.extend([int(n.id[0]) for n in nodes])

        print('________\n_______')
        print('IDs:\n_______')
        print(ids)

        edges = []
        print(f"The ids are of type {type(ids[-1])}")
        for e in range(ids[-1]+1):
            edges.append([])
            for _ in range(ids[-1]+1):
                edges[e].append(0)

        for s in src_children:
            # print(f'source {(eval(s)[0])} has children: {src_children[s]}')
            s_id = eval(s)[0]
            for c in src_children[s]:
                edges[s_id][int(clusters[c]['id'])] += 1
                edges[int(clusters[c]['id'])][s_id] += 1

        for c in clusters:
            c_id = int(c['id'])
            for child in c['children']:
                child_id = int(clusters[child]['id'])
                edges[c_id][child_id] += 1
                edges[child_id][c_id] += 1
        # print('___________\n____________')
        # print('EDGES:\n__________')
        # for cur_id in ids:
        #     print(f"Edges of {cur_id}: {edges[cur_id]}")

        vertices = []
        vertices.extend([{'id': int(n.id), 'lat': float(n.latitude), 'lon': float(n.longitude), 'fdg_lat': float(n.fdg_lat), 'fdg_lon': float(n.fdg_lon)} for n in src_nodes])
        vertices.extend([{'id': int(n.id), 'lat': float(n.latitude), 'lon': float(n.longitude), 'fdg_lat': float(n.fdg_lat), 'fdg_lon': float(n.fdg_lon)} for n in nodes])

        # print('___________\n____________')
        # print('VERTICES:\n__________')
        # for v in vertices:
        #     print(v)

        #FDG mapping
        # fdg_positions = self.fdg_palcement_birchfield(edges,vertices)

        # Do the SLD mapping
        # -----------------------


        #Greedy approach

        # print("CLUSTERS\n_______________")
        # for c in clusters:
        #     print(c)
        #
        # print("SOURCES\n_____________")
        # for s in src_nodes:
        #     print(s)


        # print('_______________\n______________')
        # print("NODES\n____________")
        # for n in nodes:
        #     print(n)
        # print('_________________\n___________')
        # print("LOADS\n______")
        # for a in h_load:
        #     print(a)

        grid.append(nodes)
        grid.append(h_load)
        # for f in fdg_positions:
        #     grid.node.fdg_lat[grid.node.id == int(f['id'])] = f['fdg_lat']
        #     grid.node.fdg_lon[grid.node.id == int(f['id'])] = f['fdg_lon']
        # print(type(grid.node[0].fdg_lat))
        # grid.node.fdg_lat[grid.node.id == int(grid.node.id[0])] = 5.0
        # print(grid.node[0])
        print("NODES\n_____________")
        for s in grid.node:
            print(s)

        line_generator = LineGenerator(grid=grid, seed=seed)
        lines, basic_lines = line_generator.connect_geo_nodes(clusters)
        grid.append(lines)

        return grid



    def run(self, seed=None, create_10_3_kv_net: bool = False) -> T:
        """Run the generator to create a random radial grid.

        if a seed is provided, this will be used to set rng.
        """
        grid = self.grid_class.empty(graph_model=self.graph_model)
        # create nodeArray
        node_generator = NodeGenerator(grid=grid, seed=seed)

        nodes, _loads_low, loads_high = node_generator.run(amount=self.nr_nodes)
        grid.append(nodes)
        grid.append(loads_high)
        # create sourceArray
        source_generator = SourceGenerator(grid=grid, seed=seed)
        nodes, sources = source_generator.run(amount=self.nr_sources)
        grid.append(nodes)
        grid.append(sources)

        # create lineArray
        line_generator = LineGenerator(grid=grid, seed=seed)
        lines = line_generator.run(amount=self.nr_nops)
        grid.append(lines)
        if create_10_3_kv_net:
            # create 3kV nodes
            nodes, _loads_low, _loads_high = node_generator.run(amount=10, voltage_level=3_000)
            grid.append(nodes)
            grid.append(_loads_high)

            # create transformerArray
            transformer_generator = TransformerGenerator(grid=grid, seed=seed)
            transformers = transformer_generator.run(amount=2)
            grid.append(transformers)

            lines = line_generator.run(amount=0, number_of_routes=0)
            grid.append(lines[~np.isin(lines.id, grid.line.id)])

        return grid
