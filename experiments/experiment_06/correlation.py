import numpy as np
from ternary import xy_to_comp


def compute_correlations(system):
    """
    Compute Othmer-Tobias, Hand, and Bachman linear correlation fits from tie-line data.

    Subscript convention (fractions, not %):
      1=carrier, 2=solute, 3=solvent; second subscript = phase (1=carrier-rich, 3=solvent-rich)
      w11 = carrier in carrier-rich phase
      w21 = solute  in carrier-rich phase
      w23 = solute  in solvent-rich phase
      w33 = solvent in solvent-rich phase

    Models:
      Othmer-Tobias : ln[(1-w11)/w11] = a + b·ln[(1-w33)/w33]
      Hand          : ln(w21/w11)     = a + b·ln(w23/w33)
      Bachman       : w11             = a + b·(w11/w33)
    """
    _eps = 1e-9

    w11_arr, w13_arr, w21_arr, w23_arr, w33_arr = [], [], [], [], []
    for pt_L, pt_R in system.tie_coords:
        cL = xy_to_comp(*pt_L)   # returns (wpa%, wbp%, ww%) = (solute, carrier, solvent)
        cR = xy_to_comp(*pt_R)   # pt_L = solvent-rich, pt_R = carrier-rich
        w11_arr.append(max(_eps, cR[1] / 100))  # wbp in carrier-rich = w11
        w13_arr.append(max(_eps, cL[1] / 100))  # wbp in solvent-rich = w13
        w21_arr.append(max(_eps, cR[0] / 100))  # wpa in carrier-rich = w21
        w23_arr.append(max(_eps, cL[0] / 100))  # wpa in solvent-rich = w23
        w33_arr.append(max(_eps, cL[2] / 100))  # ww  in solvent-rich = w33

    w11 = np.array(w11_arr)
    w13 = np.array(w13_arr)
    w21 = np.array(w21_arr)
    w23 = np.array(w23_arr)
    w33 = np.array(w33_arr)

    def _fit(x, y):
        coeffs = np.polyfit(x, y, 1)   # [slope, intercept]
        b, a = float(coeffs[0]), float(coeffs[1])
        y_pred = a + b * x
        ss_res = float(np.sum((y - y_pred) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 1e-12 else 1.0
        x_fit = np.linspace(x.min(), x.max(), 60)
        return {
            'x':     x.tolist(),
            'y':     y.tolist(),
            'x_fit': x_fit.tolist(),
            'y_fit': (a + b * x_fit).tolist(),
            'a':     round(a, 4),
            'b':     round(b, 4),
            'r2':    round(r2, 6),
        }

    x_ot   = np.log((1 - w33) / w33)
    y_ot   = np.log((1 - w11) / w11)

    x_hand = np.log(w23 / w33)
    y_hand = np.log(w21 / w11)

    x_bach = w11 / w33
    y_bach = w11.copy()

    # Selectivity: D1 = w13/w11 (carrier), D2 = w23/w21 (solute), S = D2/D1
    d1 = w13 / w11
    d2 = w23 / w21
    s  = d2 / d1

    return {
        'ot':         _fit(x_ot,   y_ot),
        'hand':       _fit(x_hand, y_hand),
        'bachman':    _fit(x_bach, y_bach),
        'selectivity': {
            'w21': np.round(w21, 6).tolist(),
            'w23': np.round(w23, 6).tolist(),
            'd1':  np.round(d1,  4).tolist(),
            'd2':  np.round(d2,  4).tolist(),
            's':   np.round(s,   4).tolist(),
        },
    }
