import numpy as np

# System: n-Bromopropane (bp) / Propionic Acid (pa) / Water (w)

# Equilibrium data [wbp wt%, wpa wt%, ww wt%]
EQUIL_DATA = np.array([
    [ 5.100,  9.490, 85.410],
    [ 8.370, 36.650, 54.980],
    [17.670, 49.400, 32.930],
    [32.724, 49.087, 18.189],
    [56.740, 37.830,  5.430],
    [84.180,  9.350,  6.470],
])

# Tie-line data [(wpa in water-rich phase, wpa in bp-rich phase)] wt%
TIE_DATA: list[tuple[float, float]] = [
    (6.253,  2.564),
    (8.020,  2.650),
    (8.291,  3.058),
    (14.175, 8.047),
    (16.730, 9.880),
    (26.069, 19.418),
]

# Physical properties
RHO_BP: float = 1.354   # g/mL
RHO_PA: float = 0.993   # g/mL
RHO_W:  float = 1.000   # g/mL
MW_BP:  float = 122.99  # g/mol
MW_PA:  float = 74.08   # g/mol
MW_W:   float = 18.015  # g/mol

# Titration results (0.5 M NaOH; diluted 10x for R0 and E1, undiluted for Rn)
# c [mol/L] = 0.05 * v[mL]  (undiluted); multiply by 10 for 10x-diluted samples
V_R0: float = 10.78  # feed   (10x diluted) [mL]
V_E1: float = 3.80   # extract (10x diluted) [mL]
V_RN: float = 0.64   # raffinate (undiluted) [mL]

# Operating flow rates
FLOW_SOLVENT_ML_MIN: float = 100.0  # pure n-BP solvent [mL/min]
FLOW_FEED_ML_MIN:    float = 40.0   # feed [mL/min]
