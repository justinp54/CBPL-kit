from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq

try:
    from .conjugate import ConjugateCurve
    from .equilibrium import EquilibriumSystem
    from .ternary import xy_to_comp
except ImportError:
    from conjugate import ConjugateCurve
    from equilibrium import EquilibriumSystem
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
        steps: list[Step] = []
        current_E = self.pt_E1
        y_Rn = self.pt_Rn[1]

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
