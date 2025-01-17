# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0
"""This file contains the Grid protocol defining the minimal arrays contained in a grid"""

from typing import Protocol

from power_grid_model_ds._core.model.arrays import (
    BranchArray,
    NodeArray,
    ThreeWindingTransformerArray,
)


class MinimalGridArrays(Protocol):
    """Protocol for the minimal arrays contained in a grid,
    they may be implemented using properties or added as attributes"""

    node: NodeArray
    three_winding_transformer: ThreeWindingTransformerArray
    branches: BranchArray
    branch_arrays: list[BranchArray]
