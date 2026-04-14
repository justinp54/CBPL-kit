from __future__ import annotations

import numpy as np
import numpy.typing as npt

# ---------------------------------------------------------------------------
# Adsorption isotherm model functions  (pure, no global state)
# ---------------------------------------------------------------------------

def freundlich(
    C: npt.NDArray[np.float64],
    Kf: float,
    n: float,
) -> npt.NDArray[np.float64]:
    return Kf * (C ** (1.0 / n))


def langmuir(
    C: npt.NDArray[np.float64],
    qmax: float,
    b: float,
) -> npt.NDArray[np.float64]:
    return (qmax * b * C) / (1.0 + b * C)


def temkin(
    C: npt.NDArray[np.float64],
    A: float,
    B: float,
) -> npt.NDArray[np.float64]:
    return B * np.log(A * C)


def log_model(
    C: npt.NDArray[np.float64],
    a: float,
    b: float,
) -> npt.NDArray[np.float64]:
    return a + b * np.log(C)


# ---------------------------------------------------------------------------
# Name → callable mapping  (used by fit.py and plot_util.py)
# ---------------------------------------------------------------------------
MODEL_FN: dict[str, object] = {
    "Freundlich":    freundlich,
    "Langmuir":      langmuir,
    "Temkin":        temkin,
    "Empirical log": log_model,
}
