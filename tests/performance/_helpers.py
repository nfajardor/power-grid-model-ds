# SPDX-FileCopyrightText: Contributors to the Power Grid Model project <powergridmodel@lfenergy.org>
#
# SPDX-License-Identifier: MPL-2.0

import inspect
import timeit
from typing import Generator

from tests.performance._constants import GRAPH_SETUP_CODES, SETUP_CODES


def do_performance_test(code_to_test: str | dict[str, str], array_sizes: list[int], repeats: int):
    """Run the performance test for the given code."""

    print(f"{'-' * 20} {inspect.stack()[1][3]} {'-' * 20}")

    for array_size in array_sizes:
        if isinstance(code_to_test, dict):
            code_to_test_list = [code_to_test[variant].format(array_size=array_size) for variant in SETUP_CODES]
        else:
            code_to_test_list = [code_to_test.format(array_size=array_size)] * len(SETUP_CODES)
        print(f"\n\tArray size: {array_size}\n")
        setup_codes = [setup_code.format(array_size=array_size) for setup_code in SETUP_CODES.values()]
        timings = _get_timings(setup_codes, code_to_test_list, repeats)

        if code_to_test == "pass":
            _print_timings(timings, list(SETUP_CODES.keys()), setup_codes)
        else:
            _print_timings(timings, list(SETUP_CODES.keys()), code_to_test_list)
    print()


def do_graph_test(code_to_test: str | dict[str, str], graph_sizes: list[int], repeats: int):
    """Run the performance test for the given code."""

    print(f"{'-' * 20} {inspect.stack()[1][3]} {'-' * 20}")

    for graph_size in graph_sizes:
        if isinstance(code_to_test, dict):
            code_to_test_list = [code_to_test[variant] for variant in GRAPH_SETUP_CODES]
        else:
            code_to_test_list = [code_to_test] * len(GRAPH_SETUP_CODES)
        print(f"\n\tGraph size: {graph_size}\n")
        setup_codes = [setup_code.format(graph_size=graph_size) for setup_code in GRAPH_SETUP_CODES.values()]
        timings = _get_timings(setup_codes, code_to_test_list, repeats)

        if code_to_test == "pass":
            _print_graph_timings(timings, list(GRAPH_SETUP_CODES.keys()), setup_codes)
        else:
            _print_graph_timings(timings, list(GRAPH_SETUP_CODES.keys()), code_to_test_list)
    print()


def _print_test_code(code: str | dict[str, str], repeats: int):
    print(f"{'-' * 40}")
    if isinstance(code, dict):
        for variant, code_variant in code.items():
            print(f"{variant}")
            print(f"\t{code_variant} (x {repeats})")
        return
    print(f"{code} (x {repeats})")


def _print_graph_timings(timings: Generator, graph_types: list[str], code_list: list[str]):
    for graph_type, timing, code in zip(graph_types, timings, code_list):
        if ";" in code:
            code = code.split(";")[-1]

        code = code.replace("\n", " ").replace("\t", " ")
        code = f"{graph_type}: " + code

        if isinstance(timing, Exception):
            print(f"\t\t{code.ljust(100)} | Not supported")
            continue
        print(f"\t\t{code.ljust(100)} | {sum(timing):.2f}s")


def _print_timings(timings: Generator, array_types: list[str], code_list: list[str]):
    for array, timing, code in zip(array_types, timings, code_list):
        if ";" in code:
            code = code.split(";")[-1]

        code = code.replace("\n", " ").replace("\t", " ")
        array_name = f"{array}_array"
        code = code.replace("input_array", array_name)

        if isinstance(timing, Exception):
            print(f"\t\t{code.ljust(100)} | Not supported")
            continue
        print(f"\t\t{code.ljust(100)} | {sum(timing):.2f}s")


def _get_timings(setup_codes: list[str], test_codes: list[str], repeats: int):
    """Return a generator with the timings for each array type."""
    for setup_code, test_code in zip(setup_codes, test_codes):
        if test_code == "pass":
            yield timeit.repeat(setup_code, number=repeats)
        else:
            try:
                yield timeit.repeat(test_code, setup_code, number=repeats)
            # pylint: disable=broad-exception-caught
            except Exception as error:  # noqa
                yield error
