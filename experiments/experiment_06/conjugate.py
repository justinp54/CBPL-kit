from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq

try:
    from .equilibrium import EquilibriumSystem
except ImportError:
    from equilibrium import EquilibriumSystem


@dataclass
class ConjugateCurve:
    """
    Polynomial conjugate curve from auxiliary-line intersections and plait-point finder.

    Method (Treybal, Mass Transfer Operations):
    1. For each tie line, draw auxiliary lines with slopes ±√3 from each endpoint.
    2. Their intersection gives one point on the conjugate curve.
    3. Fit a degree-N polynomial; intersect with equilibrium curve to find the plait point.
    """

    system: EquilibriumSystem
    degree: int = 4

    def __post_init__(self) -> None:
        self.aux_points: list[tuple[float, float]] = self._build_aux_points()
        self.x_anchor: float = self.aux_points[0][0]
        self._coefs: np.ndarray = self._fit_polynomial()
        self.pt_plait: tuple[float, float] = self._find_plait_point()
        self.x_curve: np.ndarray
        self.y_curve: np.ndarray
        self.x_curve, self.y_curve = self._eval_curve()

    def _build_aux_points(self) -> list[tuple[float, float]]:
        m1, m2 = -np.sqrt(3), np.sqrt(3)
        # Baseline intercepts serve as the first (degenerate) "tie line"
        ic = self.system.x_intercepts
        tie_aug = [((ic[0], 0.0), (ic[1], 0.0))] + self.system.tie_coords

        points: list[tuple[float, float]] = []
        for (xL, yL), (xR, yR) in tie_aug:
            # Solve: m1*(x-xL)+yL = m2*(x-xR)+yR
            x_int = (m1 * xL - m2 * xR + yR - yL) / (m1 - m2)
            points.append((float(x_int), float(m1 * (x_int - xL) + yL)))
        return points

    def _fit_polynomial(self) -> np.ndarray:
        xa, ya = self.aux_points[0]
        x_guide = np.array([p[0] for p in self.aux_points[1:]])
        y_guide = np.array([p[1] for p in self.aux_points[1:]])
        t = np.linspace(0, 1, len(x_guide) + 2)[1:-1]
        x_fit = np.concatenate([[xa], (1 - t) * xa + t * x_guide])
        y_fit = np.concatenate([[ya], (1 - t) * ya + t * y_guide])
        return np.polyfit(x_fit, y_fit, self.degree)

    def eval(self, x: float | np.ndarray) -> np.ndarray:
        return np.polyval(self._coefs, x)

    def _find_plait_point(self) -> tuple[float, float]:
        x_max = max(p[0] for p in self.aux_points)

        def diff(x: float) -> float:
            return float(self.eval(x)) - float(self.system.spline(x))

        try:
            x_pp = brentq(diff, x_max, 100.0)
            return (float(x_pp), float(self.eval(x_pp)))
        except ValueError as exc:
            raise ValueError(
                f"Plait point not found: the degree-{self.degree} conjugate polynomial does "
                f"not intersect the equilibrium curve in [{x_max:.3f}, 100]. "
                "Check tie-line data or try a different polynomial degree."
            ) from exc

    def _eval_curve(self) -> tuple[np.ndarray, np.ndarray]:
        x_min = min(p[0] for p in self.aux_points)
        x_eval = np.linspace(x_min, self.pt_plait[0], 2000)
        return x_eval, np.asarray(self.eval(x_eval), dtype=float)
