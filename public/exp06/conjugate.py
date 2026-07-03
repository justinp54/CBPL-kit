from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.interpolate import PchipInterpolator

try:
    from .equilibrium import EquilibriumSystem
    from .ternary import xy_to_comp
except ImportError:
    from equilibrium import EquilibriumSystem
    from ternary import xy_to_comp


@dataclass
class ConjugateCurve:
    """
    Conjugate curve from auxiliary-line intersections and plait-point finder.

    Method (Treybal, Mass Transfer Operations):
    1. For each tie line, draw auxiliary lines with slopes ±√3 from each endpoint.
    2. Their intersection gives one point on the conjugate curve.
    3. Extend that curve, in a straight line along its tangent at the last real
       point (curvature clamped to zero — see _extend_to_plait), until it comes
       closest to the equilibrium curve. That's the plait-point estimate.

    Sparse, real tie-line data is never actually close enough to the plait point
    for this extension to be a precise measurement (the last available tie line
    can still be tens of composition-% away from where the two phases truly
    merge), so step 3 optimizes a "closest approach" objective instead of
    requiring an exact intersection, which may not exist for any well-behaved
    extension of the real points. Treat the result as an estimate, not a
    high-precision answer — a different construction can reasonably land
    somewhere else nearby.
    """

    system: EquilibriumSystem
    method: str = "diagonal"  # "diagonal" | "horizontal"

    def __post_init__(self) -> None:
        self.aux_points: list[tuple[float, float]]
        self.horizontal_side: str | None
        self.aux_points, self.horizontal_side = self._build_aux_points()
        self._t: np.ndarray
        self._px: PchipInterpolator
        self._py: PchipInterpolator
        self._t, self._px, self._py = self._build_parametric()
        self.pt_plait: tuple[float, float]
        self.x_curve: np.ndarray
        self.y_curve: np.ndarray
        self.pt_plait, self.x_curve, self.y_curve = self._extend_to_plait()

    def _build_aux_points(self) -> tuple[list[tuple[float, float]], str | None]:
        # m1 (left/solvent-rich endpoint) is parallel to the right leg;
        # m2 (right/carrier-rich endpoint) parallel to the left leg by
        # default ("diagonal"). "horizontal" swaps ONE of the two for a
        # line parallel to the base (slope 0) instead — but which side
        # stays inside the *triangle* (not just the equilibrium curve's
        # x-domain: a point can have a perfectly in-range x and still be
        # geometrically outside, e.g. y too large for that x, which shows
        # up as a negative composition) depends on the system. So for
        # "horizontal" we build both variants and keep whichever has less
        # total negative-composition violation across its aux points.
        if self.method != "horizontal":
            return self._aux_points_for(-np.sqrt(3), np.sqrt(3)), None

        left_pts = self._aux_points_for(0.0, np.sqrt(3))
        right_pts = self._aux_points_for(-np.sqrt(3), 0.0)

        def excursion(pts: list[tuple[float, float]]) -> float:
            return sum(
                sum(max(-v, 0.0) for v in xy_to_comp(x, y))
                for x, y in pts
            )

        if excursion(left_pts) < excursion(right_pts):
            return left_pts, "left"
        return right_pts, "right"

    def _aux_points_for(self, m1: float, m2: float) -> list[tuple[float, float]]:
        # Baseline intercepts serve as the first (degenerate) "tie line"
        ic = self.system.x_intercepts
        tie_aug = [((ic[0], 0.0), (ic[1], 0.0))] + self.system.tie_coords

        points: list[tuple[float, float]] = []
        for (xL, yL), (xR, yR) in tie_aug:
            # Solve: m1*(x-xL)+yL = m2*(x-xR)+yR
            x_int = (m1 * xL - m2 * xR + yR - yL) / (m1 - m2)
            points.append((float(x_int), float(m1 * (x_int - xL) + yL)))
        return points

    def _build_parametric(self) -> tuple[np.ndarray, PchipInterpolator, PchipInterpolator]:
        """Parametrize the real aux points by cumulative point-to-point
        distance instead of x, since the aux-point trajectory can double
        back in x near the plait point (it isn't a function of x) but
        distance-walked-so-far is always monotonic.
        """
        xs = np.array([p[0] for p in self.aux_points])
        ys = np.array([p[1] for p in self.aux_points])
        ds = np.sqrt(np.diff(xs) ** 2 + np.diff(ys) ** 2)
        t = np.concatenate([[0.0], np.cumsum(ds)])
        return t, PchipInterpolator(t, xs), PchipInterpolator(t, ys)

    def intersect_line(self, slope: float, x0: float, y0: float) -> tuple[float, float]:
        """Intersection of line y = slope*(x-x0)+y0 with the conjugate curve."""
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

    def _extend_to_plait(self) -> tuple[tuple[float, float], np.ndarray, np.ndarray]:
        """Extend the real-data curve past its last point along a straight
        line in its exact tangent direction there — curvature clamped to
        zero, no continued cubic bending — and take the closest approach
        to the equilibrium curve as the plait point.

        Letting the natural PCHIP cubic keep curving instead is unstable:
        stretched far enough, a cubic segment inevitably bends back on
        itself, so "closest approach" can end up almost anywhere depending
        on how far the search is allowed to run (verified empirically —
        the answer swings from one side of the triangle to the other, and
        past a certain distance leaves the triangle entirely, as the
        search range grows). A straight line can't develop that wobble:
        once it's long enough to reach the equilibrium curve, the
        closest-approach point is unique and stops changing no matter how
        much further the search extends.
        """
        t_max = float(self._t[-1])
        x0, y0 = float(self._px(t_max)), float(self._py(t_max))
        dxdt, dydt = float(self._px.derivative()(t_max)), float(self._py.derivative()(t_max))

        dt_scan = np.linspace(0.0, 20.0 * t_max, 6000)
        x_scan = x0 + dxdt * dt_scan
        y_scan = y0 + dydt * dt_scan

        lo, hi = self.system.x_domain
        in_domain = (x_scan >= lo) & (x_scan <= hi)
        if not np.any(in_domain):
            raise ValueError(
                "Conjugate-curve extension never re-enters the equilibrium "
                "curve's domain — check this system's tie-line data."
            )
        gap = np.full_like(x_scan, np.inf)
        gap[in_domain] = np.abs(y_scan[in_domain] - self.system.spline(x_scan[in_domain]))
        i_best = int(np.argmin(gap))
        pt_plait = (float(x_scan[i_best]), float(y_scan[i_best]))

        t_dense = np.linspace(0.0, t_max, 1500)
        # [1:] -- dt=0 is the same point as t_dense's last sample; skip it
        # so the join isn't a duplicated, zero-length segment.
        dt_dense = np.linspace(0.0, dt_scan[i_best], 500)[1:]
        x_curve = np.concatenate([self._px(t_dense), x0 + dxdt * dt_dense])
        y_curve = np.concatenate([self._py(t_dense), y0 + dydt * dt_dense])
        return pt_plait, np.asarray(x_curve), np.asarray(y_curve)
