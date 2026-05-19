from __future__ import annotations
import numpy as np


def comp_to_xy(wbp: float, wpa: float) -> tuple[float, float]:
    """Weight percents (wbp, wpa) → internal Cartesian coords used in calculations."""
    x = wbp + 0.5 * wpa
    y = np.sqrt(3) / 2.0 * wpa
    return float(x), float(y)


def xy_to_comp(x: float, y: float) -> tuple[float, float, float]:
    """Internal Cartesian (x, y) → (wpa, wbp, ww) weight percents."""
    wpa = y / np.sqrt(3) * 2.0
    wbp = x - 0.5 * wpa
    ww  = 100.0 - wpa - wbp
    return float(wpa), float(wbp), float(ww)
