from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import PchipInterpolator
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

    def intersect_line(self, slope: float, x0: float, y0: float) -> tuple[float, float]:
        """Intersection of line y = slope*(x-x0)+y0 with the PCHIP conjugate curve."""
        f = self.y_curve - (slope * (self.x_curve - x0) + y0)
        sc = np.where(f[:-1] * f[1:] < 0)[0]
        if len(sc) > 0:
            i = int(sc[0])
            alpha = f[i] / (f[i] - f[i + 1])
            x = float(self.x_curve[i] + alpha * (self.x_curve[i + 1] - self.x_curve[i]))
            y = float(self.y_curve[i] + alpha * (self.y_curve[i + 1] - self.y_curve[i]))
            return x, y
        idx = int(np.argmin(np.abs(f)))
        return float(self.x_curve[idx]), float(self.y_curve[idx])

    def _find_plait_point(self) -> tuple[float, float]:
        x_max = max(p[0] for p in self.aux_points)

        def _try(coefs: np.ndarray, lo: float) -> tuple[float, float] | None:
            def diff(x: float) -> float:
                return float(np.polyval(coefs, x)) - float(self.system.spline(x))
            try:
                x_pp = brentq(diff, lo, 100.0)
                return float(x_pp), float(np.polyval(coefs, x_pp))
            except ValueError:
                return None

        # Try current degree with slightly relaxed lower bound
        for lo in [x_max, x_max * 0.9]:
            result = _try(self._coefs, lo)
            if result:
                return result

        # Fallback: refit with progressively lower degree
        xa, ya = self.aux_points[0]
        x_guide = np.array([p[0] for p in self.aux_points[1:]])
        y_guide = np.array([p[1] for p in self.aux_points[1:]])
        t = np.linspace(0, 1, len(x_guide) + 2)[1:-1]
        x_fit = np.concatenate([[xa], (1 - t) * xa + t * x_guide])
        y_fit = np.concatenate([[ya], (1 - t) * ya + t * y_guide])

        for deg in range(self.degree - 1, 1, -1):
            coefs = np.polyfit(x_fit, y_fit, deg)
            for lo in [x_max, x_max * 0.9]:
                result = _try(coefs, lo)
                if result:
                    self._coefs = coefs
                    self.degree = deg
                    return result

        raise ValueError(
            f"Plait point not found with polynomial degrees {self.degree} down to 2 "
            f"(search range [{x_max:.3f}, 100]). "
            "Check that equilibrium and tie-line data are consistent."
        )

    def _eval_curve(self) -> tuple[np.ndarray, np.ndarray]:
        # Parametric PCHIP by arc length in tie-line order (y is monotone in this order)
        all_pts = self.aux_points + [self.pt_plait]
        xs = np.array([p[0] for p in all_pts])
        ys = np.array([p[1] for p in all_pts])
        ds = np.sqrt(np.diff(xs) ** 2 + np.diff(ys) ** 2)
        t = np.concatenate([[0.0], np.cumsum(ds)])
        t_eval = np.linspace(0.0, t[-1], 2000)
        return (
            np.asarray(PchipInterpolator(t, xs)(t_eval), dtype=float),
            np.asarray(PchipInterpolator(t, ys)(t_eval), dtype=float),
        )
