from pathlib import Path
from typing import Iterable

import config
import mrl
import plot_util


def main(x1_values: Iterable[float] | None = None) -> list[float]:
    """Run modified Raoult calculation for all input liquid compositions."""
    x1_values = list(config.x1_list if x1_values is None else x1_values)
    results: list[float] = []

    for x1 in x1_values:
        bubble_t, _ = mrl.modified_raoult(
            config.acetone,
            config.isopropanol,
            x1,
            pressure=config.P,
        )
        results.append(bubble_t)

    return results


def build_continuous_xy(n_points: int = 101) -> tuple[list[float], list[float]]:
    """Generate smooth x-y data from MRL using evenly spaced liquid compositions."""
    if n_points < 2:
        raise ValueError("n_points must be at least 2.")

    x_grid = [i / (n_points - 1) for i in range(n_points)]
    return mrl.build_xy_data(
        config.acetone,
        config.isopropanol,
        x_grid,
        pressure=config.P,
    )


def plot_vle_with_experiment(
    y1_exp: Iterable[float],
    x1_exp: Iterable[float] | None = None,
    n_points: int = 101,
    connect_exp_endpoints: bool = True,
) -> tuple[list[float], list[float]]:
    """Plot continuous MRL curve with optional experimental points."""
    x_exp = list(config.x1_list if x1_exp is None else x1_exp)
    y_exp = list(y1_exp)
    if len(x_exp) != len(y_exp):
        raise ValueError("x1_exp and y1_exp must have the same length.")

    x_model, y_model = build_continuous_xy(n_points=n_points)
    plot_util.plot_vle_comparison(
        x_model,
        y_model,
        x_exp=x_exp,
        y_exp=y_exp,
        connect_exp_endpoints=connect_exp_endpoints,
    )
    return x_model, y_model


def save_vle_outputs(
    output_dir: str | Path | None = None,
    n_points: int = 101,
    connect_exp_endpoints: bool = True,
    show_plot: bool = True,
) -> dict[str, Path]:
    """Save VLE figure and numeric outputs (text/csv files)."""
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / "outputs"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_path = output_dir / "vle_xy.png"
    summary_path = output_dir / "vle_summary.txt"
    model_csv_path = output_dir / "vle_model_xy.csv"
    exp_csv_path = output_dir / "vle_exp_xy.csv"

    x_model, y_model = build_continuous_xy(n_points=n_points)
    y_exp = list(getattr(config, "y1_exp", []))
    x_exp = list(config.x1_list)

    if y_exp and len(y_exp) == len(x_exp):
        plot_util.plot_vle_comparison(
            x_model,
            y_model,
            x_exp=x_exp,
            y_exp=y_exp,
            connect_exp_endpoints=connect_exp_endpoints,
            save_path=figure_path,
            show_plot=show_plot,
        )
    else:
        plot_util.plot_vle_comparison(
            x_model,
            y_model,
            connect_exp_endpoints=connect_exp_endpoints,
            save_path=figure_path,
            show_plot=show_plot,
        )

    temperatures = main(config.x1_list)

    with model_csv_path.open("w", encoding="utf-8") as f:
        f.write("x1_model,y1_model\n")
        for x1, y1 in zip(x_model, y_model):
            f.write(f"{x1:.8f},{y1:.8f}\n")

    if y_exp and len(y_exp) == len(x_exp):
        with exp_csv_path.open("w", encoding="utf-8") as f:
            f.write("x1_exp,y1_exp,t_bubble_model_degC\n")
            for x1, y1, t_bubble in zip(x_exp, y_exp, temperatures):
                f.write(f"{x1:.8f},{y1:.8f},{t_bubble:.8f}\n")

    lines: list[str] = [
        "experiment=experiment_04",
        f"pressure_bar={config.P}",
        f"n_model_points={len(x_model)}",
        "",
        "bubble_temperature_at_experimental_x1_degC:",
    ]
    for x1, t_bubble in zip(config.x1_list, temperatures):
        lines.append(f"x1={x1:.4f}, t_bubble_degC={t_bubble:.6f}")

    lines.append("")
    lines.append(f"figure_file={figure_path.name}")
    lines.append(f"model_csv_file={model_csv_path.name}")
    if y_exp and len(y_exp) == len(x_exp):
        lines.append(f"exp_csv_file={exp_csv_path.name}")

    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    outputs: dict[str, Path] = {
        "figure": figure_path,
        "summary": summary_path,
        "model_csv": model_csv_path,
    }
    if y_exp and len(y_exp) == len(x_exp):
        outputs["exp_csv"] = exp_csv_path
    return outputs


if __name__ == "__main__":
    temperatures = main()
    for x1, t_bub in zip(config.x1_list, temperatures):
        print(f"x1={x1:.4f}, T_bubble={t_bub:.3f} degC")

    output_files = save_vle_outputs(
        output_dir=Path(__file__).resolve().parent / "outputs",
        n_points=101,
        connect_exp_endpoints=True,
        show_plot=True,
    )
    print("Saved output files:")
    for key, path in output_files.items():
        print(f"  {key}: {path}")
