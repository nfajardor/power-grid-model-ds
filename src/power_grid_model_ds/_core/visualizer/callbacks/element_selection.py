from dash import callback, Input, Output, State, ctx
import json

@callback(
    Output("slider-output-text", "children"),
    Output("nodes-geolayer", "hideout", allow_duplicate=True),
    Output("edges-geolayer", "hideout", allow_duplicate=True),
    Input("nodes-geolayer","clickData"),
    Input("edges-geolayer","clickData"),
    State('nodes-geolayer', 'hideout'),
    State('edges-geolayer', 'hideout'),
    prevent_initial_call=True
)
def select_element(node_clicked, edge_clicked, node_hideout, edge_hideout):
    trig = ctx.triggered_id
    node_copy = node_hideout.copy() if node_hideout else {}
    edge_copy = edge_hideout.copy() if edge_hideout else {}
    if node_clicked is not None and trig == "nodes-geolayer":
        data = node_clicked["properties"]['data']
        edge_copy['selected_id'] = data['id']
        node_copy['selected_id'] = data['id']
        node_copy['selected_geo'] = [data['latitude'], data['longitude']]
        node_copy['selected_fdg'] = [data['fdg_lat'], data['fdg_lon']]
        node_copy['selected_sld'] = [data['sld_lat'], data['sld_lon']]
        edge_copy['selected_geo'] = [data['latitude'], data['longitude']]
        edge_copy['selected_fdg'] = [data['fdg_lat'], data['fdg_lon']]
        edge_copy['selected_sld'] = [data['sld_lat'], data['sld_lon']]
        if data['node_type'] == 1:
            return f"Selected substation {data['id']}:\nRated Power: {data['u_rated']}\nRef. Power: {node_clicked['properties']['type_props']['u_ref']}\n", node_copy, edge_copy
        return f"Selected bus {data['id']}:\nRated Power: {data['u_rated']}\nActive power: {node_clicked['properties']['type_props']['p_specified']}\nReactive power: {node_clicked['properties']['type_props']['q_specified']}\n", node_copy, edge_copy

    if edge_clicked is not None and trig == "edges-geolayer":
        data = edge_clicked["properties"]['data']
        edge_copy['selected_id'] = data['id']
        node_copy['selected_id'] = data['id']
        from_geo = data['from_geo']
        to_geo = data['to_geo']
        from_fdg = data['from_fdg']
        to_fdg = data['to_fdg']
        from_sld = data['from_sld']
        to_sld = data['to_sld']
        node_copy['selected_geo'] = get_midpoint(from_geo[1], from_geo[0], to_geo[1], to_geo[0])
        node_copy['selected_fdg'] = get_midpoint(from_fdg[1], from_fdg[0], to_fdg[1], to_fdg[0])
        node_copy['selected_sld'] = get_midpoint(from_sld[1], from_sld[0], to_sld[1], to_sld[0])
        edge_copy['selected_geo'] = get_midpoint(from_geo[1], from_geo[0], to_geo[1], to_geo[0])
        edge_copy['selected_fdg'] = get_midpoint(from_fdg[1], from_fdg[0], to_fdg[1], to_fdg[0])
        edge_copy['selected_sld'] = get_midpoint(from_sld[1], from_sld[0], to_sld[1], to_sld[0])
        return f"Edge: {data['id']} connecting nodes {data['from_node']} and {data['to_node']}\nResistance: {data['r1']}\nReactance: {data['x1']}\nCapacitance: {data['c1']}\nLoss Factor: {data['tan1']}\nRated Current {data['i_n']}", node_copy, edge_copy

    return "Click an element to select it", node_copy, edge_copy


def get_midpoint(from_lat, from_lon, to_lat, to_lon):
    return [(from_lat + to_lat) / 2, (from_lon + to_lon) / 2 ]
# @callback(
#     Output("slider-output-text", "children"),
#     Output('nodes-geolayer', 'hideout'),
#     Output('edges-geolayer', 'hideout'),
#     Input("nodes-geolayer","clickData"),
#     Input("edges-geolayer","clickData"),
#     State('nodes-geolayer', 'node-hideout'),
#     State('edges-geolayer', 'edge-hideout'),
#     prevent_initial_call=True
# )
# def select_element(node_clicked, edge_clicked, n_hideout, e_hideout):
#     trig = ctx.triggered_id
#     node_copy = n_hideout.copy() if n_hideout else {}
#     edge_copy = e_hideout.copy() if e_hideout else {}
#     if node_clicked is not None and trig == "nodes-geolayer":
#         data = node_clicked["properties"]['data']
#         node_copy['selected_id'] = data['id']
#         edge_copy['selected_id'] = data['id']
#         if data['node_type'] == 1:
#             return f"Selected substation {data['id']}:\nRated Power: {data['u_rated']}\nRef. Power: {node_clicked['properties']['type_props']['u_ref']}\n", node_copy, edge_copy
#         return f"Selected bus {data['id']}:\nRated Power: {data['u_rated']}\nActive power: {node_clicked['properties']['type_props']['p_specified']}\nReactive power: {node_clicked['properties']['type_props']['q_specified']}\n" , node_copy, edge_copy
#
#     if edge_clicked is not None and trig == "edges-geolayer":
#         data = edge_clicked["properties"]['data']
#         node_copy['selected_id'] = data['id']
#         edge_copy['selected_id'] = data['id']
#         return f"Edge: {data['id']} connecting nodes {data['from_node']} and {data['to_node']}\nResistance: {data['r1']}\nReactance: {data['x1']}\nCapacitance: {data['c1']}\nLoss Factor: {data['tan1']}\nRated Current {data['i_n']}", node_copy, edge_copy
#
#     return "Click an element to select it", node_copy, edge_copy
