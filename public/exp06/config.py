"""
Experiment 06 — system constants loaded from systems/bp_pa_w_snu_cbe.yaml.

To change the ternary system, edit (or replace) that YAML file.
To change titration/flow defaults, edit the values at the bottom of this file
or override them in the web sidebar.
"""
from __future__ import annotations

import numpy as np
import yaml
from pathlib import Path

_path = Path(__file__).parent / "systems" / "bp_pa_w_snu_cbe.yaml"
_d    = yaml.safe_load(_path.read_text())
_p    = _d["properties"]

# Thermodynamic / physical data (from YAML)
EQUIL_DATA: np.ndarray               = np.array(_d["equilibrium_data"], dtype=float)
TIE_DATA:   list[tuple[float, float]] = [tuple(float(v) for v in r) for r in _d["tie_lines"]]

RHO_BP: float = float(_p["rho_carrier"])   # g/mL  — n-BP (feed carrier) density
RHO_PA: float = float(_p["rho_solute"])    # g/mL  — solute density
RHO_W:  float = float(_p["rho_solvent"])   # g/mL  — Water (extracting solvent) density
MW_PA:  float = float(_p["mw_solute"])     # g/mol — solute molar mass (NaOH titration)

# Supplementary constants (not in YAML, not used in core calculations)
MW_BP: float = 122.99   # g/mol — n-Bromopropane
MW_W:  float = 18.015   # g/mol — Water

# Titration protocol — override with your actual setup
C_NAOH:       float = 0.5    # mol/L — NaOH titrant concentration
V_ALIQUOT_ML: float = 10.0   # mL    — sample aliquot volume titrated

# Experiment defaults — override with your actual titration results
V_R0: float = 10.78   # feed   (10× diluted) [mL]
V_E1: float = 3.80    # first extract (10× diluted) [mL]
V_RN: float = 0.64    # raffinate (undiluted) [mL]

F_R0: float = 10.0   # feed dilution factor
F_E1: float = 10.0   # first extract dilution factor
F_RN: float = 1.0    # raffinate dilution factor (undiluted)

FLOW_SOLVENT_ML_MIN: float = 100.0   # pure water (solvent) [mL/min]
FLOW_FEED_ML_MIN:    float = 40.0    # feed stream [mL/min]


def conc_from_titration(v_naoh_mL: float, f: float = 1.0) -> float:
    """NaOH titration volume → solute molar concentration [mol/L].

    C = C_NAOH · V_NaOH · f / V_ALIQUOT_ML, where f is the dilution factor,
    assuming 1:1 acid-base neutralization. Reads C_NAOH / V_ALIQUOT_ML at
    call time so runtime overrides (config.C_NAOH = ...) from the web
    sidebar take effect.
    """
    return C_NAOH * float(v_naoh_mL) * float(f) / V_ALIQUOT_ML


def conc_from_wt_percent(w_solute: float) -> float:
    """Solute wt% in the FEED -> solute molar concentration [mol/L].

    The feed carries no solvent, so it is a binary carrier + solute mixture and
    volume additivity inverts in closed form -- no iteration. The warning in
    AGENTS.md about the density depending on the sample's own solute content
    applies to a free ternary composition; here, and on the binodal curve, one
    number already fixes the whole composition.

    This is the exact inverse of the wpa_R0 line in compute_stream_points:
        w/100 = c.M / (c.M + rho_c.(1000 - c.M/rho_s))
    Densities are read at call time so a system switch (which rewrites
    config.RHO_BP etc.) takes effect.
    """
    k = float(w_solute) / 100.0
    if not 0.0 <= k < 1.0:
        raise ValueError(
            f"Feed solute fraction {w_solute:.3f} wt% is outside 0-100 wt%."
        )
    return 1000.0 * k * RHO_BP / (MW_PA * (1.0 - k * (1.0 - RHO_BP / RHO_PA)))


#: How a stream's solute content was measured. The web sidebar picks one for
#: all three streams; the signature below takes it per stream so that showing
#: a per-stream choice later is a user-interface change only.
INPUT_MODES = ("titration", "wt_percent", "molar")


def solute_concentration(
    mode: str,
    value: float,
    *,
    f: float = 1.0,
    system=None,
    left: bool | None = None,
) -> float:
    """A stream's solute molar concentration [mol/L], however it was measured.

    Everything downstream of this -- the stream points, the construction, the
    stage count -- speaks molar concentration, so the three input modes only
    have to meet here.

    mode   "titration" (value is the NaOH titre in mL), "wt_percent", or "molar"
    f      dilution factor, titration only
    left   None for the feed, which is a binary carrier + solute mixture;
           True for the extract and False for the raffinate, which lie on the
           binodal curve and need the system to place a wt% on it
    """
    if mode not in INPUT_MODES:
        raise ValueError(f"Unknown input mode {mode!r}; expected one of {INPUT_MODES}.")
    if mode == "titration":
        return conc_from_titration(value, f)
    if mode == "molar":
        return float(value)
    if left is None:
        return conc_from_wt_percent(value)
    if system is None:
        raise ValueError(
            "A wt% on the binodal curve needs the system to place it; "
            "pass system= for the extract and the raffinate."
        )
    return system.concentration_from_wt_percent(value, left=left)
