"""
Experiment 06 -- LLE Hunter-Nash Method
System: n-Bromopropane / Propionic Acid / Water

Run this file directly:
    python experiments/experiment_06/main.py

Or from the package:
    from experiments.experiment_06 import main
    main(output_dir="experiments/experiment_06/outputs")
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    from . import plot_util
    from .config import (
        F_E1,
        F_R0,
        F_RN,
        FLOW_FEED_ML_MIN,
        FLOW_SOLVENT_ML_MIN,
        MW_PA,
        RHO_BP,
        RHO_PA,
        RHO_W,
        V_E1,
        V_R0,
        V_RN,
        conc_from_titration,
    )
    from .conjugate import ConjugateCurve
    from .equilibrium import EquilibriumSystem
    from .hunter_nash import HunterNashSolver
    from .lever_rule import find_E1_prime, find_M_and_P, mixing_point
    from .ternary import comp_to_xy, xy_to_comp
except ImportError:
    import plot_util
    from config import (
        F_E1,
        F_R0,
        F_RN,
        FLOW_FEED_ML_MIN,
        FLOW_SOLVENT_ML_MIN,
        MW_PA,
        RHO_BP,
        RHO_PA,
        RHO_W,
        V_E1,
        V_R0,
        V_RN,
        conc_from_titration,
    )
    from conjugate import ConjugateCurve
    from equilibrium import EquilibriumSystem
    from hunter_nash import HunterNashSolver
    from lever_rule import find_E1_prime, find_M_and_P, mixing_point
    from ternary import comp_to_xy, xy_to_comp


# ---------------------------------------------------------------------------
# Stream-point computation from titration
# ---------------------------------------------------------------------------

@dataclass
class StreamPoints:
    """Cartesian coordinates and feed composition derived from titration data."""
    pt_R0:  tuple[float, float]   # feed (BP-rich, no water)
    pt_E1:  tuple[float, float]   # first extract (water-rich branch)
    pt_Rn:  tuple[float, float]   # final raffinate (BP-rich branch)
    pt_En1: tuple[float, float]   # pure solvent inlet (n-BP vertex)
    wpa_R0: float                 # PA wt% in feed
    wbp_R0: float                 # n-BP wt% in feed


def compute_stream_points(system: EquilibriumSystem) -> StreamPoints:
    """Derive R0, E1, Rn Cartesian coordinates from titration results in config.py."""
    c_R0 = conc_from_titration(V_R0, F_R0)
    c_E1 = conc_from_titration(V_E1, F_E1)
    c_Rn = conc_from_titration(V_RN, F_RN)

    # R0: binary BP+PA (no water); solve for wpa from molar concentration
    denom = c_R0 * MW_PA + RHO_BP * (1000.0 - c_R0 * MW_PA / RHO_PA)
    wpa_R0 = c_R0 * MW_PA / denom * 100.0
    wbp_R0 = 100.0 - wpa_R0
    pt_R0 = comp_to_xy(wbp_R0, wpa_R0)

    # E1: water-rich branch (left); Rn: BP-rich branch (right)
    pt_E1, comp_E1, cpa_E1 = system.find_curve_point_by_concentration(c_E1, left=True)
    pt_Rn, comp_Rn, cpa_Rn = system.find_curve_point_by_concentration(c_Rn, left=False)

    # Pure solvent En+1 at the n-BP vertex
    pt_En1 = (0.0, 0.0)

    print("STREAM POINTS")
    print(f"  c_PA [M]:  feed={c_R0:.3f}  extract={c_E1:.3f}  raffinate={c_Rn:.3f}")
    print(f"  R0   wPA={wpa_R0:.2f}%  wBP={wbp_R0:.2f}%  wW=0%")
    print(f"  E1   wPA={comp_E1[0]:.2f}%  wBP={comp_E1[1]:.2f}%  wW={comp_E1[2]:.2f}%"
          f"  (c_calc={cpa_E1:.3f} M)")
    print(f"  Rn   wPA={comp_Rn[0]:.2f}%  wBP={comp_Rn[1]:.2f}%  wW={comp_Rn[2]:.2f}%"
          f"  (c_calc={cpa_Rn:.3f} M)")
    return StreamPoints(
        pt_R0=pt_R0,
        pt_E1=pt_E1,
        pt_Rn=pt_Rn,
        pt_En1=pt_En1,
        wpa_R0=wpa_R0,
        wbp_R0=wbp_R0,
    )


def compute_mass_flows(wpa_R0: float, wbp_R0: float) -> tuple[float, float]:
    """Mass flow rates [g/min]: (solvent En1, feed R0).

    En1 is pure solvent, so it takes RHO_W, not the carrier density. Getting
    this wrong inflates the solvent mass, which slides the mixture point M
    toward the solvent vertex and corrupts S/F and the stage count with it.
    """
    mass_En1 = FLOW_SOLVENT_ML_MIN * RHO_W
    vol_per_g = wpa_R0 / 100.0 / RHO_PA + wbp_R0 / 100.0 / RHO_BP
    mass_R0 = FLOW_FEED_ML_MIN / vol_per_g
    return mass_En1, mass_R0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(output_dir: str | Path = ".") -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Thermodynamic models ──────────────────────────────────────────────
    print("Building equilibrium system...", flush=True)
    system = EquilibriumSystem()
    print(f"  x-intercepts (spline): {system.x_intercepts}")

    print("Building conjugate curve...")
    conjugate = ConjugateCurve(system)
    pp_wpa, pp_wbp, pp_ww = xy_to_comp(*conjugate.pt_plait)
    print(f"  Plait point: PA={pp_wpa:.2f}%  n-BP={pp_wbp:.2f}%  Water={pp_ww:.2f}%")
    print()

    # ── Stream points ─────────────────────────────────────────────────────
    sp = compute_stream_points(system)

    # ── Operating points M and P ──────────────────────────────────────────
    pt_M, pt_P = find_M_and_P(sp.pt_E1, sp.pt_Rn, sp.pt_En1, sp.pt_R0)
    print("\nOperating points")
    print(f"  M = ({pt_M[0]:.3f}, {pt_M[1]:.3f})")
    print(f"  P = ({pt_P[0]:.3f}, {pt_P[1]:.3f})")

    # ── Hunter-Nash stepping ──────────────────────────────────────────────
    print("\nRunning Hunter-Nash stepping...")
    solver = HunterNashSolver(system, conjugate, pt_P, sp.pt_E1, sp.pt_Rn)
    steps, N_theory = solver.solve()
    print(f"  N_theoretical = {N_theory}")
    for s in steps:
        print(f"    Stage {s.index}: E (PA={s.comp_E[0]:.2f}%) -> R (PA={s.comp_R[0]:.2f}%)")

    # ── Lever-rule variants ───────────────────────────────────────────────
    mass_En1, mass_R0 = compute_mass_flows(sp.wpa_R0, sp.wbp_R0)
    print(f"\nMass flows  En1={mass_En1:.1f} g/min  R0={mass_R0:.1f} g/min")

    # Fig 4: experimental flow ratio
    pt_Mp_exp = mixing_point(sp.pt_R0, sp.pt_En1, mass_R0, mass_En1)
    pt_E1p_exp = find_E1_prime(sp.pt_Rn, pt_Mp_exp, system.spline)

    # Fig 5(a): solvent:feed weight ratio = 80:20
    pt_Mp_80 = mixing_point(sp.pt_R0, sp.pt_En1, mass_A=0.20, mass_B=0.80)
    pt_E1p_80 = find_E1_prime(sp.pt_Rn, pt_Mp_80, system.spline)

    # Fig 5(b): solvent:feed weight ratio = 55:45
    pt_Mp_55 = mixing_point(sp.pt_R0, sp.pt_En1, mass_A=0.45, mass_B=0.55)
    pt_E1p_55 = find_E1_prime(sp.pt_Rn, pt_Mp_55, system.spline)

    # Fig 6(a): hypothetical feed at 40 wt% PA (actual flow rates)
    pt_R0_40 = comp_to_xy(60.0, 40.0)
    pt_Mp_40 = mixing_point(pt_R0_40, sp.pt_En1, mass_R0, mass_En1)
    pt_E1p_40 = find_E1_prime(sp.pt_Rn, pt_Mp_40, system.spline)

    # Fig 6(b): hypothetical feed at 25 wt% PA (actual flow rates)
    pt_R0_25 = comp_to_xy(75.0, 25.0)
    pt_Mp_25 = mixing_point(pt_R0_25, sp.pt_En1, mass_R0, mass_En1)
    pt_E1p_25 = find_E1_prime(sp.pt_Rn, pt_Mp_25, system.spline)

    # ── Generate figures ──────────────────────────────────────────────────
    print("\nGenerating figures...")

    figures = {
        "fig1_ternary_equilibrium.html": plot_util.fig_ternary_equilibrium(system),
        "fig2a_conjugate_curve.html":    plot_util.fig_conjugate_curve(system, conjugate),
        "fig2b_interpolated_tie_lines.html": plot_util.fig_interpolated_tie_lines(
            system, conjugate, steps, N_theory
        ),
        "fig3_hunter_nash.html": plot_util.fig_hunter_nash(
            system, steps, N_theory, sp.pt_R0, sp.pt_Rn, sp.pt_E1, sp.pt_En1, pt_P
        ),
        "fig4_lever_rule_exp.html": plot_util.fig_lever_rule(
            system, sp.pt_R0, sp.pt_Rn, sp.pt_E1, sp.pt_En1, pt_M, pt_Mp_exp, pt_E1p_exp,
            title="Fig 4 -- Lever Rule (Experimental Flow Ratio)",
        ),
        "fig5a_solvent_feed_80_20.html": plot_util.fig_lever_rule(
            system, sp.pt_R0, sp.pt_Rn, sp.pt_E1, sp.pt_En1, pt_M, pt_Mp_80, pt_E1p_80,
            title="Fig 5(a) -- Solvent : Feed = 80 : 20",
        ),
        "fig5b_solvent_feed_55_45.html": plot_util.fig_lever_rule(
            system, sp.pt_R0, sp.pt_Rn, sp.pt_E1, sp.pt_En1, pt_M, pt_Mp_55, pt_E1p_55,
            title="Fig 5(b) -- Solvent : Feed = 55 : 45",
        ),
        "fig6a_feed_40pct_PA.html": plot_util.fig_lever_rule(
            system, pt_R0_40, sp.pt_Rn, sp.pt_E1, sp.pt_En1, pt_M, pt_Mp_40, pt_E1p_40,
            title="Fig 6(a) -- Hypothetical Feed: 40 wt% PA",
            pt_R0_actual=sp.pt_R0,
        ),
        "fig6b_feed_25pct_PA.html": plot_util.fig_lever_rule(
            system, pt_R0_25, sp.pt_Rn, sp.pt_E1, sp.pt_En1, pt_M, pt_Mp_25, pt_E1p_25,
            title="Fig 6(b) -- Hypothetical Feed: 25 wt% PA",
            pt_R0_actual=sp.pt_R0,
        ),
        "fig_lever_rule_interactive.html": plot_util.fig_lever_rule_interactive(
            system, sp.pt_R0, sp.pt_Rn, sp.pt_E1, sp.pt_En1, pt_M,
        ),
        "fig_lever_rule_interactive_feed.html": plot_util.fig_lever_rule_interactive_feed(
            system, sp.pt_Rn, sp.pt_E1, sp.pt_En1,
            mass_R0, mass_En1, sp.pt_R0,
        ),
    }

    for fname, fig in figures.items():
        path = output_dir / fname
        fig.write_html(str(path))
        print(f"  {path}")

    print("\nDone. Open any .html file in a browser for interactive plots.")


if __name__ == "__main__":
    main(output_dir=Path(__file__).parent / "outputs")
