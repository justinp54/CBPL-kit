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
    diffs = spline(x_scan) - (m * x_scan + b)
    sign_change = np.where(np.diff(np.sign(diffs)) != 0)[0]
    if len(sign_change) == 0:
        return None
    i = sign_change[0]
    xL, xR = x_scan[i], x_scan[i + 1]
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
    diffs = spline(x_scan) - (m * x_scan + b)
    sign_change = np.where(np.diff(np.sign(diffs)) != 0)[0]
    if len(sign_change) > 0:
        i = sign_change[0]
        x_hit = brentq(diff, x_scan[i], x_scan[i + 1])
        return (float(x_hit), float(spline(x_hit)))
    return None


def find_smax_point(
    system,
    pt_R0: tuple[float, float],
    pt_En1: tuple[float, float],
) -> tuple[float, float] | None:
    """
    M_max: as M moves from F(=R0) toward S(=En1), the extraction stops being
    physically possible once M reaches the equilibrium curve itself (the
    mixture becomes a single phase) — this is that point. None if the F-S
    line never reaches the curve.
    """
    return _line_curve_intersect(pt_R0, pt_En1, system.spline, system.x_domain[0], pt_R0[0])


def find_smax_over_f(
    system,
    pt_R0: tuple[float, float],
    pt_En1: tuple[float, float],
) -> float | None:
    """S_max/F as `frac` (solvent mass share, same as the slider) — see find_smax_point."""
    pt_Mmax = find_smax_point(system, pt_R0, pt_En1)
    if pt_Mmax is None:
        return None
    return _frac_along(pt_R0, pt_En1, pt_Mmax)


def _operating_point_at_frac(
    system,
    pt_R0: tuple[float, float],
    pt_Rn: tuple[float, float],
    pt_En1: tuple[float, float],
    frac: float,
) -> tuple[float, float] | None:
    """The operating point P (a.k.a. the difference point Δ) for a
    hypothetical S:F ratio `frac`: the overall mixing point M(frac) on the
    R0-En1 line determines E1' (via find_E1_prime), and P follows from
    find_M_and_P. P always lies on the fixed Rn-En1 line, regardless of
    frac — only its position along that line moves.
    """
    pt_Mp = mixing_point(pt_R0, pt_En1, mass_A=1 - frac, mass_B=frac)
    pt_E1p = find_E1_prime(pt_Rn, pt_Mp, system.spline)
    if pt_E1p is None:
        return None
    _, pt_P = find_M_and_P(pt_E1p, pt_Rn, pt_En1, pt_R0)
    return pt_P


def find_smin_construction(
    system,
    pt_R0: tuple[float, float],
    pt_Rn: tuple[float, float],
    pt_En1: tuple[float, float],
    n_scan: int = 300,
) -> dict | None:
    """
    S_min/F is the largest `frac` (solvent mass share) at which the
    operating point P(frac) — see _operating_point_at_frac — lands exactly
    on a real measured tie line, extended. Below that ratio, that stage's
    operating step and its equilibrium tie line coincide (zero driving
    force there), so no finite number of stages can pass it.

    P always lies on the fixed Rn-En1 line, so "P(frac) lands on tie line
    i" is just "P(frac)'s position along Rn-En1 equals tie line i's own
    (frac-independent) intersection with Rn-En1" — a 1-D scalar match
    rather than a 2-D one.

    As frac decreases from 1, P(frac)'s position along Rn-En1 doesn't move
    monotonically toward Rn: on real systems it commonly sweeps away from
    En1 (through negative territory, past the pure-solvent corner) long
    before ever approaching Rn from the far side. A tie line living on
    that first (negative) leg of the sweep is encountered — and pinches —
    before any tie line on the far (t>1, beyond Rn) leg ever would, no
    matter how far away it looks on the raw ternary diagram. Earlier
    versions of this function only checked the t>1 leg, which happened to
    work for every system checked at the time (their real tie lines all
    sat on that leg) but wrongly reported "no S_min" for systems whose
    tie lines sit on the negative leg instead (found via w_acoh_dipe).

    So: scan frac from just under 1 down to just above 0, tracking where
    P(frac) sits along Rn-En1, and stop at the first frac (i.e. the
    largest) where that position crosses any real tie line's own position
    on the same line. That's S_min. Large jumps between consecutive scan
    samples are P(frac) sweeping through the point at infinity (a normal
    feature of this parametrization, not a real crossing) and are ignored.

    Returns a dict with every point of that construction (pt_tie_L/R: the
    real tie line that produced the pinch; pt_P_pinch; pt_E1_pinch;
    pt_Mmin; frac_min), for building a reference figure that shows the
    construction itself — or None if no tie line is ever crossed (a
    genuine gap: this system's real tie-line data alone doesn't imply a
    finite-stage limit by this method).
    """
    L_ol = _line_coeffs(pt_En1, pt_Rn)
    tie_t = []
    for pt_L, pt_R in system.tie_coords:
        P = _intersect(_line_coeffs(pt_L, pt_R), L_ol)
        if P is None:
            continue
        tie_t.append((_frac_along(pt_En1, pt_Rn, P), pt_L, pt_R))
    if not tie_t:
        return None

    JUMP = 20.0  # a swing larger than this between adjacent samples is P(frac) crossing infinity, not a real tie-line hit
    fracs = np.linspace(0.999, 0.001, n_scan)
    prev_frac, prev_t = None, None
    frac_hi = frac_lo = None
    winner = None

    for frac in fracs:
        P = _operating_point_at_frac(system, pt_R0, pt_Rn, pt_En1, frac)
        t = _frac_along(pt_En1, pt_Rn, P) if P is not None else None
        if prev_t is not None and t is not None and abs(t - prev_t) < JUMP:
            # Among tie lines whose t_i falls between prev_t and t, the one
            # closest to prev_t is crossed first (t moves monotonically
            # within a pole-free interval).
            candidates = [(t_i, pt_L, pt_R) for t_i, pt_L, pt_R in tie_t
                          if (prev_t - t_i) * (t - t_i) <= 0]
            if candidates:
                t_i, pt_L, pt_R = min(candidates, key=lambda c: abs(c[0] - prev_t))
                winner = (t_i, pt_L, pt_R)
                frac_hi, frac_lo = prev_frac, frac  # prev_frac > frac
                break
        prev_frac, prev_t = frac, t

    if winner is None:
        return None
    t_i, pt_L, pt_R = winner

    def h(frac):
        P = _operating_point_at_frac(system, pt_R0, pt_Rn, pt_En1, frac)
        return (_frac_along(pt_En1, pt_Rn, P) if P is not None else t_i) - t_i

    try:
        frac_min = brentq(h, frac_lo, frac_hi)
    except ValueError:
        frac_min = (frac_lo + frac_hi) / 2

    pt_P_pinch = _operating_point_at_frac(system, pt_R0, pt_Rn, pt_En1, frac_min)
    pt_Mmin = mixing_point(pt_R0, pt_En1, mass_A=1 - frac_min, mass_B=frac_min)
    pt_E1_pinch = find_E1_prime(pt_Rn, pt_Mmin, system.spline)
    if pt_P_pinch is None or pt_E1_pinch is None:
        return None
    return {
        'pt_tie_L': pt_L, 'pt_tie_R': pt_R,
        'pt_P_pinch': pt_P_pinch, 'pt_E1_pinch': pt_E1_pinch, 'pt_Mmin': pt_Mmin,
        'frac_min': frac_min,
    }


def find_smin_over_f(
    system,
    pt_R0: tuple[float, float],
    pt_Rn: tuple[float, float],
    pt_En1: tuple[float, float],
) -> float | None:
    """S_min/F as `frac` (solvent mass share, same as the slider) — see find_smin_construction."""
    c = find_smin_construction(system, pt_R0, pt_Rn, pt_En1)
    if c is None:
        return None
    return c['frac_min']


def _feed_construction_ok(
    system,
    wpa: float,
    pt_Rn: tuple[float, float],
    pt_En1: tuple[float, float],
    mass_R0: float,
    mass_En1: float,
) -> bool:
    """True if the Feed Explorer construction exists for a hypothetical
    binary (carrier + solute, no solvent) feed of `wpa` solute wt% at the
    fixed experimental mass flows: the mixing point M' must yield an E1'
    on the binodal (find_E1_prime) and a finite operating point P. This is
    exactly what the Feed Explorer's slider figure draws, so it is the
    right feasibility test for the slider's own range.
    """
    pt_R0 = (100.0 - 0.5 * wpa, np.sqrt(3) / 2.0 * wpa)
    pt_Mp = mixing_point(pt_R0, pt_En1, mass_A=mass_R0, mass_B=mass_En1)
    pt_E1p = find_E1_prime(pt_Rn, pt_Mp, system.spline)
    if pt_E1p is None:
        return False
    _, pt_P = find_M_and_P(pt_E1p, pt_Rn, pt_En1, pt_R0)
    return pt_P is not None


def find_feed_bounds(
    system,
    pt_Rn: tuple[float, float],
    pt_En1: tuple[float, float],
    mass_R0: float,
    mass_En1: float,
    wpa_anchor: float,
    step: float = 2.0,
    refine_iters: int = 6,
) -> tuple[float, float] | None:
    """Feasible feed-composition span (wpa_lo, wpa_hi) for the Feed
    Explorer slider, probed outward from the experimental feed
    (`wpa_anchor`) until the construction first fails on each side, then
    bisected to ~step/2**refine_iters precision.

    Unlike S_min/S_max there is no named textbook limit for feed
    concentration, and the failure geometry differs between systems, so no
    boundary shape is assumed: walking outward from a known-good anchor
    also keeps the result to the contiguous feasible span containing the
    real experiment, in case feasibility is not contiguous. The dilute end
    is additionally floored just above the raffinate target composition —
    a feed leaner than the target raffinate has nothing to extract.

    Returns None if the anchor itself is infeasible; callers fall back to
    the legacy fixed 10-55 span.
    """
    def ok(w: float) -> bool:
        return _feed_construction_ok(system, w, pt_Rn, pt_En1, mass_R0, mass_En1)

    if not ok(wpa_anchor):
        return None

    # Dilute-side floor: raffinate solute wt% (from its y-coordinate) plus
    # a small margin, never below 0.5 wt%.
    rn_wpa = pt_Rn[1] * 2.0 / np.sqrt(3)
    floor = max(rn_wpa + 0.5, 0.5)
    ceil = 99.5

    # Rich side: walk up until the first failure, then bisect the bracket.
    hi_good, w = wpa_anchor, wpa_anchor + step
    while w < ceil and ok(w):
        hi_good, w = w, w + step
    if w >= ceil:
        hi = ceil if ok(ceil) else hi_good
    else:
        good, bad = hi_good, w
        for _ in range(refine_iters):
            mid = 0.5 * (good + bad)
            if ok(mid):
                good = mid
            else:
                bad = mid
        hi = good

    # Dilute side: walk down until the first failure or the floor.
    lo_good, w = wpa_anchor, wpa_anchor - step
    while w > floor and ok(w):
        lo_good, w = w, w - step
    if w <= floor:
        lo = floor if ok(floor) else lo_good
    else:
        good, bad = lo_good, w
        for _ in range(refine_iters):
            mid = 0.5 * (good + bad)
            if ok(mid):
                good = mid
            else:
                bad = mid
        lo = good

    return (float(lo), float(hi))
