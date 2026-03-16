from pathlib import Path
from typing import Iterable, Optional

import config
import mrl
import pr_eos
import plot_util

METHOD = {
    "modified_raoult": mrl.modified_raoult,
    "pr_eos": pr_eos.pr_eos,
}

METHOD_LABEL = {
    "modified_raoult": "Modified Raoult",
    "pr_eos": "PR EOS",
}

def main(x1_values: Optional[Iterable[float]] = None, method: str = "modified_raoult") -> list[float]:
    """Run the specified method for all input liquid compositions."""
    if method not in METHOD:
        raise ValueError(f"Unsupported method '{method}'.")
    
    x1_values = list(config.x1_list if x1_values is None else x1_values)
    results: list[float] = []

    for x1 in x1_values:
        bubble_t = METHOD[method](
            config.acetone,
            config.isopropanol,
            x1,
            pressure=config.P,
        )[0]
        results.append(bubble_t)

    return results


def build_continuous_xy(n_points: int = 101, method: str = "modified_raoult") -> tuple[list[float], list[float]]:
    """Generate smooth x-y data using the specified method with evenly spaced liquid compositions."""
    if n_points < 2:
        raise ValueError("n_points must be at least 2.")

    x_grid = [i / (n_points - 1) for i in range(n_points)]
    if method == "pr_eos":
        return pr_eos.build_xy_data(
            config.acetone,
            config.isopropanol,
            x_grid,
            pressure=config.P,
        )
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
    method: str = "modified_raoult",
) -> tuple[list[float], list[float]]:
    """Plot continuous VLE curve with optional experimental points."""
    x_exp = list(config.x1_list if x1_exp is None else x1_exp)
    y_exp = list(y1_exp)
    if len(x_exp) != len(y_exp):
        raise ValueError("x1_exp and y1_exp must have the same length.")

    x_model, y_model = build_continuous_xy(n_points=n_points, method=method)
    plot_util.plot_vle_comparison(
        x_model,
        y_model,
        x_exp=x_exp,
        y_exp=y_exp,
        connect_exp_endpoints=connect_exp_endpoints,
        model_name=METHOD_LABEL[method],
        title=f"VLE diagram by experiment and {METHOD_LABEL[method]} calculation",
    )
    return x_model, y_model


def save_vle_outputs(
    output_dir: str | Path | None = None,
    n_points: int = 101,
    connect_exp_endpoints: bool = True,
    show_plot: bool = True,
    method: str = "modified_raoult",
) -> dict[str, Path]:
    """Save VLE figure and numeric outputs (text/csv files)."""
    if output_dir is None:
        output_dir = Path(__file__).resolve().parent / "outputs"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_path = output_dir / f"vle_xy_{method}.png"
    summary_path = output_dir / f"vle_summary_{method}.txt"
    model_csv_path = output_dir / f"vle_model_xy_{method}.csv"
    exp_csv_path = output_dir / f"vle_exp_xy_{method}.csv"

    x_model, y_model = build_continuous_xy(n_points=n_points, method=method)
    y_exp = list(getattr(config, "y1_exp", []))
    x_exp = list(config.x1_list)

    if y_exp and len(y_exp) == len(x_exp):
        plot_util.plot_vle_comparison(
            x_model,
            y_model,
            x_exp=x_exp,
            y_exp=y_exp,
            connect_exp_endpoints=connect_exp_endpoints,
            model_name=METHOD_LABEL[method],
            title=f"VLE diagram by experiment and {METHOD_LABEL[method]} calculation",
            save_path=figure_path,
            show_plot=show_plot,
        )
    else:
        plot_util.plot_vle_comparison(
            x_model,
            y_model,
            connect_exp_endpoints=connect_exp_endpoints,
            model_name=METHOD_LABEL[method],
            title=f"VLE diagram by {METHOD_LABEL[method]} calculation",
            save_path=figure_path,
            show_plot=show_plot,
        )

    temperatures = main(config.x1_list, method=method)

    with model_csv_path.open("w", encoding="utf-8") as f:
        f.write("x1_model,y1_model\n")
        for x1, y1 in zip(x_model, y_model):
            f.write(f"{x1:.8f},{y1:.8f}\n")

    if y_exp and len(y_exp) == len(x_exp):
        with exp_csv_path.open("w", encoding="utf-8") as f:
            f.write("x1_exp,y1_exp,t_bubble_model_K\n")
            for x1, y1, t_bubble in zip(x_exp, y_exp, temperatures):
                f.write(f"{x1:.8f},{y1:.8f},{t_bubble:.8f}\n")

    lines: list[str] = [
        "experiment=experiment_04",
        f"pressure_bar={config.P}",
        f"n_model_points={len(x_model)}",
        "",
        "bubble_temperature_at_experimental_x1_K:",
    ]
    for x1, t_bubble in zip(config.x1_list, temperatures):
        lines.append(f"x1={x1:.4f}, t_bubble_K={t_bubble:.6f}")

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
    for method in METHOD.keys():
        print(f"\n=== Running VLE calculations using method: {method} ===")
        temperatures = main(method=method)
        for x1, t_bub in zip(config.x1_list, temperatures):
            print(f"x1={x1:.4f}, T_bubble={t_bub:.3f} K")

        output_files = save_vle_outputs(
            output_dir=Path(__file__).resolve().parent / "outputs",
            n_points=101,
            connect_exp_endpoints=True,
            show_plot=True,
            method=method
        )
        print(f"Saved output files for {method}:")
        for key, path in output_files.items():
            print(f"  {key}: {path}")
