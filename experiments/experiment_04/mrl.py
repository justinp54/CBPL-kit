import numpy as np
import mol_class
from typing import Tuple, List


def modified_raoult(
    mol1: mol_class.MoleculeClass,
    mol2: mol_class.MoleculeClass,
    x1: float,
) -> Tuple[float, List[float]]:
    """
    Calculate Bubble point temperature using modified Raoult's law

    Parameters:
    mol1: MoleculeClass
    mol2: MoleculeClass
    x1: float - mole fraction of component 1 (acetone)

    Returns:
    T: float - bubble point temperature [°C]
    T_arr: List[float] - list of temperature estimates during iteration
    """

    if not 0.0 <= x1 <= 1.0:
        raise ValueError("x1 must be in [0, 1].")

    x2 = 1 - x1

    P = 1.0  # bar
    T_sat1 = mol1.T_sat(P)
    T_sat2 = mol2.T_sat(P)

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
        gamma1 = mol1.gamma(x1, A, T)
        gamma2 = mol2.gamma(x2, A, T)

        P_sat1 = P / (gamma1 * x1 + gamma2 * x2 * P_sat2 / P_sat1)
        T_new = mol1.B / (mol1.A - np.log10(P_sat1)) - mol1.C
        T_arr.append(T_new)
        if abs(T_new - T) < 1e-2:
            return T_new, T_arr
        T = T_new

    raise RuntimeError("modified_Raoult did not converge within 200 iterations.")
