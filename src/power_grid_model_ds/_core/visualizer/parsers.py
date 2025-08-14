# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from typing import Any, Literal

from power_grid_model_ds._core.model.arrays.base.array import FancyArray
from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds.arrays import Branch3Array, BranchArray, NodeArray
import os
import json
import random

def parse_node_array(nodes: NodeArray) -> list[dict[str, Any]]:
    """Parse the nodes."""
    parsed_nodes = []

    with_coords = "x" in nodes.columns and "y" in nodes.columns

    columns = nodes.columns
    for node in nodes:
        cyto_elements = {"data": _array_to_dict(node, columns)}
        cyto_elements["data"]["id"] = str(node.id.item())
        cyto_elements["data"]["group"] = "node"
        if with_coords:
            cyto_elements["position"] = {"x": node.x.item(), "y": -node.y.item()}  # invert y-axis for visualization
        parsed_nodes.append(cyto_elements)
    return parsed_nodes


def parse_branches(grid: Grid) -> list[dict[str, Any]]:
    """Parse the branches."""
    parsed_branches = []
    parsed_branches.extend(parse_branch_array(grid.line, "line"))
    parsed_branches.extend(parse_branch_array(grid.link, "link"))
    parsed_branches.extend(parse_branch_array(grid.transformer, "transformer"))
    parsed_branches.extend(parse_branch3_array(grid.three_winding_transformer, "transformer"))
    return parsed_branches


def parse_branch3_array(branches: Branch3Array, group: Literal["transformer"]) -> list[dict[str, Any]]:
    """Parse the three-winding transformer array."""
    parsed_branches = []
    columns = branches.columns
    for branch3 in branches:
        for branch1 in branch3.as_branches():
            cyto_elements = {"data": _array_to_dict(branch1, columns)}
            cyto_elements["data"].update(
                {
                    # IDs need to be unique, so we combine the branch ID with the from and to nodes
                    "id": str(branch3.id.item()) + f"_{branch1.from_node.item()}_{branch1.to_node.item()}",
                    "source": str(branch1.from_node.item()),
                    "target": str(branch1.to_node.item()),
                    "group": group,
                }
            )
            parsed_branches.append(cyto_elements)
    return parsed_branches


def parse_branch_array(branches: BranchArray, group: Literal["line", "link", "transformer"]) -> list[dict[str, Any]]:
    """Parse the branch array."""
    parsed_branches = []
    columns = branches.columns
    for branch in branches:
        cyto_elements = {"data": _array_to_dict(branch, columns)}
        cyto_elements["data"].update(
            {
                "id": str(branch.id.item()),
                "source": str(branch.from_node.item()),
                "target": str(branch.to_node.item()),
                "group": group,
            }
        )
        parsed_branches.append(cyto_elements)
    return parsed_branches


def _array_to_dict(array_record: FancyArray, columns: list[str]) -> dict[str, Any]:
    """Stringify the record (required by Dash)."""
    return dict(zip(columns, array_record.tolist().pop()))


def parse_nodes_geojson(nodes: NodeArray) \
        -> tuple[list[dict[str, Any]], dict[str, list[float]]]:
    """Parses the nodes in the grid into a list of feature element for the geojson and a dictionary

        Parameters
        ----------
        nodes: NodeArray
            The nodes in the grid

        Returns
        ---------
        parsed_nodes: list[dict[str, Any]]
            The parsed nodes in the grid

        node_dict: dict[str, list[float]]
            Dictionary with the nodes in the grid
    """

    parsed_nodes = []
    node_dict = {}

    # Mean and std of latitude and longitude to set the current coordinates as random
    center = [4.36716, 52.00738]
    extreme = [4.39349, 51.98508]
    std_lon = (extreme[0] - center[0]) / 3
    std_lat = (extreme[1] - center[1]) / 3
    print(f"Node columns: {nodes.columns}")
    for node in nodes:
        data = _array_to_dict(node, nodes.columns)
        node_name = str(node.id.item())
        node_dict[node_name] = \
            [
                round(random.normalvariate(mu=center[0], sigma=std_lon), 5),
                round(random.normalvariate(mu=center[1], sigma=std_lat), 5)
            ]
        element = {
            "type": "Feature",
            "properties": {
                "Name": node_name,
                "data": data,
                "coords": {
                    "geo": node_dict[node_name],
                    "fdg": center,
                    "sdl": extreme
                }
            },
            "geometry": {
                "type": "Point",
                "coordinates": node_dict[node_name]
            }
        }
        parsed_nodes.append(element)
    return parsed_nodes, node_dict


def parse_branch_array_geojson(
        branches: BranchArray,
        group: Literal["line", "link", "transformer"],
        node_dict: dict[str, list[float]]) \
        -> list[dict[str, Any]]:
    """Parses a branch array of a single type as a list of geojson features

    Parameters
    ----------
    branches: BranchArray
    The branch array of specific type

    group: Literal["line", "link", "transformer"]
    The type of the branch array. Can be 'line', 'link', or 'transformer'

    node_dict: dict[str, list[float]]
    Dictionary with the nodes in the grid

    Returns
    -----------
    list[dict[str, Any]]
    parsed branches

    """
    parsed_branches = []
    columns = branches.columns
    print(f"{group} columns: {columns}")
    for branch in branches:
        data = _array_to_dict(branch, columns)
        data["group"] = group
        element = {
            "type": "Feature",
            "properties": {
                "Name": str(branch.id.item()),
                "data": data
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [node_dict[str(branch.from_node.item())], [node_dict[str(branch.to_node.item())]]]
            }
        }
        parsed_branches.append(element)
    return parsed_branches


def parse_branches_geojson(
        grid: Grid,
        node_dict: dict[str, list[float]]) \
        -> list[dict[str, Any]]:
    """Parse the branches into a list of feature element for the geojson

    Parameters
    ----------
    grid: Grid
    The grid

    node_dict: dict[str, list[float]]
    Dictionary with the nodes in the grid

    Returns
    ----------
    parsed_branches: list[dict[str, Any]]
    The parsed branches in the grid as geojson features

    """
    parsed_branches = []
    parsed_branches.extend(parse_branch_array_geojson(grid.line, "line", node_dict))
    parsed_branches.extend(parse_branch_array_geojson(grid.link, "link", node_dict))
    parsed_branches.extend(parse_branch_array_geojson(grid.transformer, "transformer", node_dict))
    return parsed_branches


def parse_grid_to_geojson(
        grid: Grid,
        name: str,
        file_name: str) \
        -> dict[str, any]:
    """Parses the grid into GeoJSON format and stores it in a file

    Parameters
    ------------
    grid: Grid
        The grid to be parsed

    name: str
        Name of the Feature Collection

    file_name: str
        Name of the file to store the GeoJSON

    Returns
    -------------
    dict[str, Any]
        Dictionary with the grid parsed as geojson

    """

    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)

    features = []
    parsed_nodes, node_dict = parse_nodes_geojson(grid.node)
    parsed_branches = parse_branches_geojson(grid, node_dict)

    features.extend(parsed_nodes)
    features.extend(parsed_branches)
    geojson = {

        "type": "FeatureCollection",
        "name": f"{name}",
        "features": features
    }
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=4)
    return geojson


def divide_geojson(geojson: dict[str, any]) -> tuple[dict[str, any], dict[str, any]]:
    nodes = [f for f in geojson["features"] if f["geometry"]["type"] == "Point"]
    branches = [f for f in geojson["features"] if f["geometry"]["type"] == "LineString"]
    nodes_geojson = {
        "type": "FeatureCollection",
        "name": "NODES",
        "features": nodes
    }
    branches_geojson = {
        "type": "FeatureCollection",
        "name": "BRANCHES",
        "features": branches
    }
    return nodes_geojson, branches_geojson
def parse_geojson_to_dict(geojson: dict[str, any]) -> dict[str, any]:
    dictionary = {}
    for f in geojson["features"]:
        dictionary[f["properties"]["Name"]] = f
    return dictionary
