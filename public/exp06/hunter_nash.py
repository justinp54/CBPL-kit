from __future__ import annotations
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq, minimize_scalar

try:
    from .equilibrium import EquilibriumSystem
    from .conjugate import ConjugateCurve
    from .ternary import xy_to_comp
except ImportError:
    from equilibrium import EquilibriumSystem
    from conjugate import ConjugateCurve
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

    def solve(self) -> tuple[list[Step], int]:
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
                return steps, i
            next_E = self._R_to_E(pt_R)
            if abs(next_E[0] - current_E[0]) + abs(next_E[1] - current_E[1]) < 1e-4:
                break  # solver converged to a fixed point (separation limit reached)
            current_E = next_E

        return steps, len(steps)

    def _E_to_R(
        self, pt_E: tuple[float, float]
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        xE, yE = pt_E
        m1 = -np.sqrt(3)
        line_m1 = lambda x: m1 * (x - xE) + yE

        res = minimize_scalar(
            lambda x: abs(float(self.conjugate.eval(x)) - line_m1(x)),
            bounds=(self.conjugate.x_anchor, self.conjugate.pt_plait[0]),
            method="bounded",
        )
        x_inter = float(res.x)
        y_inter = float(line_m1(x_inter))

        m2 = np.sqrt(3)
        line_m2 = lambda x: m2 * (x - x_inter) + y_inter
        x_pp = self.conjugate.pt_plait[0]
        x_scan = np.linspace(x_pp, 100.0, 2000)
        f_vals = np.array([line_m2(x) - float(self.system.spline(x)) for x in x_scan])
        sc = np.where(f_vals[:-1] * f_vals[1:] < 0)[0]
        if len(sc) > 0:
            xR = brentq(lambda x: line_m2(x) - float(self.system.spline(x)),
                        x_scan[sc[0]], x_scan[sc[0] + 1])
        else:
            xR = float(x_scan[int(np.argmin(np.abs(f_vals)))])
        return (float(xR), float(line_m2(xR))), (x_inter, y_inter)

    def _R_to_E(self, pt_R: tuple[float, float]) -> tuple[float, float]:
        x1, y1 = pt_R
        x2, y2 = self.pt_P
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        x_pp = self.conjugate.pt_plait[0]
        x_scan = np.linspace(0.0, x_pp, 2000)
        f_vals = np.array([(m * x + b) - float(self.system.spline(x)) for x in x_scan])
        sc = np.where(f_vals[:-1] * f_vals[1:] < 0)[0]
        if len(sc) > 0:
            xE = brentq(lambda x: (m * x + b) - float(self.system.spline(x)),
                        x_scan[sc[0]], x_scan[sc[0] + 1])
        else:
            xE = float(x_scan[int(np.argmin(np.abs(f_vals)))])
        return (float(xE), float(m * xE + b))
