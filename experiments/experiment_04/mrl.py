import numpy as np
from mol_class import MoleculeClass


def modified_raoult(
    mol1: MoleculeClass,
    mol2: MoleculeClass,
    x1: float,
    pressure: float = 1.0,
    epsilon: float = 1e-3,
) -> tuple[float, list[float]]:
    """
    Calculate Bubble point temperature using modified Raoult's law

    Parameters:
    mol1: MoleculeClass
    mol2: MoleculeClass
    x1: float - mole fraction of component 1 (acetone)

    Returns:
    T: float - bubble point temperature [K]
    T_arr: List[float] - list of temperature estimates during iteration
    """

    if not 0.0 <= x1 <= 1.0:
        raise ValueError("x1 must be in [0, 1].")

    if pressure <= 0.0:
        raise ValueError("pressure must be positive.")

    x2 = 1 - x1

    T_sat1 = mol1.T_sat(pressure)
    T_sat2 = mol2.T_sat(pressure)

    T_i = T_sat1 * x1 + T_sat2 * x2  # initial guess for T
    if not np.isfinite(T_i):
        raise ValueError("Initial temperature estimate is not finite.")
    T = T_i
    T_arr = [T]

    for _ in range(200):
        P_sat1 = mol1.P_sat(T)
        P_sat2 = mol2.P_sat(T)

        # activity coefficient
        A = 2.771 - 0.00523 * T
        gamma1 = mol1.gamma(x1, A)
        gamma2 = mol2.gamma(x2, A)

        if (
            P_sat1 <= 0.0
            or not np.isfinite(P_sat1)
            or P_sat2 <= 0.0
            or not np.isfinite(P_sat2)
        ):
            raise RuntimeError(
                "Encountered non-physical saturation pressure during iteration."
            )

        denom = gamma1 * x1 + gamma2 * x2 * P_sat2 / P_sat1
        if denom <= 0.0 or not np.isfinite(denom):
            raise RuntimeError(
                "Encountered invalid denominator in modified Raoult iteration."
            )

        P_sat1 = pressure / denom
        if P_sat1 <= 0.0 or not np.isfinite(P_sat1):
            raise RuntimeError(
                "Encountered non-physical updated saturation pressure during iteration."
            )

        T_new = mol1.B / (mol1.A - np.log10(P_sat1)) - mol1.C
        if not np.isfinite(T_new):
            raise RuntimeError("Temperature update became non-finite during iteration.")
        T_arr.append(T_new)
        if abs(T_new - T) < epsilon:
            return T_new, T_arr
        T = T_new

    raise RuntimeError("modified_Raoult did not converge within 200 iterations.")


def vapor_composition_at_bubble(
    mol1: MoleculeClass,
    mol2: MoleculeClass,
    x1: float,
    pressure: float = 1.0,
    epsilon: float = 1e-3,
) -> float:
    """
    Return vapor composition y1 at bubble point for a given liquid composition x1.
    
    Parameters:
    mol1: MoleculeClass
    mol2: MoleculeClass
    x1: float - mole fraction of component 1
    pressure: float - system pressure [bar]
    epsilon: float - convergence criterion
    
    Returns:
    y1: float - vapor mole fraction of component 1 at bubble point
    """
    t_bubble, _ = modified_raoult(
        mol1,
        mol2,
        x1,
        pressure=pressure,
        epsilon=epsilon,
    )

    x2 = 1.0 - x1
    A = 2.771 - 0.00523 * t_bubble
    gamma1 = mol1.gamma(x1, A)
    gamma2 = mol2.gamma(x2, A)

    p_sat1 = mol1.P_sat(t_bubble)
    p_sat2 = mol2.P_sat(t_bubble)

    k1 = gamma1 * p_sat1 / pressure
    k2 = gamma2 * p_sat2 / pressure
    denom = x1 * k1 + x2 * k2
    if denom <= 0.0 or not np.isfinite(denom):
        raise RuntimeError(
            "Encountered invalid denominator while computing vapor composition."
        )

    y1 = (x1 * k1) / denom
    y1 = float(np.clip(y1, 0.0, 1.0))

    return y1


def build_xy_data(
    mol1: MoleculeClass,
    mol2: MoleculeClass,
    x1_list: list[float],
    pressure: float = 1.0,
) -> tuple[list[float], list[float]]:
    """
    Compute x-y VLE data from modified Raoult results.
    Takes a list of liquid compositions and returns corresponding vapor compositions.
    """
    x_data = sorted(x1_list)
    y_data: list[float] = [
        vapor_composition_at_bubble(mol1, mol2, x1, pressure=pressure)
        for x1 in x_data
    ]
    return x_data, y_data
