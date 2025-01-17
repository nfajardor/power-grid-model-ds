# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import numpy as np

from power_grid_model_ds._core.utils.misc import is_sequence

# pylint: disable=missing-function-docstring


def test_list_is_sequence():
    assert is_sequence([])


def test_tuple_is_sequence():
    assert is_sequence(())


def test_array_is_sequenc():
    assert is_sequence(np.array([]))


def test_set_is_sequence():
    assert is_sequence(set())


def test_dict_is_not_a_sequence():
    assert not is_sequence({})


def test_string_is_not_a_sequence():
    assert not is_sequence("abc")
