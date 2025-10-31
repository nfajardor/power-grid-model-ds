from dash import Input, Output, callback, State


@callback(
    Output('tiles', 'opacity'),
    Output('nodes-geolayer', 'hideout'),
    Output('edges-geolayer', 'hideout'),
    Input('main-slider', 'value'),
    State('nodes-geolayer', 'hideout'),
    State('edges-geolayer', 'hideout'),
)
def update_slider_value(value, node_hideout, edge_hideout):
    new_opacity = 1
    if value >= 0.5:
        new_opacity = 3 - 4 * value

    updated_node_hideout = node_hideout.copy() if node_hideout else {}
    updated_edge_hideout = edge_hideout.copy() if edge_hideout else {}

    updated_node_hideout['value'] = value
    updated_edge_hideout['value'] = value

    return new_opacity, updated_node_hideout, updated_edge_hideout


