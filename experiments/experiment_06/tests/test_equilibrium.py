"""Smoke tests: every shipped system builds an EquilibriumSystem without error,
and produces structurally sane spline/domain/tie-coordinate outputs.
"""
from __future__ import annotations

import numpy as np
import pytest

from equilibrium import EquilibriumSystem

from _helpers import SYSTEMS_DIR, SYSTEM_IDS


@pytest.fixture(scope="module", params=SYSTEM_IDS)
def eq_system(request):
    path = SYSTEMS_DIR / f"{request.param}.yaml"
    return EquilibriumSystem.from_yaml(path)


def test_from_yaml_builds(eq_system):
    assert isinstance(eq_system, EquilibriumSystem)


def test_domain_ordered_and_in_range(eq_system):
    lo, hi = eq_system.x_domain
    assert lo < hi
    assert 0.0 <= lo <= 100.0
    assert 0.0 <= hi <= 100.0


def test_smooth_curve_nonnegative_and_finite(eq_system):
    assert np.all(np.isfinite(eq_system.x_smooth))
    assert np.all(np.isfinite(eq_system.y_smooth))
    # y clamped at 0 in __post_init__
    assert np.all(eq_system.y_smooth >= 0.0)


def test_plait_approx_within_domain(eq_system):
    lo, hi = eq_system.x_domain
    assert lo <= eq_system.x_plait_approx <= hi


def test_two_x_intercepts(eq_system):
    assert len(eq_system.x_intercepts) == 2
    assert eq_system.x_intercepts[0] < eq_system.x_intercepts[1]


def test_tie_coords_match_input_count(eq_system):
    assert len(eq_system.tie_coords) == len(eq_system.tie_data)
    for (xL, yL), (xR, yR) in eq_system.tie_coords:
        # left endpoint on the solvent-rich (left) branch, right on the other
        assert xL <= eq_system.x_plait_approx + 1e-6
        assert xR >= eq_system.x_plait_approx - 1e-6
        assert all(np.isfinite(v) for v in (xL, yL, xR, yR))


def test_default_constructor_matches_config():
    """Zero-arg constructor uses config.py defaults (the default system)."""
    sysd = EquilibriumSystem()
    assert sysd.equil_data.shape[1] == 3
    assert len(sysd.tie_data) >= 2
