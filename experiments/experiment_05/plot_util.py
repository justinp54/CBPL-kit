import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, TypeAlias

try:
    from .config import Segment
    from .mccabe import compute_total_reflux
except ImportError:
    from config import Segment
    from mccabe import compute_total_reflux

def plot_equilibrim_curve(x: List[float], y: List[float], title: str = "Equilibrium Curve") -> None:
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, linestyle='-', color='red')
    plt.plot([0, 1], [0, 1], linestyle='-', color='black')  # y=x line for reference
    plt.xlabel('Acetone mole fraction in liquid, x')
    plt.ylabel('Acetone mole fraction in vapor, y')
    plt.grid()
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.title(title)
    plt.show()

def plot_mccabe_thiele(
    x: List[float],
    y: List[float],
    xB: float,
    xD: float,
    title: str = "McCabe-Thiele Diagram",
    max_steps: int = 1000
) -> None:
    plt.figure(figsize = (8,6))
    plt.title(title+f" (xB={xB:.2f}, xD={xD:.2f})")
    plt.plot(x, y, linestyle='-', color='red')
    plt.plot([0,1],[0,1], linestyle='-', color='black') # y=x line for reference
    
    segments, stages = compute_total_reflux(xD, xB, max_steps)
    segments_to_plot = segments[:2*max_steps]
    for (x_1, y_1), (x_2, y_2) in segments_to_plot:
        plt.plot([x_1, x_2], [y_1, y_2], linestyle='-', color='blue')
    plt.plot([xB, xB], [0, xB], linestyle='--', color='grey')  # Vertical line from (xB, xB) to (xB, 0)
    plt.text(xB, 0, 'xB', verticalalignment = 'bottom', horizontalalignment = 'left')
    plt.plot([xD, xD], [0, xD], linestyle='--', color='grey')  # Vertical line from (xD, xD) to (xD, 0)
    plt.text(xD, 0, 'xD', verticalalignment = 'bottom', horizontalalignment = 'left')
    plt.plot([xB, xB], [xB,y_1], linestyle = '-', color = 'grey', lw = 1)
    plt.scatter([xB, xD], [xB, xD])
    plt.text(xB, xB, f' Stages: {stages:.2f}', verticalalignment='top', horizontalalignment='left')
    print(f"Total stages (including fraction): {stages:.2f}")
    plt.xlabel('Acetone mole fraction in liquid, x')
    plt.ylabel('Acetone mole fraction in vapor, y')
    plt.grid()
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()