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
      Othmer-Tobias : ln[(1-w33)/w33] = a + b·ln[(1-w11)/w11]
      Hand          : ln(w23/w33)     = a + b·ln(w21/w11)
      Bachman       : w33             = a + b·(w33/w11)
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

    x_ot   = np.log((1 - w11) / w11)
    y_ot   = np.log((1 - w33) / w33)

    x_hand = np.log(w21 / w11)
    y_hand = np.log(w23 / w33)

    x_bach = w33 / w11
    y_bach = w33.copy()

    # Selectivity: D1 = w13/w11 (carrier), D2 = w23/w21 (solute), S = D2/D1
    d1 = w13 / w11
    d2 = w23 / w21
    s  = d2 / d1

    return {
        'ot':         _fit(x_ot,   y_ot),
        'hand':       _fit(x_hand, y_hand),
        'bachman':    _fit(x_bach, y_bach),
        # Full precision on purpose: rounding is a display-only concern, done
        # once at the point of display (JS toFixed / Plotly hover format).
        # Pre-rounding here would double-round (e.g. 0.056451 -> 0.0565 -> 0.057
        # instead of 0.056) and could disagree with the tie-line table/chart.
        'selectivity': {
            'w21': w21.tolist(),
            'w23': w23.tolist(),
            'd1':  d1.tolist(),
            'd2':  d2.tolist(),
            's':   s.tolist(),
        },
    }


def compute_plait_loglog(system):
    """
    Log-log plait point determination chart data.

    Axes are natural log (ln) and match the Hand correlation panel:
      For binodal data (columns [wCarrier%, wSolute%, wSolvent%]):
        x = ln(wSolute / wCarrier)   = ln(wpa/wbp)
        y = ln(wSolute / wSolvent)   = ln(wpa/ww)
      For tie-line data (same axes as the Hand correlation):
        x = ln(w21/w11)  = ln(solute_carrier-rich / carrier_carrier-rich)
        y = ln(w23/w33)  = ln(solute_solvent-rich / solvent_solvent-rich)

    The tie-line points and their linear fit here are identical to the Hand
    correlation chart (same points; same regression ln(w23/w33) = a + b*ln(w21/w11)).
    Plait point: intersection of that tie-line fit line with the binodal spline.
    """
    from scipy.interpolate import splprep, splev
    from scipy.optimize import brentq

    _eps = 1e-9

    # --- Binodal data ---
    bx, by = [], []
    for row in system.equil_data:
        wC, wS, wSv = row[0]/100, row[1]/100, row[2]/100
        if wC > _eps and wS > _eps and wSv > _eps:
            bx.append(float(np.log(wS / wC)))    # x = ln(w2/w1)
            by.append(float(np.log(wS / wSv)))   # y = ln(w2/w3)
    bx = np.array(bx)
    by = np.array(by)

    n = len(bx)
    bx_fine, by_fine = bx.copy(), by.copy()
    tck = None
    u_fine = np.linspace(0, 1, 300)
    if n >= 4:
        tck, _ = splprep([bx, by], s=0.0, k=min(3, n - 1))
        bx_fine, by_fine = splev(u_fine, tck)
        bx_fine = np.array(bx_fine)
        by_fine = np.array(by_fine)

    # --- Tie-line data (Hand correlation axes) — compute FIRST for intersection ---
    tx, ty = [], []
    for pt_L, pt_R in system.tie_coords:
        cL = xy_to_comp(*pt_L)
        cR = xy_to_comp(*pt_R)
        w21 = max(_eps, cR[0] / 100)
        w11 = max(_eps, cR[1] / 100)
        w23 = max(_eps, cL[0] / 100)
        w33 = max(_eps, cL[2] / 100)
        tx.append(float(np.log(w21 / w11)))   # x = ln(w21/w11)  (Hand x-axis)
        ty.append(float(np.log(w23 / w33)))   # y = ln(w23/w33)  (Hand y-axis)
    tx = np.array(tx)
    ty = np.array(ty)

    coeffs         = np.polyfit(tx, ty, 1)
    b_fit, a_fit   = float(coeffs[0]), float(coeffs[1])

    # Plait point: intersection of binodal spline with tie-line linear fit
    # i.e., find t where spline_y(t) = a_fit + b_fit * spline_x(t)
    plait_loglog = None
    plait_comp   = None
    if tck is not None:
        diff = by_fine - (a_fit + b_fit * bx_fine)
        for i in range(len(diff) - 1):
            if diff[i] * diff[i + 1] < 0:
                try:
                    def _f(uu, _a=a_fit, _b=b_fit):
                        px, py = splev(float(uu), tck)
                        return float(py) - (_a + _b * float(px))
                    u_root = brentq(_f, float(u_fine[i]), float(u_fine[i + 1]))
                    px, py = splev(u_root, tck)
                    px, py = float(px), float(py)
                    ex, ey = np.exp(px), np.exp(py)   # ex = w2/w1, ey = w2/w3
                    wS  = 1.0 / (1.0 + 1.0 / ex + 1.0 / ey)
                    wC  = wS / ex
                    wSv = wS / ey
                    plait_loglog = {'x': round(px, 4), 'y': round(py, 4)}
                    plait_comp   = {
                        'carrier': round(wC  * 100, 2),
                        'solute':  round(wS  * 100, 2),
                        'solvent': round(wSv * 100, 2),
                    }
                except Exception:
                    pass
                break

    # Extend tie-line fit to the plait point x (+ small margin)
    tx_end = max(float(tx.max()), plait_loglog['x'] + 0.3) if plait_loglog else float(tx.max())
    tx_fit = np.linspace(float(tx.min()), tx_end, 80)
    ty_fit = a_fit + b_fit * tx_fit

    return {
        'binodal': {
            'x':     np.round(bx,      6).tolist(),
            'y':     np.round(by,      6).tolist(),
            'x_fit': np.round(bx_fine, 6).tolist(),
            'y_fit': np.round(by_fine, 6).tolist(),
        },
        'tieline': {
            'x':     np.round(tx,     6).tolist(),
            'y':     np.round(ty,     6).tolist(),
            'x_fit': np.round(tx_fit, 6).tolist(),
            'y_fit': np.round(ty_fit, 6).tolist(),
        },
        'plait':      plait_loglog,
        'plait_comp': plait_comp,
    }
