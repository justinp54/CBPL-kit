"""
Vercel serverless handler for LLE Hunter-Nash computation.

POST /api/compute
Body:  {"V_R0": 10.78, "V_E1": 3.80, "V_RN": 0.64,
        "flow_solvent": 100.0, "flow_feed": 40.0}
Returns: Plotly JSON figures + computed values
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — works both locally and on Vercel
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from experiments.experiment_06.config import (
    RHO_BP, RHO_PA, RHO_W, MW_PA,
)
from experiments.experiment_06.equilibrium import EquilibriumSystem
from experiments.experiment_06.conjugate import ConjugateCurve
from experiments.experiment_06.hunter_nash import HunterNashSolver
from experiments.experiment_06.lever_rule import (
    find_M_and_P, mixing_point, find_E1_prime,
)
from experiments.experiment_06.ternary import comp_to_xy, xy_to_comp
from experiments.experiment_06 import plot_util


# ---------------------------------------------------------------------------
# Defaults (used when a field is missing from the request body)
# ---------------------------------------------------------------------------
_DEFAULTS = {
    "V_R0": 10.78,
    "V_E1": 3.80,
    "V_RN": 0.64,
    "flow_solvent": 100.0,
    "flow_feed": 40.0,
}

_BOUNDS = {
    "V_R0":         (0.5,  40.0),
    "V_E1":         (0.1,  20.0),
    "V_RN":         (0.01,  5.0),
    "flow_solvent": (5.0, 500.0),
    "flow_feed":    (5.0, 300.0),
}


def _validate(body: dict) -> dict:
    out: dict = {}
    for key, default in _DEFAULTS.items():
        raw = body.get(key, default)
        try:
            val = float(raw)
        except (TypeError, ValueError):
            val = default
        lo, hi = _BOUNDS[key]
        out[key] = max(lo, min(hi, val))
    return out


def _titration_c(v_mL: float, diluted_10x: bool) -> float:
    """0.5 M NaOH titration volume [mL] → PA molar concentration [mol/L]."""
    return 0.05 * v_mL * (10.0 if diluted_10x else 1.0)


# ---------------------------------------------------------------------------
# Core computation — no global state touched
# ---------------------------------------------------------------------------
def _compute(inp: dict) -> dict:
    system    = EquilibriumSystem()
    conjugate = ConjugateCurve(system)

    # Titration concentrations
    c_R0 = _titration_c(inp["V_R0"], diluted_10x=True)
    c_E1 = _titration_c(inp["V_E1"], diluted_10x=True)
    c_Rn = _titration_c(inp["V_RN"], diluted_10x=False)

    # Feed (binary BP+PA, no water)
    denom  = c_R0 * MW_PA + RHO_BP * (1000.0 - c_R0 * MW_PA / RHO_PA)
    wpa_R0 = c_R0 * MW_PA / denom * 100.0
    wbp_R0 = 100.0 - wpa_R0
    pt_R0  = comp_to_xy(wbp_R0, wpa_R0)

    # Extract / raffinate on equilibrium curve
    pt_E1,  comp_E1, cpa_E1 = system.find_curve_point_by_concentration(c_E1, left=True)
    pt_Rn,  comp_Rn, cpa_Rn = system.find_curve_point_by_concentration(c_Rn, left=False)
    pt_En1 = (0.0, 0.0)

    # Operating points
    pt_M, pt_P = find_M_and_P(pt_E1, pt_Rn, pt_En1, pt_R0)

    # Hunter-Nash stages
    solver = HunterNashSolver(system, conjugate, pt_P, pt_E1, pt_Rn)
    steps, N_theory = solver.solve()

    # Mass flows
    mass_En1   = inp["flow_solvent"] * RHO_BP
    vol_per_g  = wpa_R0 / 100.0 / RHO_PA + wbp_R0 / 100.0 / RHO_BP
    mass_R0_gm = inp["flow_feed"] / vol_per_g

    # Lever rule — experimental flow ratio
    pt_Mp_exp  = mixing_point(pt_R0, pt_En1, mass_R0_gm, mass_En1)
    pt_E1p_exp = find_E1_prime(pt_Rn, pt_Mp_exp, system.spline)

    # Plait point composition
    pp = xy_to_comp(*conjugate.pt_plait)

    # All figures as Plotly JSON
    figures = {
        "fig1":  plot_util.fig_ternary_equilibrium(system).to_json(),
        "fig2a": plot_util.fig_conjugate_curve(system, conjugate).to_json(),
        "fig2b": plot_util.fig_interpolated_tie_lines(
            system, conjugate, steps, N_theory
        ).to_json(),
        "fig3": plot_util.fig_hunter_nash(
            system, steps, N_theory,
            pt_R0, pt_Rn, pt_E1, pt_En1, pt_P,
        ).to_json(),
        "fig4": plot_util.fig_lever_rule(
            system, pt_R0, pt_Rn, pt_E1, pt_En1,
            pt_M, pt_Mp_exp, pt_E1p_exp,
            title="Lever Rule — Experimental Flow Ratio",
        ).to_json(),
        "fig_sf": plot_util.fig_lever_rule_interactive(
            system, pt_R0, pt_Rn, pt_E1, pt_En1, pt_M,
        ).to_json(),
        "fig_feed": plot_util.fig_lever_rule_interactive_feed(
            system, pt_Rn, pt_E1, pt_En1,
            mass_R0=mass_R0_gm,
            mass_En1=mass_En1,
            pt_R0_actual=pt_R0,
        ).to_json(),
    }

    def _r(v: float) -> float:
        return round(float(v), 2)

    def _comp(wpa, wbp, ww):
        return {"wpa": _r(wpa), "wbp": _r(wbp), "ww": _r(ww)}

    return {
        "success":    True,
        "N_theory":   N_theory,
        "plait_point": _comp(*pp),
        "stream_points": {
            "R0":  _comp(wpa_R0, wbp_R0, 0.0),
            "E1":  _comp(*comp_E1),
            "Rn":  _comp(*comp_Rn),
            "En1": _comp(0.0, 100.0, 0.0),
        },
        "concentrations": {
            "c_R0": _r(c_R0),
            "c_E1": _r(c_E1),
            "c_Rn": _r(c_Rn),
        },
        "mass_flows": {
            "solvent_g_min": _r(mass_En1),
            "feed_g_min":    _r(mass_R0_gm),
        },
        "stages": [
            {
                "index": s.index,
                "E": _comp(*s.comp_E),
                "R": _comp(*s.comp_R),
            }
            for s in steps[:N_theory]
        ],
        "figures": figures,
    }


# ---------------------------------------------------------------------------
# Vercel HTTP handler
# ---------------------------------------------------------------------------
class handler(BaseHTTPRequestHandler):
    def _send_cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_cors()
        self.end_headers()

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", 0))
            body   = json.loads(self.rfile.read(length)) if length else {}
            inp    = _validate(body)
            result = _compute(inp)
        except Exception as exc:
            result = {"success": False, "error": str(exc)}

        payload = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self._send_cors()
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args) -> None:  # silence default stdout logs
        pass
