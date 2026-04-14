from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import numpy.typing as npt
from scipy.optimize import curve_fit

from .config import MODEL_CONFIGS
from .models import MODEL_FN


# Result Dataclass for storing
@dataclass
class FitResult:
    name: str
    success: bool
    params: npt.NDArray[np.float64] | None = field(default=None, repr=False)
    cov:    npt.NDArray[np.float64] | None = field(default=None, repr=False)
    yhat:   npt.NDArray[np.float64] | None = field(default=None, repr=False)
    metrics: dict[str, float] | None = None
    error: str = ""


# Core curve fitting function

def calc_metrics(
    y_true: npt.NDArray[np.float64],
    y_pred: npt.NDArray[np.float64],
    n_params: int,
) -> dict[str, float]:
    resid = y_true - y_pred
    rss   = float(np.sum(resid ** 2))
    tss   = float(np.sum((y_true - np.mean(y_true)) ** 2))
    r2    = 1.0 - rss / tss if tss > 0 else float("nan")
    rmse  = float(np.sqrt(np.mean(resid ** 2)))
    return {"R2": r2, "RMSE": rmse, "RSS": rss}


def fit_model(
    model_func: Callable,
    x: npt.NDArray[np.float64],
    y: npt.NDArray[np.float64],
    p0: list[float],
    bounds: tuple = (-np.inf, np.inf),
    model_name: str = "model",
) -> FitResult:
    try:
        popt, pcov = curve_fit(
            model_func, x, y, p0=p0, bounds=bounds, maxfev=10000
        )
        yhat    = model_func(x, *popt)
        metrics = calc_metrics(y, yhat, len(popt))
        return FitResult(
            name=model_name, success=True,
            params=popt, cov=pcov, yhat=yhat, metrics=metrics,
        )
    except Exception as exc:
        return FitResult(name=model_name, success=False, error=str(exc))


# Run all models on the dataset

def run_all_fits(
    C: npt.NDArray[np.float64],
    q: npt.NDArray[np.float64],
    label: str = "dataset",
) -> list[FitResult]:
    results: list[FitResult] = []

    for name, cfg in MODEL_CONFIGS.items():
        p0     = list(cfg["p0"])
        bounds = cfg.get("bounds", (-np.inf, np.inf))

        if name == "Langmuir":
            p0[0] = float(max(q)) * 1.5  # qmax from the data

        results.append(
            fit_model(MODEL_FN[name], C, q, p0=p0, bounds=bounds, model_name=name)
        )

    print(f"\n===== {label} =====")
    for r in results:
        if r.success:
            print(f"\n[{r.name}]  params = {r.params}")
            for k, v in r.metrics.items():
                print(f"  {k:>5} = {v:.6f}")
        else:
            print(f"\n[{r.name}]  fit failed: {r.error}")

    return results
