# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

from dataclasses import dataclass

from power_grid_model_ds._core.model.grids.base import Grid


@dataclass
class ExtendedGrid(Grid):
    """Grid with an extra container"""

    extra_value: int = 123
