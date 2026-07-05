from __future__ import annotations

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
) -> tuple[float, float] | None:
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
) -> tuple[float, float] | None:
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


def _frac_along(pt_F: tuple[float, float], pt_S: tuple[float, float], pt_M: tuple[float, float]) -> float:
    """Where pt_M sits on the F->S line, as the fraction _dynamic()/mixing_point()
    already calls `frac` (solvent's mass share of the F+S mixture): 0 at F, 1 at S.
    """
    vx, vy = pt_S[0] - pt_F[0], pt_S[1] - pt_F[1]
    wx, wy = pt_M[0] - pt_F[0], pt_M[1] - pt_F[1]
    denom = vx * vx + vy * vy
    return (wx * vx + wy * vy) / denom if denom else 0.0


def _line_curve_intersect(
    pt_A: tuple[float, float],
    pt_B: tuple[float, float],
    spline,
    x_lo: float,
    x_hi: float,
    n: int = 10_000,
) -> tuple[float, float] | None:
    """First intersection of the line through pt_A/pt_B with `spline`,
    scanned over [x_lo, x_hi] explicitly (unlike find_E1_prime, which infers
    its scan range from Rn/M' and breaks if either point sits at x≈0 — as
    En1, fixed at the pure-solvent corner (0, 0), always does).
    """
    dx = pt_B[0] - pt_A[0]
    if dx == 0.0:
        return None
    m = (pt_B[1] - pt_A[1]) / dx
    b = pt_A[1] - m * pt_A[0]

    def diff(x: float) -> float:
        return float(spline(x)) - (m * x + b)

    lo, hi = sorted((x_lo, x_hi))
    x_scan = np.linspace(lo, hi, n)
    for i in range(len(x_scan) - 1):
        if diff(x_scan[i]) * diff(x_scan[i + 1]) < 0:
            x_hit = brentq(diff, x_scan[i], x_scan[i + 1])
            return (float(x_hit), float(spline(x_hit)))
    return None


def find_smax_over_f(
    system,
    pt_R0: tuple[float, float],
    pt_En1: tuple[float, float],
) -> float | None:
    """
    S_max/F: as M moves from F(=R0) toward S(=En1), the extraction stops
    being physically possible once M reaches the equilibrium curve itself
    (the mixture becomes a single phase). Returns frac_max — the same
    `frac` (solvent mass share) the slider already uses — or None if the
    F-S line never reaches the curve.
    """
    pt_Mmax = _line_curve_intersect(pt_R0, pt_En1, system.spline, system.x_domain[0], pt_R0[0])
    if pt_Mmax is None:
        return None
    return _frac_along(pt_R0, pt_En1, pt_Mmax)


def find_smin_over_f(
    system,
    pt_R0: tuple[float, float],
    pt_Rn: tuple[float, float],
    pt_En1: tuple[float, float],
) -> float | None:
    """
    S_min/F: the solvent ratio below which no finite number of stages can
    reach Rn (a "pinch" — an operating tie line coincides with the curve).

    Graphical method (Treybal): extend the operating line OL (En1-Rn) and
    every real tie line; among the intersections that fall beyond Rn (away
    from En1) on OL, the one farthest from Rn is the pinch point P_min.
    Extending F-P_min to the extract branch gives the pinch E1, from which
    M_min (and so S_min/F, as `frac`) follows the same way S_max/F does.

    Returns None if no tie line pinches on the raffinate side (e.g. a
    strongly solutropic system, where the textbook method needs the
    extract-side check too — not handled here, treated as a known gap).
    """
    L_ol = _line_coeffs(pt_En1, pt_Rn)
    best_t, best_P = -np.inf, None
    for pt_L, pt_R in system.tie_coords:
        P = _intersect(_line_coeffs(pt_L, pt_R), L_ol)
        if P is None:
            continue
        t = _frac_along(pt_En1, pt_Rn, P)  # 0 at En1, 1 at Rn
        if t > 1.0 and t > best_t:
            best_t, best_P = t, P

    if best_P is None:
        return None

    pt_E1_pinch = _line_curve_intersect(pt_R0, best_P, system.spline, system.x_domain[0], pt_R0[0])
    if pt_E1_pinch is None:
        return None
    pt_Mmin, _ = find_M_and_P(pt_E1_pinch, pt_Rn, pt_En1, pt_R0)
    return _frac_along(pt_R0, pt_En1, pt_Mmin)
