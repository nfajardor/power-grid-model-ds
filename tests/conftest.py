# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

"""Helper arrays used by various tests."""

import pytest

from power_grid_model_ds._core.model.graphs.models import RustworkxGraphModel
from power_grid_model_ds._core.model.graphs.models.base import BaseGraphModel
from power_grid_model_ds._core.model.grids.base import Grid
from tests.fixtures.arrays import FancyTestArray
from tests.fixtures.grids import build_basic_grid, build_basic_grid_with_three_winding

# pylint: disable=missing-function-docstring

IMPLEMENTED_GRAPH_MODELS: dict[str, type[BaseGraphModel]] = {
    "rustworkx": RustworkxGraphModel,
}


def get_installed_graph_models() -> dict[str, type[BaseGraphModel]]:
    models: dict[str, type[BaseGraphModel]] = {
        model_name: graph_model
        for model_name, graph_model in IMPLEMENTED_GRAPH_MODELS.items()
        if graph_model is not None
    }
    if not models:
        raise ImportError("No graph models are installed")
    return models


def pytest_generate_tests(
    metafunc: pytest.Metafunc,
) -> None:
    """Parametrize the graph fixture"""
    installed_graph_models = get_installed_graph_models()
    if "grid" in metafunc.fixturenames:
        grids = [Grid.empty(graph_model=graph) for graph in installed_graph_models.values()]
        metafunc.parametrize(
            argnames=["grid"],
            argvalues=[[grid] for grid in grids],
            ids=list(installed_graph_models.keys()),
        )

    if "graph" in metafunc.fixturenames:
        metafunc.parametrize(
            argnames=["graph"],
            argvalues=[[graph()] for graph in installed_graph_models.values()],
            ids=list(installed_graph_models.keys()),
        )


@pytest.fixture
def fancy_test_array():
    yield FancyTestArray(
        id=[1, 2, 3],
        test_int=[3, 0, 4],
        test_float=[4.0, 4.0, 1.0],
        test_str=["a", "c", "d"],
        test_bool=[True, False, True],
    )


@pytest.fixture
def basic_grid(grid):
    yield build_basic_grid(grid)


@pytest.fixture
def grid_with_3wt(grid):
    yield build_basic_grid_with_three_winding(grid)
