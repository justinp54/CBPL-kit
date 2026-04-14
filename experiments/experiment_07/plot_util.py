from __future__ import annotations

from pathlib import Path

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt

from .fit import FitResult
from .models import MODEL_FN


def plot_fit(
    C: npt.NDArray[np.float64],
    q: npt.NDArray[np.float64],
    results: list[FitResult],
    title: str,
    save_path: Path | None = None,
    show: bool = True,
) -> None:
    """단일 온도 조건의 모든 모델 fit을 한 그래프에 표시."""
    xgrid = np.linspace(min(C) * 0.9, max(C) * 1.1, 300)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.scatter(C, q, label="data", zorder=3)

    for r in results:
        if r.success and r.name in MODEL_FN:
            ygrid = MODEL_FN[r.name](xgrid, *r.params)
            ax.plot(xgrid, ygrid, label=f"{r.name} (R²={r.metrics['R2']:.3f})")

    ax.set_xlabel(r"$C_{CO_2}$ (mol/L)")
    ax.set_ylabel(r"$q_{eq}$ (g/g-cat)")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()

    if save_path is not None:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def plot_dual_temp(
    model_name: str,
    datasets: list[tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]],
    results_list: list[list[FitResult]],
    labels: list[str],
    title: str | None = None,
    save_path: Path | None = None,
    show: bool = True,
) -> None:
    """하나의 모델에 대해 두 온도 조건 데이터와 fit을 단일 그래프에 오버레이.

    Parameters
    ----------
    model_name:   MODEL_FN 키 중 하나 ("Freundlich", "Langmuir", ...)
    datasets:     [(C_T1, q_T1), (C_T2, q_T2)]
    results_list: [run_all_fits(T1), run_all_fits(T2)]
    labels:       각 온도 레이블, e.g. ["40 °C", "50 °C"]
    title:        그래프 제목 (None이면 model_name 사용)
    """
    if model_name not in MODEL_FN:
        raise ValueError(
            f"Unknown model: {model_name!r}. Choose from {list(MODEL_FN)}"
        )

    fig, ax = plt.subplots(figsize=(7, 5))

    for (C, q), results, label in zip(datasets, results_list, labels):
        color = ax._get_lines.get_next_color()

        ax.scatter(C, q, label=label, marker="s" if "40" in label else "o",
                   color=color, zorder=3)

        r = next((r for r in results if r.name == model_name), None)
        if r is not None and r.success:
            xgrid = np.linspace(min(C) * 0.9, max(C) * 1.1, 300)
            ygrid = MODEL_FN[model_name](xgrid, *r.params)
            ax.plot(xgrid, ygrid, color=color,
                    label=f"{label} fit (R²={r.metrics['R2']:.3f})")

    ax.set_xlabel(r"$C_{CO_2}$ (mol/L)")
    ax.set_ylabel(r"$q_{eq}$ (g/g-cat)")
    ax.set_title(title if title is not None else model_name)
    ax.legend()
    fig.tight_layout()

    if save_path is not None:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
