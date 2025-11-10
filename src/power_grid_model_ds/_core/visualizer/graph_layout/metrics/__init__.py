from .avoid_too_small_angles_between_incident_edges import calculate_mia
from .avoid_too_small_edge_lengths import calculate_mel
from .avoid_too_small_node_to_node_distances import calculate_mnd
from .avoid_unnecessary_line_crossings import calculate_mex
from .improve_line_orthogonality import calculate_mor
from .improve_spatial_evenness import calculate_mev
from .maintain_relative_positions_of_nodes import calculate_mrp
from .stay_close_to_initial_position import calculate_mip
from power_grid_model_ds import Grid
import numpy as np


def calculate(grid: Grid, geo_paths, fdg_paths, sld_paths):
    geo_nodes, fdg_nodes, sld_nodes = parse_node_arrays(grid)


    fdg_metrics = {
        "m_ex": calculate_mex(),
        "m_el": calculate_mel(fdg_paths),
        "m_nd": calculate_mnd(fdg_nodes),
        "m_ia": calculate_mia(),
        "m_rp": calculate_mrp(geo_paths, fdg_paths),
        "m_or": calculate_mor(fdg_paths),
        "m_ev": calculate_mev(fdg_nodes),
        "m_ip": calculate_mip(fdg_nodes, geo_nodes)
    }
    sld_metrics = {
        "m_ex": calculate_mex(),
        "m_el": calculate_mel(sld_paths),
        "m_nd": calculate_mnd(sld_nodes),
        "m_ia": calculate_mia(),
        "m_rp": calculate_mrp(geo_paths, sld_paths),
        "m_or": calculate_mor(sld_paths),
        "m_ev": calculate_mev(sld_nodes),
        "m_ip": calculate_mip(sld_nodes, geo_nodes)
    }
    return fdg_metrics, sld_metrics

def parse_node_arrays(grid: Grid):
    geo_lat = np.asarray(grid.node.latitude)
    geo_lon = np.asarray(grid.node.longitude)
    geo_nodes = np.column_stack((geo_lat, geo_lon))
    fdg_lat = np.asarray(grid.node.fdg_lat)
    fdg_lon = np.asarray(grid.node.fdg_lon)
    fdg_nodes = np.column_stack((fdg_lat, fdg_lon))
    sld_lat = np.asarray(grid.node.sld_lat)
    sld_lon = np.asarray(grid.node.sld_lon)
    sld_nodes = np.column_stack((sld_lat, sld_lon))
    # print(f"GEO:\n{geo_nodes}\nFDG:\n{fdg_nodes}\nSLD:\n{sld_nodes}\n")
    return geo_nodes, fdg_nodes, sld_nodes
