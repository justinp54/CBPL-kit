"""Smoke tests for the tie-line correlation fits (Othmer-Tobias, Hand,
Bachman) and the log-log plait-point construction, over every shipped system.
"""
from __future__ import annotations

import math

import pytest

from correlation import compute_correlations, compute_plait_loglog
from equilibrium import EquilibriumSystem

from _helpers import SYSTEMS_DIR, SYSTEM_IDS


@pytest.fixture(scope="module", params=SYSTEM_IDS)
def system(request):
    return EquilibriumSystem.from_yaml(SYSTEMS_DIR / f"{request.param}.yaml")


def test_correlations_structure(system):
    res = compute_correlations(system)
    for model in ("ot", "hand", "bachman"):
        fit = res[model]
        assert set(fit) >= {"x", "y", "x_fit", "y_fit", "a", "b", "r2"}
        assert math.isfinite(fit["a"]) and math.isfinite(fit["b"])
        assert -0.0001 <= fit["r2"] <= 1.0001
        assert len(fit["x"]) == len(fit["y"]) == len(system.tie_coords)


def test_selectivity_arrays_aligned(system):
    sel = compute_correlations(system)["selectivity"]
    n = len(system.tie_coords)
    for key in ("w21", "w23", "d1", "d2", "s"):
        assert len(sel[key]) == n


def test_plait_loglog_runs(system):
    res = compute_plait_loglog(system)
    assert "binodal" in res and "tieline" in res
    # plait may be None if no intersection, but when present must be finite
    if res["plait"] is not None:
        assert math.isfinite(res["plait"]["x"])
        assert math.isfinite(res["plait"]["y"])
    if res["plait_comp"] is not None:
        total = sum(res["plait_comp"].values())
        assert total == pytest.approx(100.0, abs=1e-6)
