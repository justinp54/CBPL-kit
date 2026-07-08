from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq

try:
    from .conjugate import ConjugateCurve
    from .equilibrium import EquilibriumSystem
    from .lever_rule import find_M_and_P, find_E1_prime, mixing_point
    from .ternary import xy_to_comp
except ImportError:
    from conjugate import ConjugateCurve
    from equilibrium import EquilibriumSystem
    from lever_rule import find_M_and_P, find_E1_prime, mixing_point
    from ternary import xy_to_comp


@dataclass
class Step:
    index: int
    pt_E: tuple[float, float]       # extract point (on left branch)
    pt_inter: tuple[float, float]   # auxiliary intersection on conjugate curve
    pt_R: tuple[float, float]       # raffinate point (on right branch)
    comp_E: tuple[float, float, float]  # (wpa, wbp, ww)
    comp_R: tuple[float, float, float]


@dataclass
class HunterNashSolver:
    """
    Graphical Hunter-Nash stepping algorithm for LLE stage counting.

    Each stage:
      E → R: draw auxiliary line (slope -√3) from E_k, intersect conjugate curve,
             then draw line (slope +√3) to right equilibrium branch → R_k.
      R → E: draw line from R_k through operating point P to left equilibrium branch → E_{k+1}.
    Stops when R_k.y < Rn.y (raffinate target reached).
    """

    system: EquilibriumSystem
    conjugate: ConjugateCurve
    pt_P: tuple[float, float]
    pt_E1: tuple[float, float]
    pt_Rn: tuple[float, float]
    max_steps: int = 50

    def solve(self) -> tuple[list[Step], float]:
        """Sets self.status to one of:
        - 'converged':  R_k actually reached Rn (the normal, expected case)
        - 'stalled':    consecutive E points stopped moving before reaching
                         Rn — the construction found a fixed point unrelated
                         to the target, not a slow approach to it. Distinct
                         from 'converged' because len(steps) alone can't
                         tell them apart (found via the S:F Explorer's S_min
                         preview: a hypothetical operating point can produce
                         a Step sequence that climbs steadily away from Rn
                         for dozens of stages before stalling, which looks
                         superficially like "just needs more stages" if you
                         only look at the count).
        - 'max_steps':  ran out of max_steps still actively moving toward
                         Rn (genuinely still converging, just slowly).
        """
        steps: list[Step] = []
        current_E = self.pt_E1
        y_Rn = self.pt_Rn[1]
        self.status = 'max_steps'

        for i in range(1, self.max_steps + 1):
            pt_R, pt_inter = self._E_to_R(current_E)
            steps.append(Step(
                index=i,
                pt_E=current_E,
                pt_inter=pt_inter,
                pt_R=pt_R,
                comp_E=xy_to_comp(*current_E),
                comp_R=xy_to_comp(*pt_R),
            ))
            if pt_R[1] <= y_Rn + 1e-6:
                self.status = 'converged'
                if len(steps) >= 2:
                    y_prev = steps[-2].pt_R[1]
                    y_curr = pt_R[1]
                    denom = y_prev - y_curr
                    frac = (y_prev - y_Rn) / denom if denom > 1e-9 else 1.0
                    return steps, float(i - 1) + frac
                return steps, float(i)
            next_E = self._R_to_E(pt_R)
            if abs(next_E[0] - current_E[0]) + abs(next_E[1] - current_E[1]) < 0.05:
                # Separation limit: last step barely advances — exclude it
                if len(steps) > 1:
                    steps = steps[:-1]
                self.status = 'stalled'
                break
            current_E = next_E

        return steps, float(len(steps))

    def _find_on_spline(self, line, lo: float, hi: float, tol: float = 0.5) -> float:
        """x in [lo, hi] where line(x) == system.spline(x). Each equilibrium
        branch is monotone (EquilibriumSystem._hermite_branch), so checking
        the two endpoints is enough: opposite signs -> brentq; same sign ->
        accept the nearer endpoint if it's a close miss (line/point just
        outside our modeled two-phase envelope), otherwise this stage's
        construction doesn't intersect the curve at all and that should be
        surfaced, not guessed at by extrapolating past the real data.
        """
        spline = self.system.spline
        f_lo, f_hi = line(lo) - float(spline(lo)), line(hi) - float(spline(hi))
        if f_lo * f_hi < 0:
            return brentq(lambda x: line(x) - float(spline(x)), lo, hi)
        x_star, f_star = (lo, f_lo) if abs(f_lo) < abs(f_hi) else (hi, f_hi)
        if abs(f_star) < tol:
            return x_star
        raise ValueError(
            f"Hunter-Nash step found no intersection with the equilibrium "
            f"curve in [{lo:.2f}, {hi:.2f}] (closest miss: {abs(f_star):.3f}). "
            "Check that P/E1/Rn are consistent with this system's equilibrium data."
        )

    def _E_to_R(
        self, pt_E: tuple[float, float]
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        xE, yE = pt_E
        m1 = -np.sqrt(3)
        x_inter, y_inter = self.conjugate.intersect_line(m1, xE, yE)

        m2 = np.sqrt(3)
        line_m2 = lambda x: m2 * (x - x_inter) + y_inter
        xR = self._find_on_spline(line_m2, self.conjugate.pt_plait[0], self.system.x_domain[1])
        return (float(xR), float(line_m2(xR))), (x_inter, y_inter)

    def _R_to_E(self, pt_R: tuple[float, float]) -> tuple[float, float]:
        x1, y1 = pt_R
        x2, y2 = self.pt_P
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        line = lambda x: m * x + b
        xE = self._find_on_spline(line, self.system.x_domain[0], self.conjugate.pt_plait[0])
        return (float(xE), float(line(xE)))


def stage_count_trend(
    system: EquilibriumSystem,
    conjugate: ConjugateCurve,
    pt_R0: tuple[float, float],
    pt_Rn: tuple[float, float],
    pt_En1: tuple[float, float],
    frac_min: float,
    frac_max: float,
    n: int = 7,
    max_steps: int = 100,
) -> list[tuple[float, float]]:
    """Stage count vs S:F ratio (`frac`), sampled from frac_max down toward
    frac_min, for the S:F Explorer's S_min reference.

    Sampled points near frac_max (close to the single-phase limit) can fail
    for reasons unrelated to S_min — an unrelated edge case, skipped rather
    than treated as "reached the S_min boundary". Once a real descending
    trend has started, though, the first failure marks the edge of what can
    be reliably computed and ends the trend there: every returned point is
    a genuine, unambiguous stage count, never a guess near the
    stalled/still-converging boundary (see fig_sf_smin_reference's
    docstring for why that boundary itself is avoided).
    """
    points: list[tuple[float, float]] = []
    for t in np.linspace(0.9, 0.05, n):
        frac = frac_min + t * (frac_max - frac_min)
        pt_Mp = mixing_point(pt_R0, pt_En1, mass_A=1 - frac, mass_B=frac)
        pt_E1p = find_E1_prime(pt_Rn, pt_Mp, system.spline)
        if pt_E1p is None:
            if points:
                break
            continue
        _, pt_Pp = find_M_and_P(pt_E1p, pt_Rn, pt_En1, pt_R0)
        if pt_Pp is None:
            if points:
                break
            continue
        solver = HunterNashSolver(system, conjugate, pt_Pp, pt_E1p, pt_Rn, max_steps=max_steps)
        try:
            _, N = solver.solve()
        except ValueError:
            if points:
                break
            continue
        if solver.status != 'converged':
            if points:
                break
            continue
        points.append((float(frac), N))
    return points
