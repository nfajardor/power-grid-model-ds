from dash import Input, Output, callback


@callback(
    Output('slider-output-text', 'children'),
    Output('tiles', 'opacity'),
    Output('nodes-geolayer', 'hideout'),
    Output('edges-geolayer', 'hideout'),
    Input('main-slider', 'value')
)
def update_slider_value(value):
    output_text = f"Value is: {value}"

    new_opacity = 1
    if value >= 0.5:
        new_opacity = 3 - 4 * value

    return output_text, new_opacity, {'value': value }, {'value': value }


