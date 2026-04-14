import numpy as np
import numpy.typing as npt

# Raw data (C, q)for 
C40_RAW: npt.NDArray[np.float64] = np.array([0.00114, 0.00258, 0.00367, 0.00490])
q40_RAW: npt.NDArray[np.float64] = np.array([0.0091,  0.0186,  0.0161,  0.0249])

C50: npt.NDArray[np.float64] = np.array([0.00139, 0.00271, 0.00395, 0.00534])
q50: npt.NDArray[np.float64] = np.array([0.0096,  0.0151,  0.0186,  0.0205])

# 40 °C — outlier at index 2 excluded
MASK40: npt.NDArray[np.bool_] = np.array([True, True, False, True])
C40: npt.NDArray[np.float64] = C40_RAW[MASK40]
q40: npt.NDArray[np.float64] = q40_RAW[MASK40]

# ---------------------------------------------------------------------------
# Model fitting configuration  (p0, bounds passed to scipy.optimize.curve_fit)
# ---------------------------------------------------------------------------
MODEL_CONFIGS: dict[str, dict] = {
    "Freundlich": {
        "p0":     [0.1, 2.0],
        "bounds": ([0, 0], [np.inf, np.inf]),
    },
    "Langmuir": {
        # p0[0] (qmax) is overridden at runtime from max(q)*1.5
        "p0":     [None, 100.0],
        "bounds": ([0, 0], [np.inf, np.inf]),
    },
    "Temkin": {
        "p0":     [1000.0, 0.01],
        "bounds": ([1e-12, 0], [np.inf, np.inf]),
    },
    "Empirical log": {
        "p0":     [0.0, 0.01],
        "bounds": (-np.inf, np.inf),
    },
}
