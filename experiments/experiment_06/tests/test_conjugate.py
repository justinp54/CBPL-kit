"""Smoke tests: every shipped system builds a ConjugateCurve, finds a plait
point without error, and lands it at a physically plausible composition
(each component 0-100 wt%, summing to ~100).
"""
from __future__ import annotations

import numpy as np
import pytest

from conjugate import ConjugateCurve
from equilibrium import EquilibriumSystem
from ternary import xy_to_comp

from _helpers import SYSTEMS_DIR, SYSTEM_IDS


@pytest.fixture(scope="module", params=SYSTEM_IDS)
def conj(request):
    system = EquilibriumSystem.from_yaml(SYSTEMS_DIR / f"{request.param}.yaml")
    return ConjugateCurve(system)


def test_builds_without_error(conj):
    assert isinstance(conj, ConjugateCurve)


def test_curve_arrays_finite_and_aligned(conj):
    assert len(conj.x_curve) == len(conj.y_curve)
    assert len(conj.x_curve) > 0
    assert np.all(np.isfinite(conj.x_curve))
    assert np.all(np.isfinite(conj.y_curve))


def test_plait_point_finite(conj):
    x, y = conj.pt_plait
    assert np.isfinite(x) and np.isfinite(y)


def test_plait_point_composition_plausible(conj):
    wpa, wbp, ww = xy_to_comp(*conj.pt_plait)
    # Cartesian y >= 0 always; solute fraction can't be negative there.
    assert wpa >= -0.5
    # Compositions should sum to 100 (xy_to_comp guarantees this analytically).
    assert abs((wpa + wbp + ww) - 100.0) < 1e-6
    # Plait point of a real system sits well inside the triangle.
    assert -1.0 <= wpa <= 100.0
    assert -1.0 <= wbp <= 101.0
    assert -1.0 <= ww <= 101.0


def test_horizontal_method_also_builds(conj):
    """The 'horizontal' aux-line variant should also complete for every
    system (exercises the excursion-minimizing branch selection)."""
    alt = ConjugateCurve(conj.system, method="horizontal")
    assert alt.horizontal_side in ("left", "right")
    x, y = alt.pt_plait
    assert np.isfinite(x) and np.isfinite(y)
