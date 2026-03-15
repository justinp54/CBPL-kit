"""Shared configuration for experiment 04."""

from mol_class import MoleculeClass

# --- Experimental input ---
x1_list = [
    0.1112,
    0.1558,
    0.2815,
    0.3268,
]  # liquid mole fraction of acetone [Sample 1-4]
P = 1.0  # constant pressure [bar]

# --- Physical constants ---
R = 0.08314462  # ideal gas constant [bar·L/mol·K]
kij = 0.0  # PR EOS binary interaction parameter

# --- Component properties ---
ACETONE = {
    "A": 4.42448,
    "B": 1312.253,
    "C": -32.445,
    "Tc": 508.1,
    "Pc": 47.0,
    "w": 0.304,
}

ISOPROPANOL = {
    "A": 4.8610,
    "B": 1357.427,
    "C": -75.814,
    "Tc": 508.3,
    "Pc": 47.6,
    "w": 0.665,
}


def build_components() -> tuple[MoleculeClass, MoleculeClass]:
    """Create molecule objects for this experiment."""
    acetone = MoleculeClass(**ACETONE)
    isopropanol = MoleculeClass(**ISOPROPANOL)
    return acetone, isopropanol


acetone, isopropanol = build_components()
