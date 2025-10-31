from dash import Input, Output, callback, State
from enum import IntEnum


class NodeDropdownOptions(IntEnum):
    ACTIVE_POWER    = 0
    REACTIVE_POWER  = 1


class EdgeDropdownOptions(IntEnum):
    RESISTANCE  = 0
    REACTANCE   = 1
    CAPACITANCE = 2
    LOSS_FACTOR = 3
    CURRENT     = 4


@callback(
    Output('nodes-geolayer', 'hideout', allow_duplicate=True),
    Input('node_dropdown', 'value'),
    State('nodes-geolayer', 'hideout'),
    prevent_initial_call=True
)
def update_node_dropdown(value, hideout):
    updated_hideout = hideout.copy() if hideout else {}
    updated_hideout['current_property'] = value
    return updated_hideout


@callback(
    Output('edges-geolayer', 'hideout', allow_duplicate=True),
    Input('edge_dropdown', 'value'),
    State('edges-geolayer', 'hideout'),
    prevent_initial_call=True
)
def update_edge_dropdown(value, hideout):
    updated_hideout = hideout.copy() if hideout else {}
    updated_hideout['current_property'] = value
    return updated_hideout
