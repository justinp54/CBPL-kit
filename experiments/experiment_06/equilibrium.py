from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.interpolate import CubicHermiteSpline, PchipInterpolator
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


class _BranchSpline:
    """Callable combining two Hermite branches, split and rejoined at x_peak.

    Both branches share the peak knot with an explicit zero derivative
    there (see EquilibriumSystem._build_spline), so this reads as one
    seamless curve even though it's built from two pieces.
    """

    def __init__(self, left: CubicHermiteSpline, right: CubicHermiteSpline, x_peak: float) -> None:
        self.left = left
        self.right = right
        self.x_peak = x_peak

    def __call__(self, x):
        x_arr = np.atleast_1d(np.asarray(x, dtype=float))
        out = np.where(x_arr <= self.x_peak, self.left(x_arr), self.right(x_arr))
        return float(out[0]) if np.ndim(x) == 0 else out


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

        # Add axis-intercept anchors (y=0) on each side. If the given data
        # already reaches the axis (wpa≈0) there, that real point is used
        # directly; otherwise one is estimated from a shape-preserving edge
        # slope and inserted. This prevents the cubic spline from curling
        # outside the data range, which would create false roots during
        # tie-line inversion and a visually incorrect equilibrium curve.
        n = len(self.x_equil)
        k = min(3, n)
        _xl = self._axis_anchor(self.x_equil[:k], self.y_equil[:k])
        _xr = self._axis_anchor(self.x_equil[::-1][:k], self.y_equil[::-1][:k])

        x_parts = [self.x_equil]
        y_parts = [self.y_equil]
        if _xl is not None:
            x_parts.insert(0, np.array([_xl]))
            y_parts.insert(0, np.array([0.0]))
        if _xr is not None:
            x_parts.append(np.array([_xr]))
            y_parts.append(np.array([0.0]))
        _x_fit = np.concatenate(x_parts)
        _y_fit = np.concatenate(y_parts)

        # Split at the highest point (the plait-point side of the curve) and
        # fit each side as its own monotone Hermite branch, instead of one
        # global cubic spline through everything. A single k=3 spline
        # enforces curvature continuity across all knots at once, so an
        # unevenly spaced knot anywhere can make it oscillate far from that
        # spot; two independent monotone branches can't overshoot past their
        # own data no matter how uneven the spacing is elsewhere.
        i_peak = int(np.argmax(_y_fit))
        left_end, x_peak, y_peak = self._fitted_peak(_x_fit, _y_fit, i_peak)
        self.x_plait_approx: float = x_peak
        self.spline = self._build_spline(_x_fit, _y_fit, left_end, x_peak, y_peak)

        # True support of the curve: real data boundary, or the synthesized
        # anchor when one was inserted. The spline is never sampled/searched
        # outside this range, so it can't extrapolate/curl unnoticed.
        self.x_domain: tuple[float, float] = (
            _xl if _xl is not None else float(self.x_equil[0]),
            _xr if _xr is not None else float(self.x_equil[-1]),
        )

        x_dense = np.linspace(self.x_domain[0], self.x_domain[1], 10_000)
        y_dense = self.spline(x_dense)
        self.x_smooth: np.ndarray = x_dense
        self.y_smooth: np.ndarray = np.maximum(y_dense, 0.0)

        self.x_intercepts: list[float] = self._find_x_intercepts(x_dense, y_dense)
        self.tie_coords: list[tuple[tuple[float, float], tuple[float, float]]] = (
            self._build_tie_coords()
        )

    @staticmethod
    def _fitted_peak(x: np.ndarray, y: np.ndarray, i_peak: int) -> tuple[int, float, float]:
        """Refine the peak with a local parabola through the max and its two
        neighbors. Sparse data can have two near-tied points straddling the
        true extremum (e.g. y=42.78 then y=42.51 fifteen x-units apart);
        splitting exactly at whichever one happens to be marginally higher
        flattens what should be a single rounded apex. A 3-point local fit
        recovers that rounding without the unbounded overshoot risk of a
        global spline (see _build_spline's docstring).

        Returns (left_end, x_peak, y_peak): left_end is the index of the
        last real point belonging to the left branch (x[i_peak] itself if
        the vertex lands to its right, x[i_peak - 1] if the vertex lands
        to its left — the fit isn't guaranteed to lean either way).
        """
        n = len(x)
        if i_peak == 0 or i_peak == n - 1:
            return i_peak, float(x[i_peak]), float(y[i_peak])

        # Only correct when the raw peak is a near-tie with (at least) one
        # neighbor — the case this refinement exists for. When the peak is
        # decisively higher than both neighbors, the 3-point parabola's
        # vertex can land above the highest sampled point (its symmetric-
        # curvature assumption doesn't hold for a skewed real peak), which
        # is never physically justified: the true curve can't be verified
        # to exceed the highest point actually measured.
        _NEAR_TIE_TOL = 1.0  # wt%
        min_gap = min(y[i_peak] - y[i_peak - 1], y[i_peak] - y[i_peak + 1])
        if min_gap >= _NEAR_TIE_TOL:
            return i_peak, float(x[i_peak]), float(y[i_peak])

        xs, ys = x[i_peak - 1 : i_peak + 2], y[i_peak - 1 : i_peak + 2]
        a, b, c = np.polyfit(xs, ys, 2)
        fallback = (i_peak, float(x[i_peak]), float(y[i_peak]))
        if abs(a) < 1e-12:
            return fallback
        x_v = -b / (2 * a)
        if xs[0] < x_v < xs[1]:
            left_end = i_peak - 1
        elif xs[1] < x_v < xs[2]:
            left_end = i_peak
        else:
            return fallback
        y_v = a * x_v ** 2 + b * x_v + c
        if y_v < y[i_peak]:
            return fallback
        return left_end, float(x_v), float(y_v)

    @staticmethod
    def _build_spline(
        x: np.ndarray, y: np.ndarray, left_end: int, x_peak: float, y_peak: float
    ) -> _BranchSpline:
        if x_peak == float(x[left_end]) and y_peak == float(y[left_end]):
            # No parabola refinement (edge of data, or genuinely flat) —
            # split directly at the raw peak point as before.
            left = EquilibriumSystem._hermite_branch(x[: left_end + 1], y[: left_end + 1], peak_at_end=True)
            right = EquilibriumSystem._hermite_branch(x[left_end:], y[left_end:], peak_at_end=False)
        else:
            left = EquilibriumSystem._hermite_branch(
                np.append(x[: left_end + 1], x_peak), np.append(y[: left_end + 1], y_peak), peak_at_end=True
            )
            right = EquilibriumSystem._hermite_branch(
                np.insert(x[left_end + 1 :], 0, x_peak), np.insert(y[left_end + 1 :], 0, y_peak), peak_at_end=False
            )
        return _BranchSpline(left, right, x_peak)

    @staticmethod
    def _hermite_branch(x: np.ndarray, y: np.ndarray, peak_at_end: bool) -> CubicHermiteSpline:
        """Monotone Hermite fit for one branch, with the peak-side knot's
        derivative forced to 0 (the plait point is a true extremum, so its
        tangent is horizontal by definition — not just an estimate) so both
        branches meet with matching value *and* slope at the peak.
        """
        if len(x) < 2:
            x = np.array([x[0], x[0] + 1.0])
            y = np.array([y[0], y[0]])
            return CubicHermiteSpline(x, y, [0.0, 0.0])
        d = PchipInterpolator(x, y).derivative()(x)
        d[-1 if peak_at_end else 0] = 0.0
        return CubicHermiteSpline(x, y, d)

    @staticmethod
    def _edge_slope(xs: np.ndarray, ys: np.ndarray) -> float:
        """Non-centered Fritsch-Carlson shape-preserving derivative at xs[0].

        Uses xs[0..2] when available (less sensitive to noise in any single
        point than a plain 2-point secant); falls back to the secant slope
        when only two points exist on that side of the curve.
        """
        if len(xs) < 3:
            return (ys[1] - ys[0]) / (xs[1] - xs[0])
        h0, h1 = abs(xs[1] - xs[0]), abs(xs[2] - xs[1])
        d0 = (ys[1] - ys[0]) / (xs[1] - xs[0])
        d1 = (ys[2] - ys[1]) / (xs[2] - xs[1])
        d_hat = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1)
        if d_hat * d0 < 0:
            d_hat = 0.0
        elif d0 * d1 < 0 and abs(d_hat) > 3 * abs(d0):
            d_hat = 3 * d0
        return d_hat

    def _axis_anchor(self, xs: np.ndarray, ys: np.ndarray) -> float | None:
        """Axis-intercept x for one side of the curve, or None to use the
        real boundary point (xs[0], ys[0]) as-is because it's already at
        (or close enough to) the axis. xs/ys must start at the curve's edge
        point and move inward (2-3 points).
        """
        x0, y0 = float(xs[0]), float(ys[0])
        slope = self._edge_slope(xs, ys)
        if abs(slope) < 1e-9:
            return None
        x_anchor = x0 - y0 / slope
        h0 = abs(xs[1] - xs[0])
        min_gap = max(0.5, 0.15 * h0)
        if abs(x_anchor - x0) < min_gap:
            return None
        max_reach = 3.0 * h0
        if abs(x_anchor - x0) > max_reach:
            x_anchor = x0 - np.sign(x_anchor - x0) * max_reach
        return float(np.clip(x_anchor, 0.0, 100.0))

    def _find_x_intercepts(self, x: np.ndarray, y: np.ndarray) -> list[float]:
        roots: list[float] = []
        for i in range(len(x) - 1):
            if y[i] * y[i + 1] < 0:
                root = brentq(self.spline, x[i], x[i + 1])
                roots.append(round(float(root), 3))

        # No sign change found within the domain (e.g. the boundary point
        # sits at a small positive residual rather than exactly 0) — the
        # domain edge itself is the best available intercept.
        lo, hi = self.x_domain
        if len(roots) == 0:
            roots = [round(lo, 3), round(hi, 3)]
        elif len(roots) == 1 and roots[0] < 50.0:
            roots.append(round(hi, 3))
        elif len(roots) == 1:
            roots.insert(0, round(lo, 3))
        return roots

    def _build_tie_coords(
        self,
    ) -> list[tuple[tuple[float, float], tuple[float, float]]]:
        def on_curve(wpa_target: float, left: bool) -> tuple[float, float]:
            # Invert the spline: find x on the left or right branch where
            # spline(x) = y_target. Each branch is a monotone Hermite piece
            # (see _hermite_branch), so f(x) = spline(x) - y_target has at
            # most one root — checking the two endpoints is enough to know
            # whether it exists, no scan needed.
            y_target = np.sqrt(3) / 2.0 * wpa_target
            lo, hi = (self.x_domain[0], self.x_plait_approx) if left else (self.x_plait_approx, self.x_domain[1])
            f_lo, f_hi = float(self.spline(lo)) - y_target, float(self.spline(hi)) - y_target

            if f_lo * f_hi < 0:
                x_star = brentq(lambda x: float(self.spline(x)) - y_target, lo, hi)
                return float(x_star), float(self.spline(x_star))

            # No sign change: target is at or just past this branch's
            # reachable range (typically a tie line very near the plait
            # point) — accept the closer endpoint if it's a near miss.
            x_star, f_star = (lo, f_lo) if abs(f_lo) < abs(f_hi) else (hi, f_hi)
            if abs(f_star) < 0.5:
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
        bounds = (self.x_domain[0], self.x_plait_approx) if left else (self.x_plait_approx, self.x_domain[1])
        res = minimize_scalar(
            lambda x: abs(
                self.molar_concentration_pa(x, float(self.spline(x))) - target_c
            ),
            bounds=bounds,
            method="bounded",
        )
        x, y = float(res.x), float(self.spline(res.x))
        return (x, y), xy_to_comp(x, y), self.molar_concentration_pa(x, y)
