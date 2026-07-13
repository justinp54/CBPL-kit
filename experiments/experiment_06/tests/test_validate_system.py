"""Exhaustive tests for validate_system.validate() — a pure function returning
a list of human-readable error strings (empty == valid).

Errors are matched by substring / prefix, not exact wording, so message
polish doesn't break the tests while the *which check fired* is still pinned.
"""
from __future__ import annotations

import copy

import pytest

import validate_system
from validate_system import validate

from _helpers import SYSTEM_IDS


def _valid_base() -> dict:
    """A minimal system dict that passes every check."""
    return {
        "components": {
            "carrier": {"name": "Carrier", "abbr": "C"},
            "solute": {"name": "Solute", "abbr": "S"},
            "solvent": {"name": "Solvent", "abbr": "W"},
        },
        "properties": {
            "rho_carrier": 1.35,
            "rho_solute": 0.99,
            "rho_solvent": 1.0,
            "mw_solute": 74.08,
        },
        # sorted by increasing carrier%, each row sums to 100
        "equilibrium_data": [
            [5.0, 10.0, 85.0],
            [20.0, 15.0, 65.0],
            [40.0, 12.0, 48.0],
        ],
        # both columns increasing
        "tie_lines": [
            [6.0, 2.5],
            [9.0, 4.0],
        ],
    }


def test_valid_base_passes():
    assert validate(_valid_base()) == []


# --- Top-level structural errors ---------------------------------------------

@pytest.mark.parametrize("bad_input", [None, [], "not a dict", 42])
def test_non_mapping_rejected(bad_input):
    errors = validate(bad_input)
    assert errors and "YAML mapping" in errors[0]


@pytest.mark.parametrize("missing_key", validate_system._REQUIRED_KEYS)
def test_missing_required_key(missing_key):
    data = _valid_base()
    del data[missing_key]
    errors = validate(data)
    assert any(f"Missing required field: {missing_key}" in e for e in errors)


@pytest.mark.parametrize("null_key", validate_system._REQUIRED_KEYS)
def test_none_required_key(null_key):
    data = _valid_base()
    data[null_key] = None
    errors = validate(data)
    assert any(f"Missing required field: {null_key}" in e for e in errors)


# --- properties errors -------------------------------------------------------

@pytest.mark.parametrize("prop", validate_system._REQUIRED_PROPS)
def test_missing_property(prop):
    data = _valid_base()
    del data["properties"][prop]
    errors = validate(data)
    assert any(f"properties must include {prop}" in e for e in errors)


@pytest.mark.parametrize("prop", validate_system._REQUIRED_PROPS)
def test_empty_property(prop):
    data = _valid_base()
    data["properties"][prop] = ""
    errors = validate(data)
    assert any(f"properties must include {prop}" in e for e in errors)


@pytest.mark.parametrize("prop", validate_system._REQUIRED_PROPS)
def test_non_numeric_property(prop):
    data = _valid_base()
    data["properties"][prop] = "abc"
    errors = validate(data)
    assert any(f"properties.{prop} must be a number" in e for e in errors)


# --- equilibrium_data errors -------------------------------------------------

@pytest.mark.parametrize("rows", [
    [],
    [[5.0, 10.0, 85.0]],
    [[5.0, 10.0, 85.0], [20.0, 15.0, 65.0]],
    "not a list",
])
def test_equilibrium_too_few_rows(rows):
    data = _valid_base()
    data["equilibrium_data"] = rows
    errors = validate(data)
    assert any("at least 3 rows" in e for e in errors)


@pytest.mark.parametrize("bad_row", [
    [5.0, 10.0],          # too short
    [5.0, 10.0, 85.0, 0.0],  # too long
    [5.0, "x", 85.0],     # non-numeric
])
def test_equilibrium_row_shape(bad_row):
    data = _valid_base()
    data["equilibrium_data"][1] = bad_row
    errors = validate(data)
    assert any("3 numeric values" in e for e in errors)


def test_equilibrium_row_sum_off():
    data = _valid_base()
    data["equilibrium_data"][1] = [20.0, 15.0, 80.0]  # sums to 115
    errors = validate(data)
    assert any("not 100%" in e for e in errors)


def test_equilibrium_sum_within_tolerance_passes():
    data = _valid_base()
    data["equilibrium_data"][1] = [20.0, 15.0, 65.3]  # 100.3, within 0.5
    assert validate(data) == []


def test_equilibrium_not_sorted_gets_sort_prefix():
    data = _valid_base()
    data["equilibrium_data"] = [
        [40.0, 12.0, 48.0],
        [5.0, 10.0, 85.0],
        [20.0, 15.0, 65.0],
    ]
    errors = validate(data)
    assert any(e.startswith("SORT:") for e in errors)


# --- tie_lines errors --------------------------------------------------------

@pytest.mark.parametrize("rows", [
    [],
    [[6.0, 2.5]],
    "not a list",
])
def test_tie_lines_too_few_rows(rows):
    data = _valid_base()
    data["tie_lines"] = rows
    errors = validate(data)
    assert any("at least 2 rows" in e for e in errors)


@pytest.mark.parametrize("bad_row", [
    [6.0],                # too short
    [6.0, 2.5, 1.0],      # too long
    [6.0, "y"],           # non-numeric
])
def test_tie_lines_row_shape(bad_row):
    data = _valid_base()
    data["tie_lines"][1] = bad_row
    errors = validate(data)
    assert any("2 numeric values" in e for e in errors)


@pytest.mark.parametrize("rows", [
    [[9.0, 4.0], [6.0, 5.0]],   # column 0 decreases
    [[6.0, 4.0], [9.0, 2.5]],   # column 1 decreases
])
def test_tie_lines_not_monotonic(rows):
    data = _valid_base()
    data["tie_lines"] = rows
    errors = validate(data)
    assert any("both increasing" in e for e in errors)


# --- Real shipped systems all pass -------------------------------------------

@pytest.mark.parametrize("system_id", SYSTEM_IDS)
def test_shipped_system_valid(loaded_systems, system_id):
    errors = validate(loaded_systems[system_id])
    assert errors == [], f"{system_id}: {errors}"
