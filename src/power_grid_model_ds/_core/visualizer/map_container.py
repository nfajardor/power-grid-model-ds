import dash_bootstrap_components as dbc
from power_grid_model_ds._core.visualizer.parsers import parse_geojson_to_dict, divide_geojson
from dash import html
import dash_leaflet as dl
from dash_extensions.javascript import Namespace

def create_map_container(geojson: dict[str, any]) -> dbc.Row:
    center = [4.36716, 52.00738]
    nodes_geojson, branch_geojson = divide_geojson(geojson)
    nodes = parse_geojson_to_dict(nodes_geojson)
    print(nodes)

    node_functions = Namespace("functionalProperties", "nodeFunctions")

    tiles = dl.TileLayer(id='tiles')
    nodes_layer = dl.GeoJSON(
        id="nodes-geolayer",
        data=nodes_geojson,
        pointToLayer=node_functions("pointToLayer")
    )

    map_element = dl.Map(
                id='the-map',
                children=[
                    tiles,
                    nodes_layer
                ],
                center=[center[1], center[0]],
                zoom=20,
                style={"height": "100vh"}
            )

    return dbc.Row([
        dbc.Col([map_element], width=12)
    ])
