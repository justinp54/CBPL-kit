import matplotlib.pyplot as plt
from pathlib import Path
from typing import Sequence


def plot_iteration_history(T_history: list[float], title: str) -> None:
    """Plot the history of temperature iteration."""
    plt.figure()
    plt.plot(T_history, marker="o")
    plt.title(title)
    plt.xlabel("Iteration")
    plt.ylabel("Temperature (degC)")
    plt.grid()
    plt.show()


def _mirror_binary_curve(
    x1: Sequence[float], y1: Sequence[float]
) -> tuple[list[float], list[float]]:
    """Build mirrored x-y curve for component 2 in a binary system."""
    mirrored = sorted((1.0 - x, 1.0 - y) for x, y in zip(x1, y1))
    x2 = [pair[0] for pair in mirrored]
    y2 = [pair[1] for pair in mirrored]
    return x2, y2


def plot_vle_comparison(
    x_model: Sequence[float],
    y_model: Sequence[float],
    x_exp: Sequence[float] | None = None,
    y_exp: Sequence[float] | None = None,
    connect_exp_endpoints: bool = True,
    model_name: str = "MRL",
    title: str | None = None,
    save_path: str | Path | None = None,
    show_plot: bool = True,
) -> None:
    """Plot MRL continuous curves with optional experimental points."""
    if len(x_model) != len(y_model):
        raise ValueError("x_model and y_model must have the same length.")

    x_model = list(x_model)
    y_model = list(y_model)

    if title is None:
        title = f"VLE diagram by experiment and {model_name} calculation"

    plt.figure(figsize=(7, 7))

    # Acetone and isopropanol model curves
    plt.plot(
        x_model,
        y_model,
        color="0.55",
        linewidth=1.5,
        label=f"Acetone ({model_name})",
    )
    x2_model, y2_model = _mirror_binary_curve(x_model, y_model)
    plt.plot(
        x2_model,
        y2_model,
        color="0.55",
        linewidth=1.5,
        label=f"Isopropanol ({model_name})",
    )

    # Optional experimental points
    if x_exp is not None and y_exp is not None:
        if len(x_exp) != len(y_exp):
            raise ValueError("x_exp and y_exp must have the same length.")

        exp_pairs = [(float(x), float(y)) for x, y in zip(x_exp, y_exp)]
        if connect_exp_endpoints:
            exp_pairs.extend([(0.0, 0.0), (1.0, 1.0)])

        exp_pairs = sorted(exp_pairs, key=lambda pair: pair[0])
        x_exp = [pair[0] for pair in exp_pairs]
        y_exp = [pair[1] for pair in exp_pairs]
        plt.plot(
            x_exp,
            y_exp,
            color="red",
            marker="o",
            markersize=5,
            markerfacecolor="white",
            linewidth=0.9,
            label="Acetone_Exp",
        )

        x2_exp, y2_exp = _mirror_binary_curve(x_exp, y_exp)
        plt.plot(
            x2_exp,
            y2_exp,
            color="blue",
            marker="o",
            markersize=5,
            markerfacecolor="white",
            linewidth=0.9,
            label="Isopropanol_Exp",
        )

    plt.plot(
        [0.0, 1.0], [0.0, 1.0], linestyle=(0, (1.2, 3.0)), color="0.5", linewidth=1.0
    )
    plt.xlim(0.0, 1.0)
    plt.ylim(0.0, 1.0)
    plt.xlabel("Liquid mole fraction (x)")
    plt.ylabel("Vapor mole fraction (y)")
    plt.title(title)
    plt.grid(alpha=0.25)
    plt.legend(loc="upper center", ncol=2, frameon=False)
    plt.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=300)

    if show_plot:
        plt.show()
    else:
        plt.close()
