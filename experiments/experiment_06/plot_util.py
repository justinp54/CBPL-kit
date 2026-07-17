"""
Plotly-based ternary figure builders for Experiment 06 (LLE Hunter-Nash).

All internal calculations use Cartesian (x, y) coordinates.
Plotly's Scatterternary uses (a=wpa, b=ww, c=wbp) with sum=100.
"""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

try:
    from .conjugate import ConjugateCurve
    from .equilibrium import EquilibriumSystem, _DEFAULT_LABELS
    from .hunter_nash import Step, stage_count_trend, feed_stage_count_trend
    from .lever_rule import find_E1_prime, find_M_and_P, mixing_point
    from .ternary import xy_to_comp
except ImportError:
    from conjugate import ConjugateCurve
    from equilibrium import EquilibriumSystem, _DEFAULT_LABELS
    from hunter_nash import Step, stage_count_trend, feed_stage_count_trend
    from lever_rule import find_E1_prime, find_M_and_P, mixing_point
    from ternary import xy_to_comp


def _lb(system: EquilibriumSystem) -> dict:
    """Return the component labels dict from a system, falling back to defaults."""
    return getattr(system, "labels", _DEFAULT_LABELS)

# ---------------------------------------------------------------------------
# Internal helpers
#
# Subscripts in any label Plotly renders — point/line labels, legend names,
# axis and plot titles, annotations, hover — are written as <sub> tags:
# "R<sub>0</sub>", "w<sub>21</sub>". Plotly renders a small HTML subset, and
# <sub> inherits the chart's own font, so it stays typographically consistent
# with everything around it. Do not use literal unicode (R₀, w₂₃) in a label:
# it can't express every case (Eₙ₊₁ is a pile of combining oddities) and it
# reads as a different glyph set next to real subscripts.
#
# LaTeX ($w_{21}$) is NOT an option here: Plotly renders math via MathJax,
# which this app does not load (KaTeX, which it does load, is HTML-side only
# and is unrelated to Plotly). Plain-text sinks — CSV/spreadsheet cells —
# take neither, and spell subscripts with "_" instead.
# ---------------------------------------------------------------------------

def _to_ternary(x: float, y: float) -> tuple[float, float, float]:
    """Cartesian → (wpa, ww, wbp) for Scatterternary (a, b, c)."""
    wpa, wbp, ww = xy_to_comp(x, y)
    return wpa, ww, wbp


def _arr_to_ternary(
    xs: np.ndarray, ys: np.ndarray
) -> tuple[list[float], list[float], list[float]]:
    a, b, c = [], [], []
    for x, y in zip(xs, ys):
        wpa, ww, wbp = _to_ternary(x, y)
        a.append(wpa)
        b.append(ww)
        c.append(wbp)
    return a, b, c


def _in_triangle(x: float, y: float) -> bool:
    """Return True if the point has all non-negative wt% fractions."""
    wpa, wbp, ww = xy_to_comp(x, y)
    return wpa >= 0 and wbp >= 0 and ww >= 0


def _valid_mask(xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    wpa = ys / np.sqrt(3) * 2.0
    wbp = xs - 0.5 * wpa
    ww  = 100.0 - wpa - wbp
    return (wpa >= 0) & (wbp >= 0) & (ww >= 0)


# ---------------------------------------------------------------------------
# Base layout
# ---------------------------------------------------------------------------

_TERNARY_TITLE_PX = 14   # Plotly's own default for these titles — the size they render at
_TERNARY_GAP_PX   = 10   # blank-line font: the b/c gap is 1.3x this, so ~13px


def _bottom_axis_title(name: str) -> dict:
    """Bottom (b/c) ternary axis title, lifted clear of its tick numbers.

    Ternary axes have no title.standoff (cartesian ones do), so a leading <br>
    is the only lever that moves these titles off the numbers they sit under.
    Plotly emits that break as dy="1.3em" against the *title* font, so the gap
    is 1.3 x title font — at the 14px default that lands ~18px, far too much.
    Shrinking the title font shrinks the gap, and an inner <span> holds the
    text at its normal size: that decoupling is what buys a part-line gap,
    since a bare <br> only ever gives whole lines and Plotly ignores font-size
    on a span wrapping the break itself.
    """
    return dict(
        text=f'<br><span style="font-size:{_TERNARY_TITLE_PX}px">{name} (wt%)</span>',
        font=dict(size=_TERNARY_GAP_PX),
    )


def _layout(title: str, system: EquilibriumSystem | None = None) -> dict:
    lb = _lb(system) if system else _DEFAULT_LABELS
    return dict(
        title=dict(text=title, x=0.5, font=dict(size=15)),
        ternary=dict(
            sum=100,
            # The a title is at the apex, clear of everything — leave it be.
            aaxis=dict(title=f"{lb['solute']['name']} (wt%)", min=0.0, ticks="outside", linewidth=2, dtick=10),
            baxis=dict(title=_bottom_axis_title(lb['solvent']['name']), min=0.0, ticks="outside", linewidth=2, dtick=10),
            caxis=dict(title=_bottom_axis_title(lb['carrier']['name']), min=0.0, ticks="outside", linewidth=2, dtick=10),
        ),
        width=750, height=700,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
    )


# ---------------------------------------------------------------------------
# Reusable trace builders
# ---------------------------------------------------------------------------

def _equil_traces(system: EquilibriumSystem) -> list[go.BaseTraceType]:
    lb = _lb(system)
    s, sv, d = lb['solute']['abbr'], lb['solvent']['abbr'], lb['carrier']['abbr']
    mask = _valid_mask(system.x_smooth, system.y_smooth)
    a, b, c = _arr_to_ternary(system.x_smooth[mask], system.y_smooth[mask])
    curve = go.Scatterternary(
        a=a, b=b, c=c,
        mode="lines", name="Binodal curve",
        line=dict(color="black", width=2.5),
        hovertemplate=f"{d}:%{{c:.1f}}%  {s}:%{{a:.1f}}%  {sv}:%{{b:.1f}}%<extra>Binodal curve</extra>",
    )
    a_pts = system.equil_data[:, 1].tolist()
    b_pts = system.equil_data[:, 2].tolist()
    c_pts = system.equil_data[:, 0].tolist()
    pts = go.Scatterternary(
        a=a_pts, b=b_pts, c=c_pts,
        mode="markers", name="Equil. data",
        marker=dict(color="black", size=7),
        hovertemplate=f"{d}:%{{c:.2f}}%  {s}:%{{a:.2f}}%  {sv}:%{{b:.2f}}%<extra>Equil. data</extra>",
    )
    return [curve, pts]


def _tie_traces(system: EquilibriumSystem) -> list[go.BaseTraceType]:
    lb = _lb(system)
    s, sv, d = lb['solute']['abbr'], lb['solvent']['abbr'], lb['carrier']['abbr']
    traces = []
    for i, ((x1, y1), (x2, y2)) in enumerate(system.tie_coords):
        a1, b1, c1 = _to_ternary(x1, y1)
        a2, b2, c2 = _to_ternary(x2, y2)
        traces.append(go.Scatterternary(
            a=[a1, a2], b=[b1, b2], c=[c1, c2],
            mode="lines+markers",
            line=dict(color="steelblue", width=1, dash="dot"),
            marker=dict(size=5, color="steelblue"),
            name="Tie-lines" if i == 0 else None,
            showlegend=(i == 0),
            hovertemplate=f"{d}:%{{c:.2f}}%  {s}:%{{a:.2f}}%  {sv}:%{{b:.2f}}%<extra>Tie-line</extra>",
        ))
    return traces


def _point_trace(
    pt: tuple[float, float],
    label: str,
    color: str,
    symbol: str = "circle",
    size: int = 9,
    labels: dict | None = None,
    textposition: str = "top center",
) -> go.Scatterternary:
    lb = labels or _DEFAULT_LABELS
    s, sv, d = lb['solute']['abbr'], lb['solvent']['abbr'], lb['carrier']['abbr']
    a, b, c = _to_ternary(*pt)
    wpa, wbp, ww = xy_to_comp(*pt)
    return go.Scatterternary(
        a=[a], b=[b], c=[c],
        mode="markers+text",
        name=label,
        marker=dict(color=color, size=size, symbol=symbol),
        text=[label],
        textposition=textposition,
        hovertemplate=(
            f"<b>{label}</b><br>{s}:{wpa:.2f}%  {sv}:{ww:.2f}%  {d}:{wbp:.2f}%<extra></extra>"
        ),
    )


def _line_trace(
    p1: tuple[float, float],
    p2: tuple[float, float],
    name: str,
    color: str,
    dash: str = "solid",
    width: float = 1.2,
    showlegend: bool = True,
) -> go.Scatterternary:
    a1, b1, c1 = _to_ternary(*p1)
    a2, b2, c2 = _to_ternary(*p2)
    return go.Scatterternary(
        a=[a1, a2], b=[b1, b2], c=[c1, c2],
        mode="lines",
        name=name,
        line=dict(color=color, width=width, dash=dash),
        showlegend=showlegend,
    )


def _en1_point_trace(pt_En1: tuple[float, float], labels: dict) -> go.Scatterternary:
    """E_N+1 on the water vertex, with its label nudged inside the triangle.

    Scatterternary clips to the triangle, and E_N+1 sits exactly on a corner of
    it, so the default "top center" label hangs outside and all but its tail is
    cut away. "top right" alone isn't enough either: the left edge rises from
    that corner at 60°, so a label starting at the vertex still begins a few px
    outside and loses the left of the "E". Two leading spaces push the glyphs in
    (Plotly renders label text with white-space:pre, so they survive).

    The padding goes on the on-plot text only — the legend name and the hover
    box keep the clean label.
    """
    tr = _point_trace(pt_En1, "E<sub>N+1</sub>", "crimson", labels=labels,
                      textposition="top right")
    tr.text = ["  E<sub>N+1</sub>"]
    return tr


# The lever-rule family (Lever Rule tab, and both explorers, which reuse these
# same two builders) labels every point and line on the plot itself, so the
# legend only needs the handful a label can't stand in for. Anything not named
# here is dropped from the legend by _trim_legend, including traces added later.
_LEVER_LEGEND = frozenset({
    "Binodal curve", "Equil. data",
    "E<sub>1</sub>", "E<sub>1</sub>'", "M", "M'",
})


def _trim_legend(fig: go.Figure, keep: frozenset[str]) -> None:
    """Leave a legend entry only for the traces named in `keep`."""
    for tr in fig.data:
        if tr.name not in keep:
            tr.showlegend = False


# ---------------------------------------------------------------------------
# Cartesian-based helpers (support extrapolation outside the triangle)
#
# Plotly's Scatterternary clips everything to the triangle interior.
# For Fig 2(a) (conjugate curve below base) and Fig 3 (P point outside),
# we switch to go.Scatter in the same internal (x, y) Cartesian space used
# by the calculation modules.  The mapping is exact:
#   Water vertex  → (0,    0)
#   n-BP vertex   → (100,  0)
#   PA vertex     → (50,   100·√3/2)
# ---------------------------------------------------------------------------

_PA_V: tuple[float, float] = (50.0, 100.0 * np.sqrt(3) / 2.0)
_W_V:  tuple[float, float] = (0.0,  0.0)
_BP_V: tuple[float, float] = (100.0, 0.0)


def _cart_layout(
    title: str,
    x_range: tuple[float, float] = (-28, 118),
    y_range: tuple[float, float] = (-55, 100),
) -> dict:
    """Layout for Cartesian ternary plots that support extrapolation."""
    return dict(
        title=dict(text=title, x=0.5, font=dict(size=15)),
        xaxis=dict(visible=False, range=x_range),
        yaxis=dict(visible=False, range=y_range, scaleanchor="x", scaleratio=1),
        width=750, height=800,
        plot_bgcolor="white",
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
        margin=dict(l=20, r=20, t=60, b=20),
    )


def _cart_triangle_traces(system: EquilibriumSystem) -> list:
    """Triangle border, vertex labels, and 10%-interval gridlines."""
    lb = _lb(system)
    traces: list = []

    # Border
    xs = [_W_V[0], _BP_V[0], _PA_V[0], _W_V[0]]
    ys = [_W_V[1], _BP_V[1], _PA_V[1], _W_V[1]]
    traces.append(go.Scatter(
        x=xs, y=ys, mode="lines",
        line=dict(color="black", width=2),
        showlegend=False, hoverinfo="skip",
    ))

    # Vertex labels (offset from vertices for readability)
    _vlabels = [
        (f"Solute ({lb['solute']['name']})",   50,   _PA_V[1] + 3, "middle center"),
        (f"Solvent ({lb['solvent']['name']})",  -10,  -5, "middle center"),
        (f"Carrier ({lb['carrier']['name']})",  118,  -5, "middle left"),
    ]
    for text, x, y, tpos in _vlabels:
        traces.append(go.Scatter(
            x=[x], y=[y], mode="text",
            text=[f"<b>{text}</b>"],
            textposition=tpos,
            textfont=dict(size=11),
            showlegend=False, hoverinfo="skip",
        ))

    # Gridlines at 10% intervals for all three families
    for i in range(1, 10):
        t = i / 10
        # Constant wPA  (parallel to W-BP base)
        traces.append(go.Scatter(
            x=[t * 50, 100 - t * 50],
            y=[t * _PA_V[1], t * _PA_V[1]],
            mode="lines", line=dict(color="lightgray", width=0.8, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ))
        # Constant wW   (parallel to BP-PA right side)
        traces.append(go.Scatter(
            x=[(1 - t) * 100, (1 - t) * 50],
            y=[0, (1 - t) * _PA_V[1]],
            mode="lines", line=dict(color="lightgray", width=0.8, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ))
        # Constant wBP  (parallel to W-PA left side)
        traces.append(go.Scatter(
            x=[t * 100, 50 * (1 + t)],
            y=[0, (1 - t) * _PA_V[1]],
            mode="lines", line=dict(color="lightgray", width=0.8, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ))

    return traces


def _comp_customdata(xs, ys) -> list:
    """Per-point [carrier, solute, solvent] wt% for a composition hover."""
    out = []
    for xx, yy in zip(xs, ys):
        wpa, wbp, ww = xy_to_comp(float(xx), float(yy))
        out.append([wbp, wpa, ww])   # carrier, solute, solvent
    return out


def _cart_equil_traces(system: EquilibriumSystem, hover_comp: bool = False) -> list:
    """Binodal curve + data points as go.Scatter.

    hover_comp=True shows a composition hover (carrier, solute, solvent — abbr +
    value, same as the Equilibrium-tab ternary traces) instead of the default
    internal (x, y) Cartesian readout. Default False keeps the (x, y) hover for
    every other Cartesian figure that shares this builder.
    """
    mask = _valid_mask(system.x_smooth, system.y_smooth)
    bx, by = system.x_smooth[mask], system.y_smooth[mask]
    binodal = go.Scatter(
        x=bx, y=by,
        mode="lines", name="Binodal curve",
        line=dict(color="black", width=2.5),
    )
    equil = go.Scatter(
        x=system.x_equil, y=system.y_equil,
        mode="markers", name="Equil. data",
        marker=dict(color="black", size=7),
    )
    if hover_comp:
        lb = _lb(system)
        ca, so, sv = lb['carrier']['abbr'], lb['solute']['abbr'], lb['solvent']['abbr']
        binodal.update(
            customdata=_comp_customdata(bx, by),
            hovertemplate=(
                f"{ca}:%{{customdata[0]:.1f}}%  {so}:%{{customdata[1]:.1f}}%  "
                f"{sv}:%{{customdata[2]:.1f}}%<extra>Binodal curve</extra>"
            ),
        )
        equil.update(
            customdata=_comp_customdata(system.x_equil, system.y_equil),
            hovertemplate=(
                f"{ca}:%{{customdata[0]:.2f}}%  {so}:%{{customdata[1]:.2f}}%  "
                f"{sv}:%{{customdata[2]:.2f}}%<extra>Equil. data</extra>"
            ),
        )
    return [binodal, equil]


def _cart_tie_traces(system: EquilibriumSystem, hover_comp: bool = False) -> list:
    """Tie-lines as go.Scatter.

    hover_comp=True adds a composition hover (carrier, solute, solvent) at each
    endpoint; default keeps the current no-hover (hoverinfo="skip") behavior.
    """
    lb = _lb(system)
    ca, so, sv = lb['carrier']['abbr'], lb['solute']['abbr'], lb['solvent']['abbr']
    traces = []
    for i, ((x1, y1), (x2, y2)) in enumerate(system.tie_coords):
        tr = go.Scatter(
            x=[x1, x2], y=[y1, y2],
            mode="lines+markers",
            line=dict(color="steelblue", width=1, dash="dot"),
            marker=dict(size=5, color="steelblue"),
            name="Tie-lines" if i == 0 else None,
            showlegend=(i == 0),
        )
        if hover_comp:
            tr.update(
                customdata=_comp_customdata([x1, x2], [y1, y2]),
                hovertemplate=(
                    f"{ca}:%{{customdata[0]:.2f}}%  {so}:%{{customdata[1]:.2f}}%  "
                    f"{sv}:%{{customdata[2]:.2f}}%<extra>Tie-line</extra>"
                ),
            )
        else:
            tr.update(hoverinfo="skip")
        traces.append(tr)
    return traces


def _cart_point_trace(
    pt: tuple[float, float], label: str, color: str,
    symbol: str = "circle", size: int = 9,
    labels: dict | None = None, show_text: bool = True,
) -> go.Scatter:
    lb = labels or _DEFAULT_LABELS
    s, sv, d = lb['solute']['abbr'], lb['solvent']['abbr'], lb['carrier']['abbr']
    x, y = pt
    wpa, wbp, ww = xy_to_comp(x, y)
    return go.Scatter(
        x=[x], y=[y],
        mode="markers+text" if show_text else "markers",
        name=label,
        marker=dict(color=color, size=size, symbol=symbol),
        text=[label] if show_text else None,
        textposition="top center",
        hovertemplate=(
            f"<b>{label}</b><br>{s}:{wpa:.2f}%  {d}:{wbp:.2f}%  {sv}:{ww:.2f}%<extra></extra>"
        ),
    )


def _cart_line_trace(
    p1: tuple[float, float],
    p2: tuple[float, float],
    name: str | None,
    color: str,
    dash: str = "solid",
    width: float = 1.2,
    showlegend: bool = True,
) -> go.Scatter:
    return go.Scatter(
        x=[p1[0], p2[0]], y=[p1[1], p2[1]],
        mode="lines",
        name=name,
        line=dict(color=color, width=width, dash=dash),
        showlegend=showlegend,
        hoverinfo="skip",
    )


# ---------------------------------------------------------------------------
# Figure builders
# ---------------------------------------------------------------------------

def fig_ternary_equilibrium(system: EquilibriumSystem) -> go.Figure:
    """Fig 1 — Ternary diagram with equilibrium curve and tie lines."""
    traces = _equil_traces(system) + _tie_traces(system)
    fig = go.Figure(data=traces)
    fig.update_layout(**_layout("Ternary Phase Diagram", system))
    return fig


def fig_conjugate_curve(
    system: EquilibriumSystem,
    conjugate: ConjugateCurve,
) -> go.Figure:
    """Fig 2(a) — Conjugate curve with extrapolation outside the triangle.

    Uses go.Scatter (Cartesian) instead of Scatterternary so the auxiliary
    intersection points and conjugate curve below the triangle base are visible.
    """
    traces = (
        _cart_triangle_traces(system)
        + _cart_equil_traces(system, hover_comp=True)
        + _cart_tie_traces(system, hover_comp=True)
    )

    # Conjugate curve — full range including extrapolation below triangle
    traces.append(go.Scatter(
        x=conjugate.x_curve, y=conjugate.y_curve,
        mode="lines", name="Conjugate curve",
        line=dict(color="darkorange", width=2),
    ))

    # All auxiliary intersection points (including those outside the triangle)
    traces.append(go.Scatter(
        x=[p[0] for p in conjugate.aux_points],
        y=[p[1] for p in conjugate.aux_points],
        mode="markers", name="Aux. intersections",
        marker=dict(color="darkorange", size=7, symbol="circle-open"),
        showlegend=False,
    ))

    # Baseline auxiliary lines: x-intercepts → aux_points[0]
    pt_aux_0 = conjugate.aux_points[0]
    for x_int in system.x_intercepts:
        traces.append(go.Scatter(
            x=[x_int, pt_aux_0[0]], y=[0.0, pt_aux_0[1]],
            mode="lines",
            line=dict(color="darkorange", width=0.8, dash="dot"),
            showlegend=False, hoverinfo="skip",
        ))

    # Dashed auxiliary lines from each tie-line endpoint → intersection point
    for (pt_L, pt_R), pt_aux in zip(system.tie_coords, conjugate.aux_points[1:]):
        for pt_end in (pt_L, pt_R):
            traces.append(go.Scatter(
                x=[pt_end[0], pt_aux[0]], y=[pt_end[1], pt_aux[1]],
                mode="lines",
                line=dict(color="darkorange", width=0.8, dash="dot"),
                showlegend=False, hoverinfo="skip",
            ))

    # Plait star built inline (not via shared _cart_point_trace) so its hover
    # can list components in carrier → solute → solvent order without changing
    # the other cart points (R₀, Rₙ, E₁, P, M, …) that share that helper.
    _lbp = _lb(system)
    _cabbr, _sabbr, _svabbr = _lbp['carrier']['abbr'], _lbp['solute']['abbr'], _lbp['solvent']['abbr']
    _px, _py = conjugate.pt_plait
    _wpa, _wbp, _ww = xy_to_comp(_px, _py)
    traces.append(go.Scatter(
        x=[_px], y=[_py],
        mode="markers",
        name="Plait pt. (Conj. Curve)",
        marker=dict(color="darkorange", size=14, symbol="star"),
        hovertemplate=(
            f"<b>Plait pt. (Conj. Curve)</b><br>"
            f"{_cabbr}:{_wbp:.2f}%  {_sabbr}:{_wpa:.2f}%  {_svabbr}:{_ww:.2f}%<extra></extra>"
        ),
    ))

    fig = go.Figure(data=traces)
    y_min = min(p[1] for p in conjugate.aux_points)
    fig.update_layout(**_cart_layout(
        "Conjugate Curve and Estimated Plait Point",
        y_range=(y_min - 8, 100),
    ))
    return fig


def fig_hunter_nash(
    system: EquilibriumSystem,
    steps: list[Step],
    N_theory: float,
    pt_R0: tuple[float, float],
    pt_Rn: tuple[float, float],
    pt_E1: tuple[float, float],   # noqa: ARG001 — see docstring
    pt_En1: tuple[float, float],
    pt_P: tuple[float, float],
) -> go.Figure:
    """Fig 3 — Hunter-Nash with operating point P shown outside the triangle.

    Uses go.Scatter (Cartesian) so the operating lines can extend to P even
    when P lies outside the ternary triangle.

    pt_E1 is accepted but unused: it is the same point as steps[0].pt_E, which
    the stage construction already draws. It stays in the signature because
    callers (app.js PY_COMPUTE, main.py, demo.ipynb) pass it positionally.
    """
    lb = _lb(system)
    traces = _cart_triangle_traces(system) + _cart_equil_traces(system, hover_comp=True)

    # Key stream and operating points. Every one is labelled on the plot, so
    # none of them takes a legend entry — the legend stays down to the three
    # things it can't say in place: Binodal curve, Equil. data, Stages.
    #
    # pt_E1 is deliberately not drawn here: it is exactly stage 1's E (the
    # solver starts there), which the stage loop below already marks and
    # labels, so a point trace for it stacked a second, differently-sized "E1"
    # on the same spot. pt_Rn is drawn — the last stage's R lands near it but
    # is a distinct point, and both labels carry information.
    for tr in (
        _cart_point_trace(pt_R0,  "R<sub>0</sub>",   "royalblue", labels=lb),
        _cart_point_trace(pt_Rn,  "R<sub>N</sub>",   "royalblue", labels=lb),
        _cart_point_trace(pt_En1, "E<sub>N+1</sub>", "crimson",   labels=lb),
        _cart_point_trace(pt_P,   "P", "saddlebrown", symbol="diamond", size=11, labels=lb),
    ):
        tr.showlegend = False
        traces.append(tr)

    # Operating lines through P (extend outside triangle)
    for pt_stream, label in [(pt_R0, "R<sub>0</sub>–P"), (pt_Rn, "R<sub>N</sub>–P")]:
        traces.append(_cart_line_trace(
            pt_stream, pt_P, label, "saddlebrown", dash="dash", width=1, showlegend=False
        ))

    # Stages: tie line E_i → R_i, then operating line R_i → P
    # Legend-only entry: green line matching the tie-line segment
    traces.append(go.Scatter(
        x=[None], y=[None], mode="lines",
        line=dict(color="darkgreen", width=1.8),
        name="Stages", showlegend=True,
    ))
    for s in steps:
        i = s.index
        wpa_E, wpa_R = s.comp_E[0], s.comp_R[0]
        traces.append(go.Scatter(
            x=[s.pt_E[0], s.pt_R[0]], y=[s.pt_E[1], s.pt_R[1]],
            mode="lines+markers+text",
            line=dict(color="darkgreen", width=1.8),
            marker=dict(color=["crimson", "royalblue"], size=8),
            text=[f"E<sub>{i}</sub>", f"R<sub>{i}</sub>"],
            textposition=["middle right", "middle left"],
            textfont=dict(size=10),
            customdata=[[wpa_E, s.comp_E[1], s.comp_E[2]],
                        [wpa_R, s.comp_R[1], s.comp_R[2]]],
            hovertemplate=f"{lb['solute']['abbr']}:%{{customdata[0]:.2f}}%  {lb['carrier']['abbr']}:%{{customdata[1]:.2f}}%  {lb['solvent']['abbr']}:%{{customdata[2]:.2f}}%<extra>%{{text}}</extra>",
            showlegend=False,
        ))
        if i < len(steps):
            traces.append(_cart_line_trace(
                s.pt_R, pt_P, None, "saddlebrown", dash="dash", width=0.8, showlegend=False
            ))

    fig = go.Figure(data=traces)
    pad = 10
    fig.update_layout(**_cart_layout(
        f"Hunter-Nash Construction (N={N_theory:.1f})",
        x_range=(min(pt_P[0] - pad, -pad), 118),
        y_range=(min(pt_P[1] - pad, -pad), 88),
    ))
    fig.update_layout(
        margin=dict(l=10, r=60, t=40, b=30),
        legend=dict(x=1.0, y=1.0, xanchor="right", yanchor="top",
                    font=dict(size=9), bgcolor="rgba(255,255,255,0.9)"),
    )
    return fig


def fig_interpolated_tie_lines(
    system: EquilibriumSystem,
    conjugate: ConjugateCurve,
    steps: list[Step],
    N_theory: float,
) -> go.Figure:
    """Fig 2(b) — Interpolated tie lines via conjugate curve (Cartesian, extrapolation visible)."""
    traces = _cart_triangle_traces(system) + _cart_equil_traces(system)

    # Conjugate curve — full range, no triangle mask
    traces.append(go.Scatter(
        x=conjugate.x_curve, y=conjugate.y_curve,
        mode="lines", name="Conjugate curve",
        line=dict(color="darkorange", width=2),
    ))
    traces.append(_cart_point_trace(
        conjugate.pt_plait, "Plait pt. (Conj. Curve)", "darkorange", symbol="star", size=14,
        labels=_lb(system), show_text=False,
    ))

    # Legend-only entry: green line matching the tie-line segment
    traces.append(go.Scatter(
        x=[None], y=[None], mode="lines",
        line=dict(color="darkgreen", width=1.8),
        name="Stages", showlegend=True,
    ))
    for s in steps:
        i = s.index
        # Interpolated tie line E_i → R_i
        traces.append(go.Scatter(
            x=[s.pt_E[0], s.pt_R[0]], y=[s.pt_E[1], s.pt_R[1]],
            mode="lines+markers+text",
            line=dict(color="darkgreen", width=1.8),
            marker=dict(color=["crimson", "royalblue"], size=7),
            text=[f"E<sub>{i}</sub>", f"R<sub>{i}</sub>"],
            textposition=["middle right", "middle left"],
            textfont=dict(size=10),
            showlegend=False,
        ))

        # Auxiliary dashed lines E_i → pt_inter and R_i → pt_inter
        for pt_end in (s.pt_E, s.pt_R):
            traces.append(go.Scatter(
                x=[pt_end[0], s.pt_inter[0]], y=[pt_end[1], s.pt_inter[1]],
                mode="lines",
                line=dict(color="darkgreen", width=0.8, dash="dot"),
                showlegend=False, hoverinfo="skip",
            ))

    fig = go.Figure(data=traces)
    y_min = min(p[1] for p in conjugate.aux_points)
    fig.update_layout(**_cart_layout(
        "Interpolated Tie-Lines", y_range=(y_min - 8, 100)
    ))
    return fig


def fig_lever_rule(
    system: EquilibriumSystem,
    pt_R0: tuple[float, float],
    pt_Rn: tuple[float, float],
    pt_E1: tuple[float, float],
    pt_En1: tuple[float, float],
    pt_M: tuple[float, float],
    pt_Mp: tuple[float, float],
    pt_E1p: tuple[float, float] | None,
    title: str = "Lever Rule",
    pt_R0_actual: tuple[float, float] | None = None,
) -> go.Figure:
    """
    Figs 4, 5(a/b), 6(a/b) — Lever-rule M' and E1' construction.

    pt_R0        : feed point used for M' calculation (actual or hypothetical)
    pt_R0_actual : if provided, also plots the actual experimental R0 separately
                   (used in Fig 6 where a hypothetical feed composition is shown)
    """
    lb = _lb(system)
    traces = _equil_traces(system)

    # Always show actual experiment stream points
    if pt_R0_actual is not None:
        traces.append(_point_trace(pt_R0_actual, "R<sub>0</sub> (exp.)", "royalblue",
                                   symbol="circle-open", size=9, labels=lb))
    traces += [
        # R₀ sits on the water-free right edge — label inward to avoid clipping
        # past it (E_N+1 has the same problem at its vertex; see _en1_point_trace).
        _point_trace(pt_R0,  "R<sub>0</sub>",    "royalblue",   labels=lb, textposition="middle left"),
        _point_trace(pt_Rn,  "R<sub>N</sub>",    "royalblue",   labels=lb),
        _point_trace(pt_E1,  "E<sub>1</sub>",    "crimson",     labels=lb),
        _en1_point_trace(pt_En1, lb),
        _point_trace(pt_M,   "M",     "purple",     symbol="diamond-open", size=10, labels=lb),
        _point_trace(pt_Mp,  "M'",    "saddlebrown", symbol="diamond",     size=10, labels=lb),
    ]

    # E1–Rn and En1–R0 lines (locating M)
    traces += [
        _line_trace(pt_E1,  pt_Rn,  "E<sub>1</sub>–R<sub>N</sub>",    "purple", width=1),
        _line_trace(pt_En1, pt_R0,  "E<sub>N+1</sub>–R<sub>0</sub>",  "purple", width=1),
    ]

    if pt_E1p is not None:
        traces.append(_point_trace(pt_E1p, "E<sub>1</sub>'", "crimson", symbol="circle-open", size=11, labels=lb))
        traces.append(_line_trace(pt_Rn, pt_E1p, "R<sub>N</sub>–E<sub>1</sub>'", "saddlebrown", width=1.2))

    fig = go.Figure(data=traces)
    fig.update_layout(**_layout(title, system))
    _trim_legend(fig, _LEVER_LEGEND)
    return fig


def fig_feed_explorer(
    system: EquilibriumSystem,
    pt_R0_actual: tuple[float, float],
    pt_Rn: tuple[float, float],
    pt_E1: tuple[float, float],
    pt_En1: tuple[float, float],
    pt_M: tuple[float, float],
    pt_R0p: tuple[float, float],
    pt_Mp: tuple[float, float],
    pt_E1p: tuple[float, float] | None,
    title: str = "Feed Explorer",
) -> go.Figure:
    """Static single-frame Feed Explorer figure for the live HTML slider.

    The real experiment is the fixed anchor, exactly like the other tabs:
    R₀ (experimental feed), its real mixing point M, and their locating lines
    stay put. The slider supplies a *hypothetical* feed R₀' (binary BP+PA edge)
    whose mixing point M' and E₁' move. Unlike fig_lever_rule (shared by Fig 4
    and the S:F explorer, which relabels the moving feed as plain "R₀"), this
    keeps R₀/M fixed and labels only the moving construction with primes, so
    the real operating point and the what-if one sit side by side.

    pt_M : the real experimental mixing point, held fixed (not recomputed
           from the hypothetical feed).
    """
    lb = _lb(system)
    traces = _equil_traces(system)

    # ── Fixed real-experiment anchors ─────────────────────────────────────────
    # R₀/R₀' sit on the water-free right edge, so their labels go inward
    # ("... left") instead of "top center", which would clip past the edge.
    # (E_N+1 has the same problem at its vertex; see _en1_point_trace.)
    traces += [
        _point_trace(pt_R0_actual, "R<sub>0</sub>",    "royalblue",   labels=lb, textposition="middle left"),
        _point_trace(pt_Rn,        "R<sub>N</sub>",    "royalblue",   labels=lb),
        _point_trace(pt_E1,        "E<sub>1</sub>",    "crimson",     labels=lb),
        _en1_point_trace(pt_En1, lb),
        _point_trace(pt_M,         "M",     "purple", symbol="diamond-open", size=10, labels=lb),
        _line_trace(pt_E1,  pt_Rn,        "E<sub>1</sub>–R<sub>N</sub>",   "purple", width=1),
        _line_trace(pt_En1, pt_R0_actual, "E<sub>N+1</sub>–R<sub>0</sub>", "purple", width=1),
    ]

    # ── Hypothetical (moving) primed construction ─────────────────────────────
    traces += [
        _point_trace(pt_R0p, "R<sub>0</sub>'", "saddlebrown", labels=lb, textposition="bottom left"),
        _line_trace(pt_En1, pt_R0p, "E<sub>N+1</sub>–R<sub>0</sub>'", "saddlebrown", width=1),
        _point_trace(pt_Mp,  "M'",  "saddlebrown", symbol="diamond", size=10, labels=lb),
    ]
    if pt_E1p is not None:
        traces.append(_point_trace(pt_E1p, "E<sub>1</sub>'", "crimson", symbol="circle-open", size=11, labels=lb))
        traces.append(_line_trace(pt_Rn, pt_E1p, "R<sub>N</sub>–E<sub>1</sub>'", "saddlebrown", width=1.2))

    fig = go.Figure(data=traces)
    fig.update_layout(**_layout(title, system))
    _trim_legend(fig, _LEVER_LEGEND)
    return fig


def fig_lever_rule_interactive(
    system: EquilibriumSystem,
    pt_R0: tuple[float, float],
    pt_Rn: tuple[float, float],
    pt_E1: tuple[float, float],
    pt_En1: tuple[float, float],
    pt_M: tuple[float, float],
    n_steps: int = 50,
) -> go.Figure:
    """Lever-rule figure with a draggable Plotly slider for solvent:feed ratio.

    The slider moves M' along the En1–R0 line and updates E1' in real time.
    Exports to a fully self-contained HTML — no server required.

    Parameters
    ----------
    n_steps : int
        Number of slider positions (more = smoother, larger file).
    """
    frac_vals = np.linspace(0.0, 1.0, n_steps)   # solvent mass fraction

    lb = _lb(system)
    # ── Static traces (triangle + equilibrium + fixed stream points) ─────────
    static = (
        _cart_triangle_traces(system)
        + _cart_equil_traces(system)
        + [
            _cart_point_trace(pt_R0,  "R<sub>0</sub>",    "royalblue",  labels=lb),
            _cart_point_trace(pt_Rn,  "R<sub>N</sub>",    "royalblue",  labels=lb),
            _cart_point_trace(pt_E1,  "E<sub>1</sub>",    "crimson",    labels=lb),
            _cart_point_trace(pt_En1, "E<sub>N+1</sub>",  "crimson",    labels=lb),
            _cart_point_trace(pt_M,   "M",      "purple", symbol="diamond-open", size=10, labels=lb),
            _cart_line_trace(pt_E1,  pt_Rn,  "E<sub>1</sub>–R<sub>N</sub>",    "purple", width=1),
            _cart_line_trace(pt_En1, pt_R0,  "E<sub>N+1</sub>–R<sub>0</sub>",  "purple", width=1),
        ]
    )
    n_static = len(static)

    def _dynamic(frac: float) -> list:
        pt_Mp  = mixing_point(pt_R0, pt_En1, mass_A=1 - frac, mass_B=frac)
        pt_E1p = find_E1_prime(pt_Rn, pt_Mp, system.spline)
        mp_tr  = _cart_point_trace(pt_Mp, "M'", "saddlebrown", symbol="diamond", size=10, labels=lb)
        if pt_E1p is not None:
            e1p_tr  = _cart_point_trace(pt_E1p, "E<sub>1</sub>'", "crimson", symbol="circle-open", size=11, labels=lb)
            line_tr = _cart_line_trace(pt_Rn, pt_E1p, "R<sub>N</sub>–E<sub>1</sub>'", "saddlebrown", width=1.5)
        else:
            e1p_tr  = go.Scatter(x=[], y=[], mode="markers", showlegend=False, hoverinfo="skip")
            line_tr = go.Scatter(x=[], y=[], mode="lines",   showlegend=False, hoverinfo="skip")
        return [mp_tr, e1p_tr, line_tr]

    fig = go.Figure(data=static + _dynamic(frac_vals[0]))

    # ── Frames (one per slider tick) ─────────────────────────────────────────
    fig.frames = [
        go.Frame(
            data=_dynamic(frac),
            traces=list(range(n_static, n_static + 3)),
            name=f"{frac:.3f}",
        )
        for frac in frac_vals
    ]

    # ── Slider layout ─────────────────────────────────────────────────────────
    slider_steps = [
        dict(
            args=[[f"{frac:.3f}"],
                  dict(frame=dict(duration=0, redraw=True), mode="immediate")],
            label=f"S:{frac*100:.0f} F:{(1-frac)*100:.0f}",
            method="animate",
        )
        for frac in frac_vals
    ]
    fig.update_layout(
        **_cart_layout("Lever Rule — Drag slider to adjust Solvent : Feed ratio"),
        sliders=[dict(
            active=0,
            steps=slider_steps,
            currentvalue=dict(
                prefix="Solvent : Feed = ",
                visible=True,
                font=dict(size=12),
            ),
            pad=dict(b=10, t=60),
            len=0.9,
            x=0.05,
            y=0,
        )],
        updatemenus=[],   # suppress default play button
    )
    fig.update_layout(height=850)   # extra height to accommodate slider
    return fig


def fig_sf_stage_trend(
    system: EquilibriumSystem,
    conjugate: ConjugateCurve,
    pt_R0: tuple[float, float],
    pt_Rn: tuple[float, float],
    pt_En1: tuple[float, float],
    frac_min: float,
    frac_max: float,
) -> go.Figure | None:
    """Stages needed vs S:F ratio, using only genuinely-computed (never
    guessed-at) points from stage_count_trend — see its docstring for why
    the trend stops short of frac_min itself rather than trying to reach
    or demonstrate the boundary directly.

    Computed once during Calculate, not tied to the live slider drag.
    Returns None if fewer than 2 usable points were found (too little to
    draw a trend from).
    """
    points = stage_count_trend(system, conjugate, pt_R0, pt_Rn, pt_En1, frac_min, frac_max)
    if len(points) < 2:
        return None

    # S/F (w/w), not S/(S+F) wt% — matches the (S/F)_min/(S/F)_max cards
    # below, and reads left-to-right increasing like any normal axis
    # (frac is monotonic in S/F, so no reversal is needed).
    xs = [p[0] / (1 - p[0]) for p in points]
    ys = [p[1] for p in points]
    _axis = dict(tickfont=dict(size=9), showgrid=False, nticks=4,
                 showline=True, linewidth=1, linecolor='#d0d5dd', mirror=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode='markers',
        marker=dict(color='steelblue', size=6, line=dict(width=0.5, color='white')),
        showlegend=False,
        hovertemplate='S/F %{x:.2f}<br>%{y:.1f} stages<extra></extra>',
    ))
    fig.update_layout(
        title=dict(text='Stages needed as S:F falls', font=dict(size=10, color='#0f2744'), x=0, xanchor='left'),
        xaxis=dict(title=dict(text='S/F (w/w)', font=dict(size=10)), **_axis),
        yaxis=dict(title=dict(text='Theoretical stages', font=dict(size=10)), rangemode='tozero', **_axis),
        margin=dict(l=34, r=34, t=28, b=36),
        width=320, height=260,
        plot_bgcolor='white',
        paper_bgcolor='white',
    )
    fig.add_vline(
        x=frac_min / (1 - frac_min),
        line_dash='dash',
        line_color='#1a8a5f',
        line_width=1,
        annotation_text='(S/F)<sub>min</sub>',
        annotation_position='bottom right',
        annotation_font_size=9,
        annotation_font_color='#1a8a5f',
    )
    return fig


def fig_feed_stage_trend(
    system: EquilibriumSystem,
    conjugate: ConjugateCurve,
    pt_Rn: tuple[float, float],
    pt_En1: tuple[float, float],
    mass_R0: float,
    mass_En1: float,
    wpa_lo: float = 10.0,
    wpa_hi: float = 55.0,
) -> go.Figure | None:
    """Stages needed vs Feed solute wt%, using only genuinely-computed points
    from feed_stage_count_trend. No named limit line (see its docstring) —
    just the trend itself. Not necessarily monotonic (see
    feed_stage_count_trend's docstring) — don't caption this as "rising"
    or "falling", the shape is whatever the real geometry gives.

    Computed once during Calculate, not tied to the live slider drag.
    Returns None if fewer than 2 usable points were found.
    """
    points = feed_stage_count_trend(system, conjugate, pt_Rn, pt_En1, mass_R0, mass_En1, wpa_lo, wpa_hi)
    if len(points) < 2:
        return None

    s = _lb(system)['solute']['abbr']
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    _axis = dict(tickfont=dict(size=9), showgrid=False, nticks=4,
                 showline=True, linewidth=1, linecolor='#d0d5dd', mirror=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode='markers',
        marker=dict(color='steelblue', size=6, line=dict(width=0.5, color='white')),
        showlegend=False,
        hovertemplate=f'Feed {s} %{{x:.0f}} wt%<br>%{{y:.1f}} stages<extra></extra>',
    ))
    fig.update_layout(
        title=dict(text=f'Stages needed vs Feed {s}', font=dict(size=10, color='#0f2744'), x=0, xanchor='left'),
        xaxis=dict(title=dict(text=f'Feed {s} (wt%)', font=dict(size=10)), **_axis),
        yaxis=dict(title=dict(text='Theoretical stages', font=dict(size=10)), rangemode='tozero', **_axis),
        margin=dict(l=34, r=34, t=28, b=36),
        width=320, height=260,
        plot_bgcolor='white',
        paper_bgcolor='white',
    )
    return fig


def fig_lever_rule_interactive_feed(
    system: EquilibriumSystem,
    pt_Rn: tuple[float, float],
    pt_E1: tuple[float, float],
    pt_En1: tuple[float, float],
    mass_R0: float,
    mass_En1: float,
    pt_R0_actual: tuple[float, float],
    wpa_range: tuple[float, float] = (10.0, 55.0),
    n_steps: int = 40,
) -> go.Figure:
    """Fig 6 interactive — slider controls feed PA wt% while flow rates stay fixed.

    The real experiment is the fixed anchor, exactly like the other tabs:
    R₀ (experimental feed) and M (its real mixing point) stay put. The slider
    explores a *hypothetical* feed R₀' along the binary BP+PA edge (wW=0); only
    R₀', its mixing point M', and E₁' move. Showing the fixed M beside the
    moving M' contrasts the real operating point with the what-if one.

    Parameters
    ----------
    mass_R0, mass_En1 : float
        Experimental mass flow rates [g/min] kept constant across all frames.
    pt_R0_actual : tuple
        Experimental feed point — the fixed R₀ anchor.
    wpa_range : tuple
        (min, max) hypothetical feed PA wt% for the slider.
    """
    wpa_vals = np.linspace(wpa_range[0], wpa_range[1], n_steps)

    lb = _lb(system)
    # Real mixing point M from the experimental feed — computed once and held
    # fixed across all frames (same M as every other tab).
    pt_M_real, _ = find_M_and_P(pt_E1, pt_Rn, pt_En1, pt_R0_actual)
    # ── Static traces (real experiment — fixed anchors) ───────────────────────
    static = (
        _cart_triangle_traces(system)
        + _cart_equil_traces(system)
        + [
            _cart_point_trace(pt_Rn,        "R<sub>N</sub>",     "royalblue",  labels=lb),
            _cart_point_trace(pt_E1,        "E<sub>1</sub>",     "crimson",    labels=lb),
            _cart_point_trace(pt_En1,       "E<sub>N+1</sub>",   "crimson",    labels=lb),
            _cart_point_trace(pt_R0_actual, "R<sub>0</sub>",     "royalblue",  labels=lb),
            _cart_point_trace(pt_M_real,    "M",      "purple", symbol="diamond-open", size=10, labels=lb),
            _cart_line_trace(pt_E1,  pt_Rn,        "E<sub>1</sub>–R<sub>N</sub>",    "purple", width=1),
            _cart_line_trace(pt_En1, pt_R0_actual, "E<sub>N+1</sub>–R<sub>0</sub>",  "purple", width=1),
        ]
    )
    n_static = len(static)
    n_dynamic = 5   # R0', En1-R0' line, M', E1', Rn-E1' line

    def _dynamic(wpa: float) -> list:
        # Hypothetical binary feed point (no water): x = wbp + 0.5*wpa, y = sqrt(3)/2 * wpa
        wbp = 100.0 - wpa
        pt_R0p = (wbp + 0.5 * wpa, np.sqrt(3) / 2.0 * wpa)
        pt_Mp  = mixing_point(pt_R0p, pt_En1, mass_A=mass_R0, mass_B=mass_En1)
        pt_E1p = find_E1_prime(pt_Rn, pt_Mp, system.spline)

        r0p_tr  = _cart_point_trace(pt_R0p, "R<sub>0</sub>'", "saddlebrown", labels=lb)
        en_r0p  = _cart_line_trace(pt_En1, pt_R0p, "E<sub>N+1</sub>–R<sub>0</sub>'", "saddlebrown", width=1)
        mp_tr   = _cart_point_trace(pt_Mp,  "M'",  "saddlebrown", symbol="diamond", size=10, labels=lb)
        if pt_E1p is not None:
            e1p_tr  = _cart_point_trace(pt_E1p, "E<sub>1</sub>'", "crimson", symbol="circle-open", size=11, labels=lb)
            line_tr = _cart_line_trace(pt_Rn, pt_E1p, "R<sub>N</sub>–E<sub>1</sub>'", "saddlebrown", width=1.5)
        else:
            e1p_tr  = go.Scatter(x=[], y=[], mode="markers", showlegend=False, hoverinfo="skip")
            line_tr = go.Scatter(x=[], y=[], mode="lines",   showlegend=False, hoverinfo="skip")
        return [r0p_tr, en_r0p, mp_tr, e1p_tr, line_tr]

    fig = go.Figure(data=static + _dynamic(wpa_vals[0]))

    fig.frames = [
        go.Frame(
            data=_dynamic(wpa),
            traces=list(range(n_static, n_static + n_dynamic)),
            name=f"{wpa:.1f}",
        )
        for wpa in wpa_vals
    ]

    slider_steps = [
        dict(
            args=[[f"{wpa:.1f}"],
                  dict(frame=dict(duration=0, redraw=True), mode="immediate")],
            label=f"{wpa:.0f}%",
            method="animate",
        )
        for wpa in wpa_vals
    ]
    fig.update_layout(
        **_cart_layout(f"Lever Rule: Drag slider to adjust Feed {lb['solute']['abbr']} wt%"),
        sliders=[dict(
            active=0,
            steps=slider_steps,
            currentvalue=dict(
                prefix=f"Feed {lb['solute']['abbr']} = ",
                visible=True,
                font=dict(size=12),
            ),
            pad=dict(b=10, t=60),
            len=0.9,
            x=0.05,
            y=0,
        )],
        updatemenus=[],
    )
    fig.update_layout(height=850)
    return fig


def fig_correlation(corr, model):
    """
    corr  : one entry from compute_correlations() — keys x,y,x_fit,y_fit,a,b,r2
    model : 'ot' | 'hand' | 'bachman'
    """
    _META = {
        'ot': {
            'title': 'Othmer-Tobias correlation',
            'xlabel': 'ln[(1−w<sub>11</sub>)/w<sub>11</sub>]',
            'ylabel': 'ln[(1−w<sub>33</sub>)/w<sub>33</sub>]',
        },
        'hand': {
            'title': 'Hand correlation',
            'xlabel': 'ln(w<sub>21</sub>/w<sub>11</sub>)',
            'ylabel': 'ln(w<sub>23</sub>/w<sub>33</sub>)',
        },
        'bachman': {
            'title': 'Bachman correlation',
            'xlabel': 'w<sub>33</sub>/w<sub>11</sub>',
            'ylabel': 'w<sub>33</sub>',
        },
    }
    m = _META[model]
    _axis = dict(tickfont=dict(size=9), showgrid=False, nticks=4,
                 showline=True, linewidth=1, linecolor='#d0d5dd', mirror=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=corr['x'], y=corr['y'],
        mode='markers',
        marker=dict(color='#1878a8', size=6, line=dict(width=0.5, color='white')),
        showlegend=False,
        hovertemplate='(%{x:.3f}, %{y:.3f})<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=corr['x_fit'], y=corr['y_fit'],
        mode='lines',
        line=dict(color='#dc2626', width=1.5, dash='dash'),
        showlegend=False, hoverinfo='skip',
    ))
    fig.update_layout(
        title=dict(text=m['title'], font=dict(size=10, color='#0f2744'), x=0, xanchor='left'),
        xaxis=dict(title=dict(text=m['xlabel'], font=dict(size=10)), **_axis),
        yaxis=dict(title=dict(text=m['ylabel'], font=dict(size=10)), **_axis),
        margin=dict(l=40, r=10, t=28, b=36),
        height=330,
        plot_bgcolor='white',
        paper_bgcolor='white',
    )
    return fig


def fig_selectivity(sel):
    """
    sel: dict with keys w23, d1, d2, s (lists from compute_correlations selectivity)
    Plots S = D2/D1 vs w23 (solute mass fraction in solvent-rich phase).
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=sel['w23'], y=sel['s'],
        mode='markers',
        marker=dict(color='#1878a8', size=6, symbol='circle',
                    line=dict(width=0.5, color='white')),
        showlegend=False,
        hovertemplate='w₂₃: %{x:.4f}<br>S: %{y:.3f}<extra></extra>',
    ))
    fig.update_layout(
        title=dict(text='Selectivity S vs w<sub>23</sub>', font=dict(size=10, color='#0f2744'), x=0, xanchor='left'),
        xaxis=dict(title=dict(text='w<sub>23</sub>', font=dict(size=10)),
                   tickfont=dict(size=9), showgrid=False, nticks=4,
                   showline=True, linewidth=1, linecolor='#d0d5dd', mirror=True),
        yaxis=dict(title=dict(text='S', font=dict(size=10)),
                   tickfont=dict(size=9), showgrid=False, nticks=4, rangemode='tozero',
                   showline=True, linewidth=1, linecolor='#d0d5dd', mirror=True),
        margin=dict(l=30, r=10, t=28, b=36),
        height=300,
        plot_bgcolor='white',
        paper_bgcolor='white',
    )
    fig.add_hline(
        y=1,
        line_dash='dash',
        line_color='#9aa4b0',
        line_width=1,
        annotation_text='Plait point (S=1)',
        annotation_position='top left',
        annotation_xshift=5,
        annotation_font_size=9,
        annotation_font_color='#9aa4b0',
    )
    return fig


def fig_plait_loglog(data):
    """
    Log-log plait point determination chart.
    data: output from compute_plait_loglog()
    """
    _axis = dict(
        tickfont=dict(size=9),
        showgrid=False,
        nticks=5,
        showline=True,
        linewidth=1,
        linecolor='#d0d5dd',
        mirror=True,
        zeroline=False,
    )

    b = data['binodal']
    t = data['tieline']

    fig = go.Figure()

    # 1. Binodal spline line (no hover, no legend)
    fig.add_trace(go.Scatter(
        x=b['x_fit'], y=b['y_fit'],
        mode='lines',
        line=dict(color='black', width=1.5, dash='dash'),
        showlegend=False, hoverinfo='skip',
    ))

    # 2. Binodal points (solid black squares)
    fig.add_trace(go.Scatter(
        x=b['x'], y=b['y'],
        mode='markers',
        marker=dict(symbol='square', color='black', size=6),
        showlegend=False,
        hovertemplate='(%{x:.3f}, %{y:.3f})<extra>Equil. data</extra>',
    ))

    # 3. Tie-line linear fit (no hover, no legend)
    fig.add_trace(go.Scatter(
        x=t['x_fit'], y=t['y_fit'],
        mode='lines',
        line=dict(color='#dc2626', width=1.5, dash='dash'),
        showlegend=False, hoverinfo='skip',
    ))

    # 4. Tie-line points (filled triangles)
    fig.add_trace(go.Scatter(
        x=t['x'], y=t['y'],
        mode='markers',
        marker=dict(symbol='triangle-up', color='#1878a8', size=7),
        showlegend=False,
        hovertemplate='(%{x:.3f}, %{y:.3f})<extra>Tie-line</extra>',
    ))

    # 5. Plait point (if found)
    if data['plait'] is not None:
        p = data['plait']
        fig.add_trace(go.Scatter(
            x=[p['x']], y=[p['y']],
            mode='markers',
            marker=dict(symbol='star', color='#dc2626', size=12,
                        line=dict(color='white', width=0.5)),
            showlegend=False,
            hovertemplate='(%{x:.3f}, %{y:.3f})<extra>Plait point</extra>',
        ))

    fig.update_layout(
        # Method name lives in the chart title, matching the Othmer-Tobias
        # correlation chart (navy, size 10, left-aligned) so the Conjugate and
        # Tie-Lines panels read consistently. The section header
        # ("Plait Point Estimation") stays an HTML label in index.html.
        title=dict(text="Treybal's method in Hand coordinates",
                   font=dict(size=10, color='#0f2744'), x=0, xanchor='left'),
        xaxis=dict(title=dict(text='ln(w<sub>21</sub>/w<sub>11</sub>),  ln(w<sub>2</sub>/w<sub>1</sub>)', font=dict(size=10)), **_axis),
        yaxis=dict(title=dict(text='ln(w<sub>23</sub>/w<sub>33</sub>),  ln(w<sub>2</sub>/w<sub>3</sub>)', font=dict(size=10)), **_axis),
        height=260,
        margin=dict(l=44, r=10, t=28, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=False,
    )
    return fig
