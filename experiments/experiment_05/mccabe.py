import numpy as np
from scipy.interpolate import interp1d
from typing import List, Tuple, TypeAlias
import matplotlib.pyplot as plt

try:
    from .config import Segment
except ImportError:
    from config import Segment

def _clamp_unit(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def _validate_inputs(xD: float, xB: float, max_steps: int) -> None:
    if not (0.0 <= xB <= 1.0 and 0.0 <= xD <= 1.0):
        raise ValueError("xD and xB must be within [0, 1].")
    if xD <= xB:
        raise ValueError("xD must be greater than xB for stripping toward bottoms.")
    if max_steps < 1:
        raise ValueError("max_steps must be >= 1.")


def _build_interpolators(x_data: np.ndarray, y_data: np.ndarray) -> Tuple[interp1d, interp1d]:
    if x_data.ndim != 1 or y_data.ndim != 1:
        raise ValueError("x_data and y_data must be 1D arrays.")
    if len(x_data) != len(y_data):
        raise ValueError("x_data and y_data must have the same length.")
    if len(x_data) < 2:
        raise ValueError("At least 2 equilibrium points are required.")
    if not np.all(np.isfinite(x_data)) or not np.all(np.isfinite(y_data)):
        raise ValueError("x_data and y_data must contain only finite values.")
    if np.any((x_data < 0.0) | (x_data > 1.0) | (y_data < 0.0) | (y_data > 1.0)):
        raise ValueError("x_data and y_data must be within [0, 1].")
    if np.any(np.diff(x_data) <= 0.0):
        raise ValueError("x_data must be strictly increasing.")
    if np.any(np.diff(y_data) <= 0.0):
        raise ValueError("y_data must be strictly increasing for inverse interpolation.")

    y_eq_local = interp1d(
        x_data,
        y_data,
        kind="linear",
        bounds_error=False,
        fill_value=(float(y_data[0]), float(y_data[-1])),
    )
    x_eq_local = interp1d(
        y_data,
        x_data,
        kind="linear",
        bounds_error=False,
        fill_value=(float(x_data[0]), float(x_data[-1])),
    )
    return y_eq_local, x_eq_local


def set_equilibrium_data(x_data: List[float], y_data: List[float]) -> None:
    global y_eq, x_eq
    x_arr = np.asarray(x_data, dtype=float)
    y_arr = np.asarray(y_data, dtype=float)
    y_eq, x_eq = _build_interpolators(x_arr, y_arr)

def digitize_curve_from_image(image_path: str, num_points: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    img = plt.imread(image_path)
    
    fig, ax = plt.subplots(figsize = (8,6))
    ax.imshow(img)
    plt.title(img)
    ax.set_title("Click to digitize points on the curve in order:\n"
                "1) origin (0,0), 2) x-axis point (1,0), 3) y-axis max point (0,1)\n"
                f"Then click {num_points} points along the curve.")
    
    pts = plt.ginput(num_points + 3, timeout=0)
    plt.close(fig)
    
    pts = np.array(pts, dtype=float)
    origin = pts[0]
    x_ref = pts[1]
    y_ref = pts[2]
    curve_points = pts[3:]
    
    x0, y0 = origin
    xx, yx = x_ref
    xy, yy = y_ref
    
    x_scale = 1.0 / (xx - x0)
    y_scale = 1.0 / (yy - y0)
    
    x_data = (curve_points[:, 0] - x0) * x_scale
    y_data = (curve_points[:, 1] - y0) * y_scale
    
    x_data = np.clip(x_data, 0.0, 1.0)
    y_data = np.clip(y_data, 0.0, 1.0)
    order = np.argsort(x_data)
    x_data = x_data[order]
    y_data = y_data[order]
    
    return x_data, y_data

def compute_total_reflux(xD: float, xB: float, max_steps: int = 1000)-> Tuple[List[Segment], float]:
    _validate_inputs(xD, xB, max_steps)

    segments = []
    x_current = _clamp_unit(xD)
    y_current = _clamp_unit(xD)  # start on the diagonal
    stages = 0.0
    
    for _ in range(max_steps):
        # Horizontal move to the equilibrium curve
        y_safe = _clamp_unit(y_current)
        x_on_eq = _clamp_unit(float(x_eq(y_safe)))
        segments.append(((x_current, y_current), (x_on_eq, y_current)))
        
        # Vertical move to the diagonal
        segments.append(((x_on_eq, y_current), (x_on_eq, x_on_eq)))

        if x_on_eq <= xB:
            fraction = (x_current - xB) / (x_current - x_on_eq) if x_current != x_on_eq else 0.0
            stages += fraction
            break
        
        x_current = x_on_eq
        y_current = x_on_eq
        stages += 1.0
    return segments, stages