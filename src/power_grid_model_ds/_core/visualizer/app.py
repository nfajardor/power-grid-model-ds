# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash_bootstrap_components.icons import FONT_AWESOME

from power_grid_model_ds._core.model.grids.base import Grid
from power_grid_model_ds._core.visualizer.callbacks import (  # noqa: F401  # pylint: disable=unused-import
    config,
    element_selection,
    header,
    search_form,
    slider_output,
    property_dropdowns
)
from power_grid_model_ds._core.visualizer.layout.cytoscape_html import get_cytoscape_html
from power_grid_model_ds._core.visualizer.layout.cytoscape_styling import DEFAULT_STYLESHEET
from power_grid_model_ds._core.visualizer.layout.header import HEADER_HTML
from power_grid_model_ds._core.visualizer.layout.selection_output import SELECTION_OUTPUT_HTML
from power_grid_model_ds._core.visualizer.parsers import parse_branches, parse_node_array, parse_grid_to_geojson, \
    parse_grid_to_geojson_new
from power_grid_model_ds.arrays import NodeArray

from power_grid_model_ds._core.visualizer.map_container import create_map_container
from power_grid_model_ds._core.visualizer.parsers import SLIDER_STEP

import time
import json
import numpy as np

GOOGLE_FONTS = "https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
BOOTSTRAP_STUFF = "https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/8.2.0/mdb.min.css"


def visualize(grid: Grid, debug: bool = False, port: int = 8050) -> None:
    """Visualize the Grid.

    grid: Grid
        The grid to visualize.

    layout: str
        The layout to use.

        If 'layout' is not provided (""):
            And grid.node contains "x" and "y" columns:
                The layout will be set to "preset" which uses the x and y coordinates to place the nodes.
            Otherwise:
                The layout will be set to "breadthfirst", which is a hierarchical breadth-first-search (BFS) layout.
        Other options:
            - "random": A layout that places the nodes randomly.
            - "circle": A layout that places the nodes in a circle.
            - "concentric": A layout that places the nodes in concentric circles.
            - "grid": A layout that places the nodes in a grid matrix.
            - "cose": A layout that uses the CompoundSpring Embedder algorithm (force-directed layout)
    """

    app = Dash(
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP, BOOTSTRAP_STUFF, FONT_AWESOME, GOOGLE_FONTS]
    )
    app.layout = get_app_layout(grid)
    app.run(debug=debug, port=port)


def slider_visualization_from_file(grid, file_name: str, paths, debug: bool = True, port: int = 8050, name: str = "Grid Data") -> None:
    """Visualize the Grid using the three mdoes: map, fdg and sld.

        grid: Grid
            The grid to visualize.

        debug: bool
            Whether to initialize the dash app in debug mode.

        port: int
            Port to access the app
        """
    app = Dash(
        external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP, BOOTSTRAP_STUFF, FONT_AWESOME, GOOGLE_FONTS]
    )
    s = time.perf_counter()
    app.layout = get_slider_app_layout(grid, name, file_name, paths)
    e = time.perf_counter()
    print(f"Layout creation time: {(e-s) * 1000}ms")
    app.run(debug=debug, port=port, dev_tools_ui=False, dev_tools_props_check=False)

def get_slider_app_layout(grid, name: str, file_name: str, paths) -> dbc.Container:
    t1 = time.perf_counter()
    menu = get_menu_layout()
    t2 = time.perf_counter()
    map_container = get_map_layout(grid, name, file_name, paths)
    t3 = time.perf_counter()
    print(f"Menu creation time: {(t2 - t1) * 1000}ms")
    print(f"Map creation time: {(t3-t2) * 1000}ms")
    return dbc.Container([
        menu,
        map_container
    ])


def get_map_layout(grid, name: str, file_name: str, paths) -> dbc.Row:
    t1 = time.perf_counter()
    # with open(file_name, "r") as f:
    #     geojson = json.load(f)
    # print(geojson)
    # x = np.asarray([i['properties']['coordinates']['geo']['lon'] for i in geojson['features'] if i['geometry']['type'] == 'Point'])
    # y = np.asarray([i['properties']['coordinates']['geo']['lat'] for i in geojson['features'] if i['geometry']['type'] == 'Point'])
    # print(f"X:\n{x}\nY:\n{y}")
    # centroid = {'lon': float(np.mean(x)), 'lat': float(np.mean(y))}
    geojson, centroid = parse_grid_to_geojson_new(grid, name, file_name, paths)
    t2 = time.perf_counter()
    map_container = create_map_container(geojson, centroid)
    t3 = time.perf_counter()
    print(f"GeoJSON mapping: {(t2 - t1) * 1000}ms")
    print(f"map container creation time: {(t3 - t2) * 1000}ms")
    return map_container


def get_menu_layout() -> dbc.Row:
    slider = dcc.Slider(
        id='main-slider',
        min=0,
        max=1,
        step=SLIDER_STEP,
        value=0,
        marks={0: 'Map View', 0.5: "FDG View", 1: "SLD View"},
        updatemode="drag"
    )
    text_output = html.Div(
        id="slider-output-text",
        children=["Hello World!"],
    )
    node_dropdown = dcc.Dropdown(options=[
        {'label': 'Active Power', 'value': property_dropdowns.NodeDropdownOptions.ACTIVE_POWER},
        {'label': 'Reactive Power', 'value': property_dropdowns.NodeDropdownOptions.REACTIVE_POWER}
        ], value=property_dropdowns.NodeDropdownOptions.ACTIVE_POWER, id='node_dropdown')

    edge_dropdown = dcc.Dropdown(options=[
        {'label': 'Resistance', 'value': property_dropdowns.EdgeDropdownOptions.RESISTANCE},
        {'label': 'Reactance', 'value': property_dropdowns.EdgeDropdownOptions.REACTANCE},
        {'label': 'Current', 'value': property_dropdowns.EdgeDropdownOptions.CURRENT},
    ],
    value= property_dropdowns.EdgeDropdownOptions.RESISTANCE,
    id='edge_dropdown')
    # edge_dropdown = dcc.Dropdown(['Resistance', 'Reactance', 'Capacitance', 'Loss Factor', 'Current'], 'Current', id='edge_dropdown')
    return dbc.Row([
        dbc.Col([slider], width=4),
        dbc.Col([node_dropdown, edge_dropdown], width=4),
        dbc.Col([text_output], width=4)
    ])


def _get_columns_store(grid: Grid) -> dcc.Store:
    return dcc.Store(
        id="columns-store",
        data={
            "node": grid.node.columns,
            "line": grid.line.columns,
            "link": grid.link.columns,
            "transformer": grid.transformer.columns,
            "three_winding_transformer": grid.three_winding_transformer.columns,
            "branch": grid.branches.columns,
        },
    )


def get_app_layout(grid: Grid) -> html.Div:
    """Get the app layout."""
    columns_store = _get_columns_store(grid)
    graph_layout = _get_graph_layout(grid.node)
    elements = parse_node_array(grid.node) + parse_branches(grid)
    cytoscape_html = get_cytoscape_html(graph_layout, elements)

    return html.Div(
        [
            columns_store,
            dcc.Store(id="stylesheet-store", data=DEFAULT_STYLESHEET),
            HEADER_HTML,
            html.Hr(style={"border-color": "white", "margin": "0"}),
            cytoscape_html,
            SELECTION_OUTPUT_HTML,
        ],
    )


def _get_graph_layout(nodes: NodeArray) -> str:
    """Determine the graph layout"""
    if "x" in nodes.columns and "y" in nodes.columns:
        return "preset"
    return "breadthfirst"
