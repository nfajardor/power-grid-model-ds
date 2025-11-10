from dash import Input, Output, callback, State, html, no_update
import json

@callback(
    Output('tiles', 'opacity'),
    Output('nodes-geolayer', 'hideout'),
    Output('edges-geolayer', 'hideout'),
    Output("the-map", 'center'),
    # Output('slider-output-text','children', allow_duplicate=True),
    Input('main-slider', 'value'),
    State('nodes-geolayer', 'hideout'),
    State('edges-geolayer', 'hideout'),
    State('the-map', 'center'),
    prevent_initial_call=True
)
def update_slider_value(value, node_hideout, edge_hideout, center):
    new_opacity = 1
    if value >= 0.5:
        new_opacity = 3 - 4 * value

    updated_node_hideout = node_hideout.copy() if node_hideout else {}
    updated_edge_hideout = edge_hideout.copy() if edge_hideout else {}

    updated_node_hideout['value'] = value
    updated_edge_hideout['value'] = value
    old_val = node_hideout['value']
    previous_center = get_pos_on_value(node_hideout['selected_fdg'], node_hideout['selected_sld'], node_hideout['selected_geo'], old_val)
    new_center = get_pos_on_value(node_hideout['selected_fdg'], node_hideout['selected_sld'], node_hideout['selected_geo'], value)
    the_center = {}
    # the_center['lat'] = center['lat'] + (new_center[0] - previous_center[0])
    # the_center['lng'] = center['lng'] + (new_center[1] - previous_center[1])
    the_center['lat'] = new_center[0]
    the_center['lng'] = new_center[1]
    # txt = html.Pre(
    #     "value="
    #     f"{value:.2f}\n"
    #     "center=" + (json.dumps(center, indent=2) if center else "None")+
    #     "the_center=" + (json.dumps(the_center, indent=2) if the_center else "None")+
    #     "previopus=" + (json.dumps(previous_center, indent=2) if previous_center else "None")+
    #     "new " + (json.dumps(new_center, indent=2) if new_center else "None")
    # )
    return new_opacity, updated_node_hideout, updated_edge_hideout, new_center #html.Pre(txt)

def interpolate(a, b, t):
    return (1 - t) * a + t * b
def get_pos_on_value(fdg, sld, geo, val):
    if val < 0.5:
        return [interpolate(geo[0],fdg[0],2 * val), interpolate(geo[1],fdg[1],2*val)]
    return [interpolate(fdg[0],sld[0],2 * val - 1), interpolate(fdg[1],sld[1],2*val-1)]