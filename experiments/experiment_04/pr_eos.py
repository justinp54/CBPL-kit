import numpy as np
from mol_class import MoleculeClass, R
from config import PSI, OMEGA, kij
from typing import Tuple, List

_SQRT2 = np.sqrt(2)
_MAX_ITER = 300
_TEMP_UPDATE_ALPHA = 0.05
_TEMP_FACTOR_MIN = 0.95
_TEMP_FACTOR_MAX = 1.05


def component_params(
    mols: List[MoleculeClass], T: float
) -> Tuple[List[float], List[float], List[List[float]]]:
    """Compute temperature-dependent a, b parameters and cross-term matrix."""
    a = [m.calculate_a(PSI, T) for m in mols]
    b = [m.calculate_b(OMEGA) for m in mols]
    n = len(mols)
    a_ij = [
        [np.sqrt(a[i] * a[j]) * (1 - (kij if i != j else 0.0)) for j in range(n)]
        for i in range(n)
    ]
    return a, b, a_ij


def mixing_parameters(
    a: List[float], b: List[float], a_ij: List[List[float]], x: List[float]
) -> Tuple[float, float]:
    n = len(x)
    a_mix = sum(x[i] * x[j] * a_ij[i][j] for i in range(n) for j in range(n))
    b_mix = sum(x[i] * b[i] for i in range(n))
    return a_mix, b_mix


def _z_root(A: float, B: float, phase: str) -> float:
    """Solve PR EOS cubic for Z; return smallest (liquid) or largest (vapor) real root."""
    coeffs = [1, -(1 - B), A - 2 * B - 3 * B**2, -(A * B - B**2 - B**3)]
    roots = np.roots(coeffs)
    real = sorted([r.real for r in roots if abs(r.imag) < 1e-8 and r.real > B])
    if not real:
        raise RuntimeError(f"No valid {phase} Z root.")
    return real[0] if phase == "liquid" else real[-1]


def _temperature_bounds(mol1: MoleculeClass, mol2: MoleculeClass, pressure: float) -> Tuple[float, float]:
    """Return a practical temperature window to keep the bubble-point iteration stable."""
    tsat1 = mol1.T_sat(pressure)
    tsat2 = mol2.T_sat(pressure)
    if not (np.isfinite(tsat1) and np.isfinite(tsat2)):
        raise ValueError("Failed to estimate finite saturation temperatures for bounds.")

    t_min = max(1.0, 0.8 * min(tsat1, tsat2))
    t_max = 1.2 * max(tsat1, tsat2)
    if t_min >= t_max:
        raise ValueError("Invalid temperature bounds for PR EOS iteration.")
    return t_min, t_max


def fugg_coeff(
    i: int,
    x: List[float],
    a_ij: List[List[float]],    
    a: float,
    b_i: List[float],
    b: float,
    Z: float,
    A: float,
    B: float,
) -> float:
    """
    Calculate fugacity coefficient for component i using PR EOS.

    Parameters:
    i    : component index (0-based)
    x    : mole fractions [x0, x1, ...]
    a_ij : cross 'a' parameter matrix
    a    : a_mix
    b_i  : list of individual b parameters
    b    : b_mix
    Z    : compressibility factor (liquid or vapor root)
    A    : a_mix * P / (R^2 * T^2)
    B    : b_mix * P / (R * T)

    Returns:
    phi_i: fugacity coefficient for component i
    """
    sum_xa = sum(x[j] * a_ij[i][j] for j in range(len(x)))

    t1 = b_i[i] / b * (Z - 1)
    t2 = -np.log(Z - B)
    t3 = (
        -A
        / (2 * _SQRT2 * B)
        * (2 * sum_xa / a - b_i[i] / b)
        * np.log((Z + (1 + _SQRT2) * B) / (Z + (1 - _SQRT2) * B))
    )

    return np.exp(t1 + t2 + t3)


def pr_eos(
    mol1: MoleculeClass,
    mol2: MoleculeClass,
    x1: float,
    pressure: float = 1.0,
    epsilon: float = 1e-3,
) -> Tuple[float, float, List[float]]:
    """
    Calculate Bubble point temperature using Peng-Robinson EOS.

    Returns:
    T_bubble: bubble point temperature [K]
    y1      : vapor mole fraction of component 1 at bubble point
    T_arr   : temperature estimates during iteration [K]
    """
    if not 0.0 <= x1 <= 1.0:
        raise ValueError("x1 must be in [0, 1].")

    if pressure <= 0.0:
        raise ValueError("pressure must be positive.")

    x2 = 1 - x1
    mols = [mol1, mol2]
    t_min, t_max = _temperature_bounds(mol1, mol2, pressure)

    # Initial T guess from Antoine equation (already in K)
    T = mol1.T_sat(pressure) * x1 + mol2.T_sat(pressure) * x2
    T = float(np.clip(T, t_min, t_max))
    if not np.isfinite(T):
        raise ValueError("Initial temperature estimate is not finite.")

    T_arr = [T]

    # Initial K-values from Wilson correlation
    # K is the ratio of fugacity coefficients
    K1 = (mol1.Pc / pressure) * np.exp(5.373 * (1 + mol1.w) * (1 - mol1.Tc / T))
    K2 = (mol2.Pc / pressure) * np.exp(5.373 * (1 + mol2.w) * (1 - mol2.Tc / T))
    S = K1 * x1 + K2 * x2
    y1 = K1 * x1 / S
    y2 = 1 - y1

    for _ in range(_MAX_ITER):
        # Compute temperature-dependent parameters once per iteration
        a_i, b_i, a_ij = component_params(mols, T)

        # --- Liquid phase (Z_l) ---
        a_mix_L, b_mix_L = mixing_parameters(a_i, b_i, a_ij, [x1, x2])
        A_L = a_mix_L * pressure / (R**2 * T**2)
        B_L = b_mix_L * pressure / (R * T)
        Z_l = _z_root(A_L, B_L, "liquid")

        phi1_L = fugg_coeff(0, [x1, x2], a_ij, a_mix_L, b_i, b_mix_L, Z_l, A_L, B_L)
        phi2_L = fugg_coeff(1, [x1, x2], a_ij, a_mix_L, b_i, b_mix_L, Z_l, A_L, B_L)

        # --- Vapor phase (Z_v) ---
        a_mix_V, b_mix_V = mixing_parameters(a_i, b_i, a_ij, [y1, y2])
        A_V = a_mix_V * pressure / (R**2 * T**2)
        B_V = b_mix_V * pressure / (R * T)
        Z_v = _z_root(A_V, B_V, "vapor")

        phi1_V = fugg_coeff(0, [y1, y2], a_ij, a_mix_V, b_i, b_mix_V, Z_v, A_V, B_V)
        phi2_V = fugg_coeff(1, [y1, y2], a_ij, a_mix_V, b_i, b_mix_V, Z_v, A_V, B_V)

        # --- K-values and bubble point criterion ---
        K1 = phi1_L / phi1_V
        K2 = phi2_L / phi2_V

        S = K1 * x1 + K2 * x2
        if not np.isfinite(S) or S <= 0.0:
            raise RuntimeError("S became non-finite during iteration.")

        y1_prev = y1
        y1 = float(np.clip(K1 * x1 / S, 0.0, 1.0))
        y2 = 1 - y1

        if abs(S - 1.0) < epsilon and abs(y1 - y1_prev) < 5e-4:
            return T, y1, T_arr

        # S > 1: T too high -> decrease; S < 1: T too low -> increase.
        # Damped and clipped update prevents runaway jumps to non-physical high-T solutions.
        temp_factor = np.exp(-_TEMP_UPDATE_ALPHA * np.log(S))
        temp_factor = float(np.clip(temp_factor, _TEMP_FACTOR_MIN, _TEMP_FACTOR_MAX))
        T_new = float(np.clip(T * temp_factor, t_min, t_max))
        if not np.isfinite(T_new):
            raise RuntimeError("Temperature update became non-finite during iteration.")
        if abs(T_new - T) < 1e-8 and abs(S - 1.0) >= epsilon:
            raise RuntimeError("Temperature update stalled before PR EOS convergence.")

        T = T_new
        T_arr.append(T)

    raise RuntimeError(f"pr_eos did not converge within {_MAX_ITER} iterations.")


def vapor_composition_at_bubble(
    mol1: MoleculeClass,
    mol2: MoleculeClass,
    x1: float,
    pressure: float = 1.0,
    epsilon: float = 1e-3,
) -> float:
    """Return vapor composition y1 at bubble point for a given liquid composition x1."""
    _, y1, _ = pr_eos(mol1, mol2, x1, pressure=pressure, epsilon=epsilon)
    return y1


def build_xy_data(
    mol1: MoleculeClass,
    mol2: MoleculeClass,
    x1_list: List[float],
    pressure: float = 1.0,
) -> Tuple[List[float], List[float]]:
    """Compute x-y VLE data from PR EOS results."""
    x_data = sorted(x1_list)
    y_data: List[float] = [
        vapor_composition_at_bubble(mol1, mol2, x1, pressure=pressure)
        for x1 in x_data
    ]
    return x_data, y_data