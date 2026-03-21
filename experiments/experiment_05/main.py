from mccabe import set_equilibrium_data
from plot_util import plot_equilibrim_curve, plot_mccabe_thiele


def main() -> None:
	# Placeholder equilibrium data (x-y). Replace with your own measured/model values.
	x_data = [0.0, 0.0359, 0.1080, 0.1468, 0.1927, 0.2489, 0.3997, 0.4215, 0.4629, 0.6077, 0.7691, 0.9249, 1.0]
	y_data = [0.0, 0.1135, 0.3018, 0.3793, 0.4525, 0.5261, 0.6860, 0.6974, 0.7242, 0.8081, 0.8873, 0.9614, 1.0]

	# Build interpolation functions used by McCabe-Thiele stepping.
	set_equilibrium_data(x_data, y_data)

	xB = 0.47037
	xD = 0.92506
	max_steps = 100

	plot_equilibrim_curve(x_data, y_data)
	plot_mccabe_thiele(x_data, y_data, xB=xB, xD=xD, max_steps=max_steps)


if __name__ == "__main__":
	main()

