"""
Experiment 07 -- CO2 Adsorption Isotherm Fitting
System: CO2 / catalyst at 40 °C and 50 °C

Run directly:
    python -m experiments.experiment_07

Or from Jupyter:
    from experiments.experiment_07 import run_all_fits, plot_fit, plot_dual_temp
    import experiments.experiment_07.config as cfg

    results_40 = run_all_fits(cfg.C40, cfg.q40, "40 °C")
    results_50 = run_all_fits(cfg.C50, cfg.q50, "50 °C")
    plot_dual_temp("Langmuir", [(cfg.C40, cfg.q40), (cfg.C50, cfg.q50)],
                   [results_40, results_50], ["40 °C", "50 °C"])
"""
from __future__ import annotations

from pathlib import Path

from .config import C40, q40, C50, q50
from .fit import run_all_fits
from .models import MODEL_FN
from .plot_util import plot_fit, plot_dual_temp

DATASETS = [
    (C40, q40, "40 °C"),
    (C50, q50, "50 °C"),
]


def main(
    output_dir: Path | str | None = None,
    show: bool = True,
) -> None:
    """Fit all isotherm models and produce plots.

    Parameters
    ----------
    output_dir:
        Directory to save figures. ``None`` skips saving.
    show:
        Whether to display figures interactively (set ``False`` for batch runs).
    """
    out = Path(output_dir) if output_dir is not None else None
    if out is not None:
        out.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 1. Fit all models for each temperature
    # ------------------------------------------------------------------
    results_map: dict[str, list] = {}
    for C, q, label in DATASETS:
        results_map[label] = run_all_fits(C, q, label=label)

    # ------------------------------------------------------------------
    # 2. Per-temperature plot  (all models on one axes)
    # ------------------------------------------------------------------
    for C, q, label in DATASETS:
        save_path = out / f"isotherm_{label.replace(' ', '_')}.png" if out else None
        plot_fit(
            C, q,
            results=results_map[label],
            title=f"Isotherm fit — {label}",
            save_path=save_path,
            show=show,
        )

    # ------------------------------------------------------------------
    # 3. Dual-temperature plot per model
    # ------------------------------------------------------------------
    datasets     = [(C, q) for C, q, _ in DATASETS]
    results_list = [results_map[label] for _, _, label in DATASETS]
    labels       = [label for _, _, label in DATASETS]

    for model_name in MODEL_FN:
        save_path = (
            out / f"dual_{model_name.lower().replace(' ', '_')}.png" if out else None
        )
        plot_dual_temp(
            model_name,
            datasets=datasets,
            results_list=results_list,
            labels=labels,
            title=f"{model_name} — 40 °C vs 50 °C",
            save_path=save_path,
            show=show,
        )


if __name__ == "__main__":
    main(
        output_dir=Path(__file__).resolve().parent / "outputs",
        show=True,
    )
