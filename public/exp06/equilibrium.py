from __future__ import annotations
from dataclasses import dataclass, field

import numpy as np
from scipy.interpolate import make_interp_spline
from scipy.optimize import brentq, minimize_scalar

try:
    from .config import EQUIL_DATA, TIE_DATA, RHO_BP, RHO_PA, RHO_W, MW_PA
    from .ternary import xy_to_comp
except ImportError:
    from config import EQUIL_DATA, TIE_DATA, RHO_BP, RHO_PA, RHO_W, MW_PA
    from ternary import xy_to_comp


@dataclass
class EquilibriumSystem:
    """Cubic-spline equilibrium curve, tie-line coordinates, and point-lookup helpers."""

    equil_data: np.ndarray = field(default_factory=lambda: EQUIL_DATA.copy())
    tie_data: list[tuple[float, float]] = field(default_factory=lambda: list(TIE_DATA))

    def __post_init__(self) -> None:
        # Cartesian coords from equilibrium data columns [wbp, wpa, ww]
        self.x_equil: np.ndarray = self.equil_data[:, 0] + 0.5 * self.equil_data[:, 1]
        self.y_equil: np.ndarray = np.sqrt(3) / 2.0 * self.equil_data[:, 1]

        self.spline = make_interp_spline(self.x_equil, self.y_equil, k=3)

        x_dense = np.linspace(0.0, 100.0, 10_000)
        y_dense = self.spline(x_dense)
        self.x_smooth: np.ndarray = x_dense
        self.y_smooth: np.ndarray = np.maximum(y_dense, 0.0)

        self.x_intercepts: list[float] = self._find_x_intercepts(x_dense, y_dense)
        self.tie_coords: list[tuple[tuple[float, float], tuple[float, float]]] = (
            self._build_tie_coords()
        )

    def _find_x_intercepts(self, x: np.ndarray, y: np.ndarray) -> list[float]:
        roots: list[float] = []
        for i in range(len(x) - 1):
            if y[i] * y[i + 1] < 0:
                root = brentq(self.spline, x[i], x[i + 1])
                roots.append(round(float(root), 3))
        return roots

    def _build_tie_coords(
        self,
    ) -> list[tuple[tuple[float, float], tuple[float, float]]]:
        def on_curve(wpa_target: float, left: bool) -> tuple[float, float]:
            # wpa determines y directly: y = (√3/2)·wpa
            # Invert the spline: find x s.t. spline(x) = y_target
            y_target = np.sqrt(3) / 2.0 * wpa_target
            lo, hi = (0.0, 50.0) if left else (50.0, 100.0)
            x = brentq(lambda x: float(self.spline(x)) - y_target, lo, hi)
            return float(x), float(self.spline(x))

        return [
            (on_curve(wpa_left, left=True), on_curve(wpa_right, left=False))
            for wpa_left, wpa_right in self.tie_data
        ]

    def molar_concentration_pa(self, x: float, y: float) -> float:
        """PA molar concentration [mol/L] at a point, assuming volume additivity."""
        wpa, wbp, ww = xy_to_comp(x, y)
        vol_L = (wpa / RHO_PA + wbp / RHO_BP + ww / RHO_W) / 1000.0
        return (wpa / MW_PA) / vol_L

    def find_curve_point_by_concentration(
        self, target_c: float, left: bool
    ) -> tuple[tuple[float, float], tuple[float, float, float], float]:
        """Find the point on the equilibrium curve whose PA concentration equals target_c."""
        bounds = (0.0, 50.0) if left else (50.0, 100.0)
        res = minimize_scalar(
            lambda x: abs(
                self.molar_concentration_pa(x, float(self.spline(x))) - target_c
            ),
            bounds=bounds,
            method="bounded",
        )
        x, y = float(res.x), float(self.spline(res.x))
        return (x, y), xy_to_comp(x, y), self.molar_concentration_pa(x, y)
