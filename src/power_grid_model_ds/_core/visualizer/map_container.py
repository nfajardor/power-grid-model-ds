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
        'color': 'black',
        'weight': 3
    }

    buses = [n for n in nodes_geojson['features'] if n['properties']['type_props']['type'] == 'BUS']
    active_powers = np.array([n['properties']['type_props']['p_specified'] for n in buses])
    reactive_powers = np.array([n['properties']['type_props']['q_specified'] for n in buses])
    print(f"active powers: {np.min(active_powers)} -> {np.max(active_powers)}")
    print(f"reactive powers: {np.min(reactive_powers)} -> {np.max(reactive_powers)}")

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
            'current_property': property_dropdowns.NodeDropdownOptions.ACTIVE_POWER
        },
    )

    edges_layer = dl.GeoJSON(
        id="edges-geolayer",
        data=branch_geojson,
        #onEachFeature=node_functions("onEachEdge"),
        onEachFeature=line_functions("onEachFeature"),
        style=line_style,
        hideout={
            'value': 0.0,
            'current_property': property_dropdowns.EdgeDropdownOptions.RESISTANCE
        }
    )

    map_element = dl.Map(
                id='the-map',
                children=[
                    tiles,
                    edges_layer,
                    nodes_layer,
                ],
                center=[center[1], center[0]],
                zoom=10,
                maxZoom=18,
                style={"height": "100vh"},
                preferCanvas=True
    )


    return dbc.Row([
        dbc.Col([map_element], width=12)
    ])
