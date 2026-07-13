"""Property tests for the Cartesian <-> ternary coordinate transforms.

comp_to_xy takes (wbp, wpa); xy_to_comp returns (wpa, wbp, ww). Round-tripping
must recover the original weight percents, and ww is fixed by wpa+wbp=100-ww.
"""
from __future__ import annotations

import numpy as np
import pytest

from ternary import comp_to_xy, xy_to_comp

# (wbp, wpa) sample compositions with wbp + wpa <= 100
COMPS = [
    (66.97, 33.03),   # default feed R0
    (5.29, 13.93),    # default E1
    (92.04, 0.18),    # default Rn
    (0.0, 0.0),       # solvent vertex
    (100.0, 0.0),     # carrier vertex
    (0.0, 100.0),     # solute vertex
    (30.0, 40.0),
    (50.0, 25.0),
]


@pytest.mark.parametrize("wbp, wpa", COMPS)
def test_roundtrip_comp_to_xy_to_comp(wbp, wpa):
    x, y = comp_to_xy(wbp, wpa)
    wpa2, wbp2, ww2 = xy_to_comp(x, y)
    assert wpa2 == pytest.approx(wpa, abs=1e-9)
    assert wbp2 == pytest.approx(wbp, abs=1e-9)
    assert ww2 == pytest.approx(100.0 - wpa - wbp, abs=1e-9)


@pytest.mark.parametrize("wbp, wpa", COMPS)
def test_components_sum_to_100(wbp, wpa):
    x, y = comp_to_xy(wbp, wpa)
    wpa2, wbp2, ww2 = xy_to_comp(x, y)
    assert (wpa2 + wbp2 + ww2) == pytest.approx(100.0, abs=1e-9)


@pytest.mark.parametrize("x, y", [
    (50.0, 20.0),
    (10.0, 5.0),
    (75.0, 0.0),
    (0.0, 0.0),
])
def test_roundtrip_xy_to_comp_to_xy(x, y):
    wpa, wbp, ww = xy_to_comp(x, y)
    x2, y2 = comp_to_xy(wbp, wpa)
    assert x2 == pytest.approx(x, abs=1e-9)
    assert y2 == pytest.approx(y, abs=1e-9)


def test_known_geometry():
    # Pure solute (wpa=100) sits at the apex: x=50, y=sqrt(3)/2*100
    x, y = comp_to_xy(0.0, 100.0)
    assert x == pytest.approx(50.0)
    assert y == pytest.approx(np.sqrt(3) / 2.0 * 100.0)
