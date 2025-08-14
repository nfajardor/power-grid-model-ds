from dash import Input, Output, callback


@callback(
    Output('slider-output-text', 'children'),
    Input('main-slider', 'value')
)
def update_slider_value(value):
    output_text = f"Value is: {value}"
    return output_text
