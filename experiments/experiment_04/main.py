from typing import Iterable

import config
import mrl


def main(x1_values: Iterable[float] | None = None) -> list[float]:
    """Run modified Raoult calculation for all input liquid compositions."""
    x1_values = list(config.x1_list if x1_values is None else x1_values)
    results: list[float] = []

    for x1 in x1_values:
        bubble_t, _ = mrl.modified_raoult(config.acetone, config.isopropanol, x1)
        results.append(bubble_t)

    return results


if __name__ == "__main__":
    temperatures = main()
    for x1, t_bub in zip(config.x1_list, temperatures):
        print(f"x1={x1:.4f}, T_bubble={t_bub:.3f} °C")
    