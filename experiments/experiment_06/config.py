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
