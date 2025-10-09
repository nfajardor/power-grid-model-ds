import dash_bootstrap_components as dbc
from power_grid_model_ds._core.visualizer.parsers import parse_geojson_to_dict, divide_geojson
from dash import html
import dash_leaflet as dl
from dash_extensions.javascript import Namespace
import json
import os


def create_map_container(geojson: dict[str, any], centroid: dict[str, float]) -> dbc.Row:
    center = [centroid['lon'], centroid['lat']]
    nodes_geojson, branch_geojson = divide_geojson(geojson)
    nodes = parse_geojson_to_dict(nodes_geojson)
    node_functions = Namespace("functionalProperties", "nodeFunctions")
    line_functions = Namespace("functionalProperties", "lineFunctions")
    line_style = {
        'color': 'black',
        'weight': 1
    }
    folder = './assets/grid_geojson/'
    # folder = './MV_rural_1_176_nodes_171_edges/'
    bus_file = f"{folder}grid_100_nodes_152_edges_NODES.json"
    line_file = f"{folder}grid_100_nodes_152_edges_EDGES.json"
    # transformer_file = "transformers.geojson"

    with open(f"{bus_file}","r") as f:
        buses = json.load(f)

    # with open(f"{folder}{transformer_file}", "r") as f:
    #     transformers = json.load(f)

    with open(f"{line_file}", "r") as f:
        lines = json.load(f)

    tiles = dl.TileLayer(id='tiles', url="https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png")
    # tiles = dl.TileLayer(id='tiles')
    nodes_layer = dl.GeoJSON(
        id="nodes-geolayer",
        data=nodes_geojson,
        pointToLayer=node_functions("pointToLayer"),
        # hideout={'value': 0.0},
        # cluster=True,
        # zoomToBoundsOnClick=True,
        # superClusterOptions={"radius": 15},
        # spiderfyOnMaxZoom=True
    )

    edges_layer = dl.GeoJSON(
        id="edges-geolayer",
        data=branch_geojson,
        #onEachFeature=node_functions("onEachEdge"),
        onEachFeature=line_functions("onEachFeature"),
        style=line_style,
        hideout={'value': 0.0}
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

    # bus_layer = dl.GeoJSON(
    #     id="bus-geolayer",
    #     data=buses,
    #     pointToLayer=alliander_data_functions("pointToLayer"),
    #     onEachFeature=alliander_data_functions("onEachFeatureTooltip"),
    #     # cluster=True,
    #     # zoomToBoundsOnClick=True,
    #     # superClusterOptions={"radius": 100}
    # )

    # transformer_layer = dl.GeoJSON(
    #     id="transformer-geolayer",
    #     data=transformers,
    #     pointToLayer=alliander_data_functions("pointToLayer"),
    #     onEachFeature=alliander_data_functions("onEachFeatureTooltip"),
    #     cluster=True,
    #     zoomToBoundsOnClick=True,
    #     superClusterOptions={"radius": 100}
    # )

    # line_layer = dl.GeoJSON(
    #     id='line-geolayer',
    #     data=lines,
    #     style=line_style
    # )
    #
    # new_map = dl.Map(
    #     id="new-map",
    #     children=[
    #         tiles,
    #         bus_layer,
    #         # transformer_layer,
    #         line_layer
    #     ],
    #     center=[center[1], center[0]],
    #     zoom=20,
    #     style={"height": "100vh"},
    #     preferCanvas=True
    # )

    return dbc.Row([
        dbc.Col([map_element], width=12)
    ])
