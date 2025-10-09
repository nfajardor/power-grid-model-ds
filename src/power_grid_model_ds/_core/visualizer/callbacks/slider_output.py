from dash import Input, Output, callback


@callback(
    Output('slider-output-text', 'children'),
    Output('tiles', 'opacity'),
    Output('nodes-geolayer', 'hideout'),
    Output('edges-geolayer', 'hideout'),
    Input('main-slider', 'value'),
    # Input('nodes-geolayer', 'data'),
    # Input('edges-geolayer', 'data'),
)
def update_slider_value(value):#, nodes, edges):
    output_text = f"Value is: {value}"
    # node_0 = nodes['features'][0]
    # print(f"node: {node_0}")
#     edge_0 = edges['features'][0]
#     print(f"edge: {edge_0}")
    new_opacity = 1
    if value >= 0.5:
        new_opacity = 3 - 4 * value

    return output_text, new_opacity, {'value': value }, {'value': value }


