from __future__ import annotations
from typing import Optional

import numpy as np
from scipy.optimize import brentq


def _line_coeffs(
    p1: tuple[float, float], p2: tuple[float, float]
) -> tuple[float, float, float]:
    """Return (A, B, C) satisfying A*x + B*y + C = 0 through p1 and p2."""
    A = p2[1] - p1[1]
    B = p1[0] - p2[0]
    C = -(A * p1[0] + B * p1[1])
    return A, B, C


def _intersect(
    L1: tuple[float, float, float],
    L2: tuple[float, float, float],
) -> Optional[tuple[float, float]]:
    """Intersection of two lines given as (A, B, C) coefficients."""
    A1, B1, C1 = L1
    A2, B2, C2 = L2
    D = A1 * B2 - A2 * B1
    if D == 0.0:
        return None  # parallel
    return (B1 * C2 - B2 * C1) / D, (C1 * A2 - C2 * A1) / D


def find_M_and_P(
    pt_E1: tuple[float, float],
    pt_Rn: tuple[float, float],
    pt_En1: tuple[float, float],
    pt_R0: tuple[float, float],
) -> tuple[tuple[float, float], tuple[float, float]]:
    """
    M = intersection of (E1–Rn) and (En1–R0)  [overall material balance point]
    P = intersection of (R0–E1) and (Rn–En1)  [operating point]
    """
    pt_M = _intersect(_line_coeffs(pt_E1, pt_Rn), _line_coeffs(pt_En1, pt_R0))
    pt_P = _intersect(_line_coeffs(pt_R0, pt_E1), _line_coeffs(pt_Rn, pt_En1))
    return pt_M, pt_P


def mixing_point(
    pt_A: tuple[float, float],
    pt_B: tuple[float, float],
    mass_A: float,
    mass_B: float,
) -> tuple[float, float]:
    """Mass-weighted lever-rule mixing point between two streams."""
    total = mass_A + mass_B
    return (
        (mass_A * pt_A[0] + mass_B * pt_B[0]) / total,
        (mass_A * pt_A[1] + mass_B * pt_B[1]) / total,
    )


def find_E1_prime(
    pt_Rn: tuple[float, float],
    pt_Mp: tuple[float, float],
    spline,
) -> Optional[tuple[float, float]]:
    """
    E1' = intersection of the Rn–M' line with the left branch of the
    equilibrium curve.  Returns None if no intersection is found.
    """
    dx = pt_Mp[0] - pt_Rn[0]
    if dx == 0.0:
        return None
    m = (pt_Mp[1] - pt_Rn[1]) / dx
    b = pt_Rn[1] - m * pt_Rn[0]

    def diff(x: float) -> float:
        return float(spline(x)) - (m * x + b)

    x_scan = np.linspace(0.0, min(pt_Rn[0], pt_Mp[0]), 10_000)
    xL = xR = None
    for i in range(len(x_scan) - 1):
        if diff(x_scan[i]) * diff(x_scan[i + 1]) < 0:
            xL, xR = x_scan[i], x_scan[i + 1]
            break

    if xL is None:
        return None
    x_E1p = brentq(diff, xL, xR)
    return (float(x_E1p), float(spline(x_E1p)))
