import dash_bootstrap_components as dbc
from power_grid_model_ds._core.visualizer.parsers import parse_geojson_to_dict, divide_geojson
from dash import html
import dash_leaflet as dl
from dash_extensions.javascript import Namespace
import json
import os
import numpy as np
from power_grid_model_ds._core.visualizer.callbacks import property_dropdowns


def create_map_container(geojson: dict[str, any], centroid: dict[str, float]) -> dbc.Row:
    center = [centroid['lon'], centroid['lat']]
    nodes_geojson, branch_geojson = divide_geojson(geojson)
    # nodes = parse_geojson_to_dict(nodes_geojson)
    node_functions = Namespace("functionalProperties", "nodeFunctions")
    line_functions = Namespace("functionalProperties", "lineFunctions")
    line_style = {
        'color': 'red',
        'weight': 3
    }
    # print(f"nodes geojson: {nodes_geojson}")
    buses = [n for n in nodes_geojson['features'] if n['properties']['type_props']['type'] == 'BUS']
    active_powers = np.array([n['properties']['type_props']['p_specified'] for n in buses])
    reactive_powers = np.array([n['properties']['type_props']['q_specified'] for n in buses])
    print(f"active powers: {np.min(active_powers)} -> {np.max(active_powers)}")
    print(f"reactive powers: {np.min(reactive_powers)} -> {np.max(reactive_powers)}")

    lines = [n for n in branch_geojson['features']]
    resistances = np.array([n['properties']['data']['r1'] for n in lines])
    reactances = np.array([n['properties']['data']['x1'] for n in lines])
    currents = np.array([n['properties']['data']['i_n'] for n in lines])
    tiles = dl.TileLayer(id='tiles', url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png")

    nodes_layer = dl.GeoJSON(
        id="nodes-geolayer",
        data=nodes_geojson,
        pointToLayer=node_functions("pointToLayer"),
        hideout={
            'value': 0.0,
            'max_active': np.max(active_powers),
            'max_reactive': np.max(reactive_powers),
            'min_active': np.min(active_powers),
            'min_reactive': np.min(reactive_powers),
            'current_property': property_dropdowns.NodeDropdownOptions.ACTIVE_POWER,
            'selected_id': -1,
            'selected_geo': [center[1], center[0]],
            'selected_fdg': [center[1], center[0]],
            'selected_sld': [center[1], center[0]]
        },
        options={"interactive": True, "bubblingMouseEvents": True},
        pane="nodes"
    )

    edges_layer = dl.GeoJSON(
        id="edges-geolayer",
        data=branch_geojson,
        #onEachFeature=node_functions("onEachEdge"),
        onEachFeature=line_functions("onEachFeature"),
        style=line_functions("style"),
        options={"interactive": True, "bubblingMouseEvents": True},
        hideout={
            'value': 0.0,
            'current_property': property_dropdowns.EdgeDropdownOptions.RESISTANCE,
            'min_resistance': np.min(resistances),
            'max_resistance': np.max(resistances),
            'min_reactance': np.min(reactances),
            'max_reactance': np.max(reactances),
            'min_current': np.min(currents),
            'max_current': np.max(currents),
            'selected_id': -1,
            'selected_geo': [center[1], center[0]],
            'selected_fdg': [center[1], center[0]],
            'selected_sld': [center[1], center[0]]

        },
        pane="edges"
    )

    map_element = dl.Map(
                id='the-map',
                children=[
                    dl.Pane(children=tiles, name="tiles", style={"zIndex": 0}),
                    dl.Pane(children=edges_layer, name="edges", style={"zIndex":100}),
                    dl.Pane(children=nodes_layer, name="nodes", style={"zIndex":200}),
                ],
                center={'lat': center[1], 'lng': center[0]},
                zoom=10,
                maxZoom=18,
                style={"height": "600px", "width": "1000px", "border": "2px solid #333", "borderRadius": "12px"},
                # preferCanvas=True
    )


    return dbc.Row([
        dbc.Col([map_element], width=12)
    ])
