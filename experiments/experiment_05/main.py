from typing import List

import numpy as np

try:
    from .mccabe import digitize_curve_from_image, set_equilibrium_data
    from .plot_util import plot_equilibrim_curve, plot_mccabe_thiele
except ImportError:
    from mccabe import digitize_curve_from_image, set_equilibrium_data
    from plot_util import plot_equilibrim_curve, plot_mccabe_thiele
IMAGE_PATH = "images/VLE_curve.png"

def load_vle_data(
    mode: str,
    x_data: List[float] | None = None,
    y_data: List[float] | None = None,
    image_path: str | None = None,
    num_points: int = 20,
) -> tuple[np.ndarray, np.ndarray]:
    if mode == "data":
        if x_data is None or y_data is None:
            raise ValueError("x_data and y_data are required when mode='data'")
        return np.asarray(x_data, dtype=float), np.asarray(y_data, dtype=float)

    if mode == "image":
        if image_path is None:
            raise ValueError("image_path is required when mode='image'")
        x_img, y_img = digitize_curve_from_image(image_path, num_points=num_points)
        return np.asarray(x_img, dtype=float), np.asarray(y_img, dtype=float)

    raise ValueError("mode must be either 'data' or 'image'")


def main(
    mode: str = "data",
    x_data: List[float] | None = None,
    y_data: List[float] | None = None,
    image_path: str | None = None,
    xB: float = 0.47037,
    xD: float = 0.92506,
    max_steps: int = 100,
    num_points: int = 20,
) -> None:
    if mode == "data" and (x_data is None or y_data is None):
        # Default list input for quick start.
        x_data = [0.0, 0.0359, 0.1080, 0.1468, 0.1927, 0.2489, 0.3997, 0.4215, 0.4629, 0.6077, 0.7691, 0.9249, 1.0]
        y_data = [0.0, 0.1135, 0.3018, 0.3793, 0.4525, 0.5261, 0.6860, 0.6974, 0.7242, 0.8081, 0.8873, 0.9614, 1.0]

    x_arr, y_arr = load_vle_data(
        mode=mode,
        x_data=x_data,
        y_data=y_data,
        image_path=image_path,
        num_points=num_points,
    )

    x_list = x_arr.tolist()
    y_list = y_arr.tolist()

    # Build interpolation functions used by McCabe-Thiele stepping.
    set_equilibrium_data(x_list, y_list)

    plot_equilibrim_curve(x_list, y_list)
    plot_mccabe_thiele(x_list, y_list, xB=xB, xD=xD, max_steps=max_steps)


if __name__ == "__main__":
    main(mode = "image", image_path=IMAGE_PATH, num_points=10)
