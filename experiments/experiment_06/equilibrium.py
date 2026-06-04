from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.interpolate import make_interp_spline
from scipy.optimize import brentq, minimize_scalar

try:
    from .config import EQUIL_DATA, MW_PA, RHO_BP, RHO_PA, RHO_W, TIE_DATA
    from .ternary import xy_to_comp
except ImportError:
    from config import EQUIL_DATA, MW_PA, RHO_BP, RHO_PA, RHO_W, TIE_DATA
    from ternary import xy_to_comp


_DEFAULT_LABELS: dict = {
    "solute":  {"name": "Propionic Acid",  "abbr": "PA"},
    "solvent": {"name": "Water",            "abbr": "W"},
    "carrier": {"name": "n-Bromopropane",  "abbr": "BP"},
}


@dataclass
class EquilibriumSystem:
    """Cubic-spline equilibrium curve, tie-line coordinates, and point-lookup helpers."""

    equil_data: np.ndarray = field(default_factory=lambda: EQUIL_DATA.copy())
    tie_data: list[tuple[float, float]] = field(default_factory=lambda: list(TIE_DATA))
    labels: dict = field(default_factory=lambda: {k: dict(v) for k, v in _DEFAULT_LABELS.items()})

    def __post_init__(self) -> None:
        # Cartesian coords from equilibrium data columns [wbp, wpa, ww]
        x_raw = self.equil_data[:, 0] + 0.5 * self.equil_data[:, 1]
        y_raw = np.sqrt(3) / 2.0 * self.equil_data[:, 1]

        # Sort by x so YAML row order doesn't matter
        idx = np.argsort(x_raw)
        self.x_equil: np.ndarray = x_raw[idx]
        self.y_equil: np.ndarray = y_raw[idx]

        # Detect near-duplicate x values that make the spline degenerate
        gaps = np.diff(self.x_equil)
        if np.any(gaps < 0.05):
            bad = int(np.argmin(gaps))
            raise ValueError(
                f"Equilibrium points at rows {idx[bad]} and {idx[bad + 1]} are "
                f"nearly identical in the ternary diagram (Δx = {gaps[bad]:.4f}). "
                "Remove the duplicate point or replace with a more distinct composition."
            )

        self.spline = make_interp_spline(self.x_equil, self.y_equil, k=3)

        x_dense = np.linspace(0.0, 100.0, 10_000)
        y_dense = self.spline(x_dense)
        self.x_smooth: np.ndarray = x_dense
        self.y_smooth: np.ndarray = np.maximum(y_dense, 0.0)

        self.x_intercepts: list[float] = self._find_x_intercepts(x_dense, y_dense)
        # Approximate plait-point x (spline maximum) used to split left/right branches
        self.x_plait_approx: float = float(x_dense[int(np.argmax(y_dense))])
        self.tie_coords: list[tuple[tuple[float, float], tuple[float, float]]] = (
            self._build_tie_coords()
        )

    def _find_x_intercepts(self, x: np.ndarray, y: np.ndarray) -> list[float]:
        roots: list[float] = []
        for i in range(len(x) - 1):
            if y[i] * y[i + 1] < 0:
                root = brentq(self.spline, x[i], x[i + 1])
                roots.append(round(float(root), 3))

        # For systems where data nearly spans [0, 100], the y=0 intercepts may
        # lie just outside the spline range. Try a short extrapolation window;
        # fall back to the data boundary (y is small there anyway).
        def _edge_intercept(x_inner: float, direction: int) -> float:
            x_outer = x_inner + direction * 5.0
            try:
                if float(self.spline(x_inner)) * float(self.spline(x_outer)) < 0:
                    return round(brentq(self.spline, min(x_inner, x_outer),
                                       max(x_inner, x_outer)), 3)
            except Exception:
                pass
            return round(float(x_inner), 3)

        if len(roots) == 0:
            roots = [_edge_intercept(float(self.x_equil[0]),  -1),
                     _edge_intercept(float(self.x_equil[-1]), +1)]
        elif len(roots) == 1 and roots[0] < 50.0:
            roots.append(_edge_intercept(float(self.x_equil[-1]), +1))
        elif len(roots) == 1:
            roots.insert(0, _edge_intercept(float(self.x_equil[0]), -1))
        return roots

    def _build_tie_coords(
        self,
    ) -> list[tuple[tuple[float, float], tuple[float, float]]]:
        def on_curve(wpa_target: float, left: bool) -> tuple[float, float]:
            # Invert the spline: find x on the left or right branch where
            # spline(x) = y_target.  Uses a dense scan so that:
            #   (a) normal tie lines  → sign change found → brentq refines it
            #   (b) near-plait-point → function barely touches zero (no sign
            #       change) → fall back to the minimum-|f| point on the scan.
            y_target = np.sqrt(3) / 2.0 * wpa_target
            lo, hi = (0.0, self.x_plait_approx) if left else (self.x_plait_approx, 100.0)
            x_scan = np.linspace(lo, hi, 5000)
            f_vals = np.array([float(self.spline(x)) - y_target for x in x_scan])

            sign_changes = np.where(f_vals[:-1] * f_vals[1:] < 0)[0]
            if len(sign_changes) > 0:
                i = sign_changes[0]
                x_star = brentq(
                    lambda x: float(self.spline(x)) - y_target,
                    x_scan[i], x_scan[i + 1],
                )
                return float(x_star), float(self.spline(x_star))

            # Touching root (near plait point): accept closest approach
            idx_min = int(np.argmin(np.abs(f_vals)))
            if abs(f_vals[idx_min]) < 0.5:
                x_star = float(x_scan[idx_min])
                return x_star, float(self.spline(x_star))

            side = "left" if left else "right"
            raise ValueError(
                f"Tie-line endpoint not found on {side} branch for "
                f"wSolute = {wpa_target:.3f}%. "
                "Check that all tie-line compositions lie within the two-phase envelope."
            )

        return [
            (on_curve(wpa_left, left=True), on_curve(wpa_right, left=False))
            for wpa_left, wpa_right in self.tie_data
        ]

    def molar_concentration_pa(self, x: float, y: float) -> float:
        """PA molar concentration [mol/L] at a point, assuming volume additivity."""
        wpa, wbp, ww = xy_to_comp(x, y)
        vol_L = (wpa / RHO_PA + wbp / RHO_BP + ww / RHO_W) / 1000.0
        return (wpa / MW_PA) / vol_L

    @classmethod
    def from_yaml(cls, path: str | Path) -> "EquilibriumSystem":
        """Load equilibrium and tie-line data from a system YAML file."""
        import yaml
        from pathlib import Path as _Path
        with open(_Path(path)) as f:
            data = yaml.safe_load(f)
        equil = np.array(data["equilibrium_data"], dtype=float)
        ties = [tuple(float(v) for v in row) for row in data["tie_lines"]]
        comps = data.get("components", {})
        lbs = {
            role: {
                "name": comps.get(role, {}).get("name", _DEFAULT_LABELS[role]["name"]),
                "abbr": comps.get(role, {}).get("abbr", _DEFAULT_LABELS[role]["abbr"]),
            }
            for role in ("solute", "solvent", "carrier")
        }
        return cls(equil_data=equil, tie_data=ties, labels=lbs)

    def find_curve_point_by_concentration(
        self, target_c: float, left: bool
    ) -> tuple[tuple[float, float], tuple[float, float, float], float]:
        """Find the point on the equilibrium curve whose PA concentration equals target_c."""
        bounds = (0.0, self.x_plait_approx) if left else (self.x_plait_approx, 100.0)
        res = minimize_scalar(
            lambda x: abs(
                self.molar_concentration_pa(x, float(self.spline(x))) - target_c
            ),
            bounds=bounds,
            method="bounded",
        )
        x, y = float(res.x), float(self.spline(res.x))
        return (x, y), xy_to_comp(x, y), self.molar_concentration_pa(x, y)
