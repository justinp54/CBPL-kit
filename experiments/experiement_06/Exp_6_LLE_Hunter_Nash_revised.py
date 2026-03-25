#%%
"""
Code for <CBPL_Exp6_LLE_Hunter_Nash>
Created on Mon Oct 13 2025
@author: Seong Lee (2020-11063)

Abbreviations:
    bp: n-bromopropane
    pa: propionic acid
    w: water

Comment: 
    Try not to understand all of the code but focus on the workflow.
    I'm bad at coding, so the code is inefficient and redundant.
"""

"""
Revised on Fri Oct 24 2025
@author: Geon Hwang (2021-15156)

Comment:
    function: E to R step (in Hunter-Nash Method, line 447) revised.
    saving figure as Fig6(b) (line 969) revised.
    
    You just need to change the result volume values in line 212
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from scipy.optimize import brentq, minimize_scalar
from matplotlib.patches import Polygon

#%% 0. Given data

# Equilibrium data (wt%): [w_bp, w_pa, w_w]
equil_data = np.array([[5.1, 9.49, 85.41],[8.37, 36.65, 54.98],[17.67, 49.4, 32.93],[32.724, 49.087, 18.189],[56.74, 37.83, 5.43],[84.18, 9.35, 6.47]])

# Tie line data (wt%): [w_pa in water-rich phase, w_pa in bp-rich phase]
tie_data = [(6.253, 2.564),(8.02, 2.65),(8.291, 3.058),(14.175, 8.047),(16.73, 9.88),(26.069, 19.418)]

# Physical properties
rho_bp = 1.354 # g/mL
rho_pa = 0.993 # g/mL
rho_w = 1.000 # g/mL
mw_bp = 122.99 # g/mol
mw_pa = 74.08 # g/mol
mw_w = 18.015 # g/mol

def xy_to_comp(x, y):
    """Ternary plot coordinate (x,y) -> (wpa, wbp, ww) [wt%]"""
    wpa = y / np.sqrt(3) * 2
    wbp = x - 0.5 * wpa
    ww  = 100 - wpa - wbp
    return (float(wpa), float(wbp), float(ww))

#%% 1. Get equilibrium curve

# Convert equil_data to (x, y) coordinates: x = wbp + 0.5 * wpa, y = sqrt(3)/2 * wpa
x_equil = equil_data[:, 0] + 0.5 * equil_data[:, 1]
y_equil = np.sqrt(3) / 2 * equil_data[:, 1]
equil_coords = np.column_stack((x_equil, y_equil))
print("Equilibrium data points:")
for i, (x, y) in enumerate(equil_coords):
    print(f"Eq({i+1})=({x:.4f}, {y:.4f})")

# Equilibrium curve by spline
spline = make_interp_spline(x_equil, y_equil, k=3)
x_smooth = np.linspace(0, 100, 10000)
y_smooth = spline(x_smooth)
y_smooth_clipped = np.maximum(y_smooth, 0)

# Extrapolate spline to get x_intercepts
x_intercepts_spline = []
for i in range(len(x_smooth) - 1):
    if y_smooth[i] * y_smooth[i+1] < 0:
        root = brentq(spline, x_smooth[i], x_smooth[i+1])
        x_intercepts_spline.append(round(root, 3))
y_intercepts = [0] * len(x_intercepts_spline)
print("\nx-intercepts (spline extrapolate):", x_intercepts_spline)

# %% 1.1 Compare with tangent line extrapolation
"""just for fun?"""

# Tangent line extrapolated from spline endpoints
spline_der = spline.derivative()
x0_left, y0_left = x_equil[0], y_equil[0]
x0_right, y0_right = x_equil[-1], y_equil[-1]
m_left = spline_der(x0_left)
m_right = spline_der(x0_right)
x_intercept_left = float(x0_left - y0_left / m_left)
x_intercept_right = float(x0_right - y0_right / m_right)
x_intercepts_tangent = [round(x_intercept_left, 3), round(x_intercept_right, 3)]
print("x-intercepts (tangent extrapolate):", x_intercepts_tangent)
print("Check whether the two methods agree!")

# %% 2. Get tie line

# Tie line intersections (equilibrium curve-based)
tie_coords = []
def minimize_error(target_y, left=True):
    x_range = (0, 50) if left else (50, 100)
    result = minimize_scalar(lambda x: abs(spline(x) - np.sqrt(3) / 2 * target_y), bounds=x_range, method='bounded')
    return float(result.x), float(spline(result.x))
for y_left, y_right in tie_data:
    tie_coords.append((minimize_error(y_left, left=True), minimize_error(y_right, left=False)))

print("\n<Tie line intersections>", "\n-----------------------------------------------------------")
for idx, ((x1, y1), (x2, y2)) in enumerate(tie_coords):
    print(f"Line {idx+1}: Left = ({x1:.3f}, {y1:.3f}), Right = ({x2:.3f}, {y2:.3f})")
    print(f"Left  = PA: {y1 / np.sqrt(3) * 2:.3f} wt%, n-BP: {x1 - 0.5 * y1 / np.sqrt(3) * 2:.3f} wt%, water: {100 - x1 - 0.5 * y1 / np.sqrt(3) * 2:.3f} wt%")
    print(f"Right = PA: {y2 / np.sqrt(3) * 2:.3f} wt%, n-BP: {x2 - 0.5 * y2 / np.sqrt(3) * 2:.3f} wt%, water: {100 - x2 - 0.5 * y2 / np.sqrt(3) * 2:.3f} wt%")
    print("-----------------------------------------------------------")

# %% 3. Setup ternary axis for diagram

def setup_ternary_axis(ax):
    # Triangular axis
    pa, water, nbp = (50, 100 * np.sqrt(3) / 2), (0, 0), (100, 0)
    divs, subdivs = 10, 100
    tick_len = 0.5
    polygon = Polygon([water, nbp, pa], closed=True, edgecolor='black', facecolor='white', linewidth=1.5)
    ax.add_patch(polygon)
    ax.text(50, 89.5, "Solute (Propionic Acid)", ha='center', va='bottom', fontsize=11, weight='bold')
    ax.text(-8, -5, "Solvent (Water)", ha='left', va='top', fontsize=11, weight='bold')
    ax.text(108, -5, "Carrier (N-Bromopropane)", ha='right', va='top', fontsize=11, weight='bold')

    # Parallel gridlines
    for i in range(divs + 1):
        t = i / divs
        t_rev = 1 - t
        if 0 < i < divs:
            x1 = (1 - t) * water[0] + t * pa[0]
            y1 = (1 - t) * water[1] + t * pa[1]
            x2 = (1 - t) * nbp[0] + t * pa[0]
            y2 = (1 - t) * nbp[1] + t * pa[1]
            ax.plot([x1, x2], [y1, y2], color='lightgray', linestyle=':', linewidth=1)
            x1 = (1 - t) * water[0] + t * nbp[0]
            y1 = (1 - t) * water[1] + t * nbp[1]
            x2 = (1 - t_rev) * nbp[0] + t_rev * pa[0]
            y2 = (1 - t_rev) * nbp[1] + t_rev * pa[1]
            ax.plot([x1, x2], [y1, y2], color='lightgray', linestyle=':', linewidth=1)
            x1 = (1 - t) * nbp[0] + t * water[0]
            y1 = (1 - t) * nbp[1] + t * water[1]
            x2 = (1 - t_rev) * water[0] + t_rev * pa[0]
            y2 = (1 - t_rev) * water[1] + t_rev * pa[1]
            ax.plot([x1, x2], [y1, y2], color='lightgray', linestyle=':', linewidth=1)
        label = str(i * 10)
        xt = (1 - t) * water[0] + t * nbp[0]
        yt = (1 - t) * water[1] + t * nbp[1]
        ax.text(xt, yt - 2.2, label, ha='center', va='top', fontsize=8)
        xt = (1 - t) * nbp[0] + t * pa[0]
        yt = (1 - t) * nbp[1] + t * pa[1]
        ax.text(xt + 2.2, yt, label, ha='left', va='center', fontsize=8)
        xt = (1 - t) * pa[0] + t * water[0]
        yt = (1 - t) * pa[1] + t * water[1]
        ax.text(xt - 2.2, yt, label, ha='right', va='center', fontsize=8)
    
    # Tick marks
    for i in range(1, subdivs):
        if i % 10 == 0:
            continue
        t = i / subdivs
        x = (1 - t) * water[0] + t * nbp[0]
        y = (1 - t) * water[1] + t * nbp[1]
        ax.plot([x, x], [y, y + tick_len], color='gray', linewidth=0.5)
        x = (1 - t) * nbp[0] + t * pa[0]
        y = (1 - t) * nbp[1] + t * pa[1]
        dx = np.sqrt(3) / 2 * tick_len
        dy = 0.5 * tick_len
        ax.plot([x, x - dx], [y, y - dy], color='gray', linewidth=0.5)
        x = (1 - t) * pa[0] + t * water[0]
        y = (1 - t) * pa[1] + t * water[1]
        ax.plot([x, x + dx], [y, y - dy], color='gray', linewidth=0.5)

    # Equilibrium curve
    ax.plot(x_smooth, y_smooth_clipped, '-', color='black', linewidth=1.2, label="Equilibrium curve")
    ax.fill_between(x_smooth, y_smooth_clipped, color='lightblue', alpha=0.5, edgecolor=None)
    
    ax.set_xlim(-10, 110)
    ax.set_ylim(-10, 98)
    ax.set_aspect('equal')
    ax.axis('off')

# %% 4. [Fig 1] Ternary plot with equilibrium curve & tie lines

fig, ax = plt.subplots(figsize=(8, 8))
setup_ternary_axis(ax)
ax.plot(x_equil, y_equil, 'o', color='black', markersize=4) # Plot equilibrium points
ax.text(50, 55, "Homogeneous (P=1)", ha='center', va='center', fontsize=11, weight='bold')
ax.text(50, 30, "Heterogeneous (P=2)", ha='center', va='center', fontsize=11, weight='bold')

# Plot tie lines
for i, ((x1, y1), (x2, y2)) in enumerate(tie_coords):
    if i == 0: ax.plot([x1, x2], [y1, y2], color='darkblue', linewidth=0.5, label="Tie lines")
    else: ax.plot([x1, x2], [y1, y2], color='darkblue', linewidth=0.5)

ax.legend()
plt.tight_layout()
plt.savefig('Fig1', bbox_inches='tight', dpi=300)
plt.show()

# %% 5. Feed(R0), extract(E1) and raffinate(Rn) from titration results
"""
feed and extract are diluted 10 times(10mL)
raffinate is not diluted(10mL)
titrated with 0.5M NaOH(v[mL]) to get concentration of PA(c[M])
0.5*v=c*10, c=0.05*v (don't forget to multiply 10 for feed and extract)
assume volume additivity (V_total = V_pa + V_bp + V_w, ideal mixing)
"""
# Titration results
v_R0, v_E1, v_Rn = 10.78, 3.8, 0.64 # mL

"""
Just change the values above!
"""

c_R0, c_E1, c_Rn = 0.05*v_R0*10, 0.05*v_E1*10, 0.05*v_Rn # M
pt_En1 = (0, 0) # Pure solvent (En1)

# Feed point (R0) from binary mixture
wpa_R0 = c_R0*mw_pa / (c_R0*mw_pa+rho_bp*(1000-c_R0*mw_pa/rho_pa))*100
wbp_R0 = 100-wpa_R0
x_R0 = wbp_R0 + 0.5 * wpa_R0
y_R0 = np.sqrt(3) / 2 * wpa_R0
pt_R0 = (x_R0, y_R0)

# Extract (E1) and raffinate (Rn) by iteration
target_c_E1 = c_E1
target_c_Rn = c_Rn

def calc_c(x, y): # too long, so make a function
    wpa = y / np.sqrt(3) * 2
    wbp = x - 0.5 * wpa
    ww = 100 - wpa - wbp
    numerator = wpa / mw_pa
    denominator = (wpa/rho_pa + wbp/rho_bp + ww/rho_w)/1000 # mL -> L
    return numerator / denominator

def find_point_for_c(target, left=True):
    x_range = (0, 50) if left else (50, 100)
    result = minimize_scalar(lambda x: abs(calc_c(x, spline(x)) - target), bounds=x_range, method='bounded')
    x_best = float(result.x)
    y_best = float(spline(x_best))
    wpa = y_best / np.sqrt(3) * 2
    wbp = x_best - 0.5 * wpa
    ww = 100 - wpa - wbp
    Cpa = calc_c(x_best, y_best)
    return (x_best, y_best), (wpa, wbp, ww), Cpa

pt_E1, comp_E1, cpa_E1 = find_point_for_c(target_c_E1, left=True)
pt_Rn, comp_Rn, cpa_Rn = find_point_for_c(target_c_Rn, left=False)

print(f"C_PA[M]: feed={c_R0:.3f}, extract={c_E1:.3f}, raffinate={c_Rn:.3f}")
print(f"\nFeed R0 = ({pt_R0[0]:.3f}, {pt_R0[1]:.3f})")
print(f"PA: {wpa_R0:.3f} wt%, n-BP: {wbp_R0:.3f} wt%, water: 0 wt%")
print(f"\nExtract E1 = ({pt_E1[0]:.3f}, {pt_E1[1]:.3f}), C_PA_cal = {cpa_E1:.3f}")
print(f"PA: {comp_E1[0]:.3f} wt%, n-BP: {comp_E1[1]:.3f} wt%, water: {comp_E1[2]:.3f} wt%")
print(f"\nRaffinate Rn = ({pt_Rn[0]:.3f}, {pt_Rn[1]:.3f}), C_PA_cal = {cpa_Rn:.3f}")
print(f"PA: {comp_Rn[0]:.3f} wt%, n-BP: {comp_Rn[1]:.3f} wt%, water: {comp_Rn[2]:.3f} wt%")
print("Check whether iteratively calculated C_PA_cal agrees with C_PA from titration!")

# %% 6. Get intersection point M and operating point P

# Intersection point
def line(p1, p2):
    A = p2[1] - p1[1]
    B = p1[0] - p2[0]
    C = -(A * p1[0] + B * p1[1])
    return A, B, C

def intersection(L1, L2):
    A1, B1, C1 = L1
    A2, B2, C2 = L2
    D = A1 * B2 - A2 * B1
    Dx = B1 * C2 - B2 * C1
    Dy = C1 * A2 - C2 * A1
    if D == 0:
        return None  # Parallel
    return (Dx / D, Dy / D)

# M, P
L1 = line(pt_E1, pt_Rn)
L2 = line(pt_En1, pt_R0)
L3 = line(pt_R0, pt_E1)
L4 = line(pt_Rn, pt_En1)
pt_M = intersection(L1, L2)
pt_P = intersection(L3, L4)
print(f"Intersection M = ({pt_M[0]:.3f}, {pt_M[1]:.3f})")
print(f"\nOperating point P = ({pt_P[0]:.3f}, {pt_P[1]:.3f})")

#%% 7. Conjugate curve and plait point
"""
Whether to approximate with a 3rd, 4th, or 5th degree polynomial is up to you.
Plot them (#7.1 below), compare, and decide which one fits the best.
In my case, I chose 4th degree polynomial.
(Actually I don't fully understand this code either lol)
"""
# Auxiliary lines and intersections
def find_auxiliary_intersection(left, right):
    xL, yL = left
    xR, yR = right
    m1 = -np.sqrt(3)  # Tangent -√3 (parallel to right side of triangle)
    m2 = np.sqrt(3)   # Tangent √3 (parallel to right side of triangle)

    # Auxiliary line 1: y = m1*(x - xL) + yL
    # Auxiliary line 2: y = m2*(x - xR) + yR
    x_int = (m1 * xL - m2 * xR + yR - yL) / (m1 - m2)
    y_int = m1 * (x_int - xL) + yL
    return (x_int, y_int)

aux_points = []
tie_coords_aux = [((x_intercepts_spline[0], 0), (x_intercepts_spline[1], 0))] + tie_coords
for i, (left_pt, right_pt) in enumerate(tie_coords_aux):
    inter = find_auxiliary_intersection(left_pt, right_pt)
    aux_points.append(inter)

# Conjugate curve
x_all, y_all = zip(*aux_points)
x_all = np.array(x_all)
y_all = np.array(y_all)

# Anchor point
x_anchor = x_all[0]
y_anchor = y_all[0]

# Guide points
x_guide = x_all[1:]
y_guide = y_all[1:]

# Create synthetic in-between points to guide the shape (interpolation between anchor and guide)
t = np.linspace(0, 1, len(x_guide) + 2)[1:-1]
x_synth = (1 - t) * x_anchor + t * x_guide
y_synth = (1 - t) * y_anchor + t * y_guide

# Combine anchor + synthetic points
x_curve = np.concatenate([[x_anchor], x_synth])
y_curve = np.concatenate([[y_anchor], y_synth])

# Polynomial fits
x_eval = np.linspace(min(x_curve), 100, 10000)

# Degree 4
coefs4 = np.polyfit(x_curve, y_curve, 4)
def conjugate_poly4(x): return np.polyval(coefs4, x)

# Find Plait Point
def diff_conjugate_vs_equilibrium(x):
    return conjugate_poly4(x) - spline(x)

try:
    x_plait = brentq(diff_conjugate_vs_equilibrium, max(x_curve), 100)
    y_plait = conjugate_poly4(x_plait)
    pt_plait = (x_plait, y_plait)
except ValueError:
    pt_plait = None
    x_plait = max(x_curve)
    y_plait = conjugate_poly4(x_plait)

# Truncated conjugate curve
x_eval = np.linspace(min(x_curve), 100, 10000)
x_eval_limited = x_eval[x_eval <= x_plait]
y_poly4_limited = conjugate_poly4(x_eval_limited)

print(f"Plait point = ({pt_plait[0]:.3f}, {pt_plait[1]:.3f})")
print("PA: {:.3f} wt%, n-BP: {:.3f} wt%, water: {:.3f} wt%".format(*xy_to_comp(pt_plait[0], pt_plait[1])))
print("Please somebody check whether this is correct from appropriate reference...I couldn't find any.")
print("\nAuxiliary line intersections")
print("------------------------------------------------------")
for i, (x, y) in enumerate(aux_points):
    print(f"Point {i+1}: ({x:.3f}, {y:.3f})")

#%% 8. [Fig 2(a)] Conjugate curve and plait point

fig, ax = plt.subplots(figsize=(8, 8))
setup_ternary_axis(ax)

# Plot tie lines and points
ax.plot(x_intercepts_spline[0], 0, 'o', color='darkblue', markersize=4)
ax.plot(x_intercepts_spline[1], 0, 'o', color='darkblue', markersize=4)
for i, ((x1, y1), (x2, y2)) in enumerate(tie_coords):
    ax.plot(x1, y1, 'o', color='darkblue', markersize=4)
    ax.plot(x2, y2, 'o', color='darkblue', markersize=4)
    if i == 0: ax.plot([x1, x2], [y1, y2], color='darkblue', linewidth=0.5, label="Tie lines")
    else: ax.plot([x1, x2], [y1, y2], color='darkblue', linewidth=0.5)

# Plot auxiliary points and conjugate curve
for (left_pt, right_pt), inter in zip(tie_coords_aux, aux_points):
    ax.plot([right_pt[0], inter[0]], [right_pt[1], inter[1]], linestyle=(0, (6, 8)), color='darkblue', linewidth=0.5)
    ax.plot([left_pt[0], inter[0]], [left_pt[1], inter[1]], linestyle=(0, (6, 8)), color='darkblue', linewidth=0.5)
ax.plot(*zip(*aux_points), 'o', color='orange', markersize=4)
ax.plot(x_eval_limited, y_poly4_limited, '-', color='orange', linewidth=1.2, label='Conjugate curve')
ax.plot(*pt_plait, 'o', color='orange', markersize=4)
ax.text(pt_plait[0] - 2.5, pt_plait[1] + 2.5, "Plait point", color='orange', fontsize=10, weight='bold')

ax.set_ylim(-80, 98) # Extend y-axis to show conjugate curve clearly
ax.legend()
plt.tight_layout()
plt.savefig('Fig2(a)', bbox_inches='tight', dpi=300)
plt.show()

# %% 7.1. Compare 3rd, 4th, 5th degree polynomial fits
"""compare 3rd, 4th, 5th degree polynomial fits for conjugate curve"""

# Degree 3
coefs3 = np.polyfit(x_curve, y_curve, 3)
y_poly3 = np.polyval(coefs3, x_eval)

# Degree 4
coefs4 = np.polyfit(x_curve, y_curve, 4)
y_poly4 = np.polyval(coefs4, x_eval)

# Degree 5
coefs5 = np.polyfit(x_curve, y_curve, 5)
y_poly5 = np.polyval(coefs5, x_eval)

fig, ax = plt.subplots(figsize=(8, 8))
setup_ternary_axis(ax)

# Plot tie lines and points
ax.plot(x_intercepts_spline[0], 0, 'o', color='darkblue', markersize=4)
ax.plot(x_intercepts_spline[1], 0, 'o', color='darkblue', markersize=4)
for i, ((x1, y1), (x2, y2)) in enumerate(tie_coords):
    ax.plot(x1, y1, 'o', color='darkblue', markersize=4)
    ax.plot(x2, y2, 'o', color='darkblue', markersize=4)
    if i == 0: ax.plot([x1, x2], [y1, y2], color='darkblue', linewidth=0.5, label="Tie lines")
    else: ax.plot([x1, x2], [y1, y2], color='darkblue', linewidth=0.5)

# Plot auxiliary points and conjugate curve
for (left_pt, right_pt), inter in zip(tie_coords_aux, aux_points):
    ax.plot([right_pt[0], inter[0]], [right_pt[1], inter[1]], linestyle=(0, (6, 8)), color='darkblue', linewidth=0.5)
    ax.plot([left_pt[0], inter[0]], [left_pt[1], inter[1]], linestyle=(0, (6, 8)), color='darkblue', linewidth=0.5)
ax.plot(*zip(*aux_points), 'o', color='orange', markersize=4)

ax.plot(x_eval, y_poly3, '-', color='red', linewidth=1, label='3rd Degree')
ax.plot(x_eval, y_poly4, '-', color='orange', linewidth=1, label='4th Degree')
ax.plot(x_eval, y_poly5, '-', color='green', linewidth=1, label='5th Degree')

ax.set_ylim(-80, 98) # Extend y-axis to show conjugate curve clearly
ax.legend()
plt.tight_layout()
plt.show()

# %% 8. Get R1, E2, R2, E3, ... by Hunter-Nash method

m1 = -np.sqrt(3)
m2 = np.sqrt(3)
def E_to_R_step(pt_E):
    """
    E_k -> m1 보조선과 conjugate line 교점 inter_pt 저장
    -> inter_pt 에서 m2 직선으로 equilibrium과 교점 R_k 저장
    """
    xE, yE = pt_E
    line_m1 = lambda x: m1*(x-xE)+yE

    # ------------------- 수정된 부분 -------------------
    # 기존: bounds=(xE, 100)
    # E_k의 x좌표(xE)가 아닌, 공액 곡선이 물리적으로 정의된 
    # x-범위, 즉 x_anchor ~ x_plait 사이에서 교점을 찾아야 합니다.
    # 이 변수들은 Section 7에서 계산되어 전역 변수로 접근 가능합니다.
    res = minimize_scalar(lambda x: abs(conjugate_poly4(x)-line_m1(x)), 
                          bounds=(x_anchor, x_plait), method='bounded')
    # ------------------- 수정 완료 -------------------

    x_min = float(res.x)
    y_min = float(line_m1(x_min))
    inter_pt = (x_min, y_min)
    
    line_m2 = lambda x: m2*(x - x_min) + y_min
    
    # 이 brentq의 탐색 범위(x_min, 100)는 올바릅니다.
    # 교점(x_min)보다 x가 큰 오른쪽 평형 곡선(Raffinate)에서 해를 찾기 때문입니다.
    xR = brentq(lambda x: line_m2(x) - spline(x), x_min, 100)
    yR = line_m2(xR)
    pt_R = (float(xR), float(yR))
    return pt_R, inter_pt

def R_to_E_step(pt_R):
    # R_k와 P를 잇는 직선과 평형의 교점 -> E_k+1
    x1, y1 = pt_R
    x2, y2 = pt_P
    m = (y2 - y1) / (x2 - x1)
    b = y1 - m * x1
    xE = brentq(lambda x: (m*x+b)-spline(x), 0.0, 50.0)        # 좌가지 고정
    yE = m * xE + b
    return (float(xE), float(yE))

# --- 반복 시작: E1부터 ---
steps = []           # 각 단계 기록용 (i, Ei, comp_Ei, inter_pt, Ri, comp_Ri)
inter_pts = []       # 보조 교점만 따로 저장
pts_E = [pt_E1]      # E1 포함
pts_R = []           # 이후 누적

y_Rn = pt_Rn[1]
max_steps = 50
i = 1
current_E = pt_E1

while i <= max_steps:
    # (1) E_i -> (inter_pt_i) -> R_i
    pt_Ri, inter_pt_i = E_to_R_step(current_E)
    comp_Ei = xy_to_comp(*current_E)
    comp_Ri = xy_to_comp(*pt_Ri)

    steps.append({
        'i': i,
        'Ei': current_E,
        'comp_Ei': comp_Ei,
        'inter_pt': inter_pt_i,   # 보조 교점 명시 저장
        'Ri': pt_Ri,
        'comp_Ri': comp_Ri
    })
    inter_pts.append(inter_pt_i)
    pts_R.append(pt_Ri)

    print(f"[Step {i}] E{i}=({current_E[0]:.3f}, {current_E[1]:.3f}), "
          f"inter_pt{i}=({inter_pt_i[0]:.3f}, {inter_pt_i[1]:.3f}), "
          f"R{i}=({pt_Ri[0]:.3f}, {pt_Ri[1]:.3f})")

    # (2) 종료 조건: R_i.y < Rn.y이면 stop → 이때의 i가 이론 단수
    if pt_Ri[1] < y_Rn:
        N_theory = i
        print(f"\nStop: R{i}.y({pt_Ri[1]:.3f}) < Rn.y({y_Rn:.3f})")
        print(f"Hunter–Nash 이론 단수 N = {N_theory}\n")
        break

    # (3) R_i -> E_{i+1}
    pt_E_next = R_to_E_step(pt_Ri)
    pts_E.append(pt_E_next)

    # 다음 루프
    current_E = pt_E_next
    i += 1
else:
    N_theory = None
    print("\nmax_steps에 도달하여 종료되었습니다.")

# %% 9. [Fig 3] Hunter-Nash graphical equillbrium-stage method

fig, ax = plt.subplots(figsize=(8, 8))
setup_ternary_axis(ax)

# Plot R0, Rn, En1
ax.plot(*pt_R0, 'bo', markersize=4)
ax.text(pt_R0[0] + 1.5, pt_R0[1] + 1.5, r"$\mathbf{R_0}$", color='blue', fontsize=10)
ax.plot(*pt_Rn, 'bo', markersize=4)
ax.text(pt_Rn[0] + 1.5, pt_Rn[1] + 1.5, r"$\mathbf{R_n}$", color='blue', fontsize=10)
ax.plot(*pt_En1, 'ro', markersize=4)
ax.text(pt_En1[0] - 8, pt_En1[1] - 4, r"$\mathbf{E_{n+1}}$", color='red', fontsize=10)
ax.plot(*pt_P, 'o', color='brown', markersize=4)
ax.text(pt_P[0], pt_P[1] + 1.5, r"$\mathbf{P}$", color='brown', fontsize=10)
ax.plot([pt_R0[0], pt_P[0]], [pt_R0[1], pt_P[1]], '-', color='brown', linewidth=1.2, label='Operating lines')
ax.plot([pt_Rn[0], pt_P[0]], [pt_Rn[1], pt_P[1]], '-', color='brown', linewidth=1.2)

for idx in range(N_theory):
    s = steps[idx]
    i = s['i']
    Ei = s['Ei']
    Ri = s['Ri']
    ax.plot(*Ei, 'ro', markersize=4)
    ax.text(Ei[0] + 1.0, Ei[1] + 1.0, rf"$\mathbf{{E_{i}}}$", color='red', fontsize=10)
    if idx == 0:
        ax.plot([Ei[0], Ri[0]], [Ei[1], Ri[1]], '-', color='darkgreen', linewidth=1.2, label='Interpolated tie lines')
    else:
        ax.plot([Ei[0], Ri[0]], [Ei[1], Ri[1]], '-', color='darkgreen', linewidth=1.2)
    ax.plot(*Ri, 'bo', markersize=4)
    ax.text(Ri[0] + 1.0, Ri[1] + 1.0, rf"$\mathbf{{R_{i}}}$", color='blue', fontsize=10)
    if i < N_theory:
        ax.plot([Ri[0], pt_P[0]], [Ri[1], pt_P[1]], '-', color='brown', linewidth=1.2)


ax.set_xlim(-50, 110)
ax.legend()
plt.tight_layout()
plt.savefig('Fig3', bbox_inches='tight', dpi=300)
plt.show()

# %% 10. [Fig2(b)] Interpolated tie lines

fig, ax = plt.subplots(figsize=(8, 8))
setup_ternary_axis(ax)

ax.plot(x_eval_limited, y_poly4_limited, '-', color='orange', linewidth=1.2, label='Conjugate curve')
ax.plot(*pt_plait, 'o', color='orange', markersize=4)
ax.text(pt_plait[0] - 2.5, pt_plait[1] + 2.5, "Plait point", color='orange', fontsize=10, weight='bold')

for idx in range(N_theory):
    s = steps[idx]
    i = s['i']
    Ei = s['Ei']
    Ri = s['Ri']
    inter_pt_i = s['inter_pt']
    ax.plot(*inter_pt_i, 'o', color='darkgreen', markersize=4)
    ax.plot(*Ei, 'ro', markersize=4)
    ax.text(Ei[0] + 1.0, Ei[1] + 1.0, rf"$\mathbf{{E_{i}}}$", color='red', fontsize=10)
    if idx == 0:
        ax.plot([Ei[0], Ri[0]], [Ei[1], Ri[1]], '-', color='darkgreen', linewidth=1.2, label='Interpolated tie lines')
    else:
        ax.plot([Ei[0], Ri[0]], [Ei[1], Ri[1]], '-', color='darkgreen', linewidth=1.2)
    ax.plot([Ei[0], inter_pt_i[0]], [Ei[1], inter_pt_i[1]], linestyle=(0, (6, 8)), color='darkgreen', linewidth=0.5)
    ax.plot([Ri[0], inter_pt_i[0]], [Ri[1], inter_pt_i[1]], linestyle=(0, (6, 8)), color='darkgreen', linewidth=0.5)
    ax.plot(*Ri, 'bo', markersize=4)
    ax.text(Ri[0] + 1.0, Ri[1] + 1.0, rf"$\mathbf{{R_{i}}}$", color='blue', fontsize=10)


ax.set_ylim(-80, 98) # Extend y-axis to show conjugate curve clearly
ax.legend()
plt.tight_layout()
plt.savefig('Fig2(b)', bbox_inches='tight', dpi=300)
plt.show()

# %% 11. Get M', E1' from lever rule

# solvent 100 mL/min, feed 40 mL/min
En1 = 100 # g/min
R0 = 40/(wpa_R0/100/rho_pa + wbp_R0/100/rho_bp) # g/min

# Step 1: R0-En+1 선분을 En1:R0 로 내분하는 점 M'
total = En1 + R0
pt_Mp = (
    (R0 * pt_R0[0] + En1 * pt_En1[0]) / total,
    (R0 * pt_R0[1] + En1 * pt_En1[1]) / total,
)

# Step 2: Rn-M' 선의 식과 equilibrium curve 교점 찾기
A_RnMp, B_RnMp, C_RnMp = line(pt_Rn, pt_Mp)
m_RnMp = (pt_Mp[1] - pt_Rn[1]) / (pt_Mp[0] - pt_Rn[0])
b_RnMp = pt_Rn[1] - m_RnMp * pt_Rn[0]
def diff_spline_vs_RnMp(x):
    return spline(x) - (m_RnMp * x + b_RnMp)

# 교점 x 좌표 찾기
x_check = np.linspace(0, min(pt_Rn[0], pt_Mp[0]), 10000)
xL, xR = None, None
for i in range(len(x_check) - 1):
    y1 = diff_spline_vs_RnMp(x_check[i])
    y2 = diff_spline_vs_RnMp(x_check[i + 1])
    if y1 * y2 < 0:
        xL = x_check[i]
        xR = x_check[i + 1]
        break

if xL and xR:
    x_E1p = brentq(diff_spline_vs_RnMp, xL, xR)
    y_E1p = spline(x_E1p)
    pt_E1p = (x_E1p, y_E1p)
else:
    pt_E1p = None

print(f"내분점 M' = ({pt_Mp[0]:.3f}, {pt_Mp[1]:.3f})")
print(f"\nE1' = ({pt_E1p[0]:.3f}, {pt_E1p[1]:.3f})")
print("PA: {:.3f} wt%, n-BP: {:.3f} wt%, water: {:.3f} wt%".format(*xy_to_comp(pt_E1p[0], pt_E1p[1])))

# %% 12. [Fig 4] M' and E1' by lever rule

fig, ax = plt.subplots(figsize=(8, 8))
setup_ternary_axis(ax)

# Plot R0, Rn, En1, E1
ax.plot(*pt_R0, 'bo', markersize=4)
ax.text(pt_R0[0] + 1.5, pt_R0[1] + 1.5, r"$\mathbf{R_0}$", color='blue', fontsize=10)
ax.plot(*pt_Rn, 'bo', markersize=4)
ax.text(pt_Rn[0] + 1.5, pt_Rn[1] + 1.5, r"$\mathbf{R_n}$", color='blue', fontsize=10)
ax.plot(*pt_E1, 'ro', markersize=4)
ax.text(pt_E1[0] - 3, pt_E1[1] + 1.5, r"$\mathbf{E_1}$", color='red', fontsize=10)
ax.plot(*pt_En1, 'ro', markersize=4)
ax.text(pt_En1[0] - 8, pt_En1[1] - 4, r"$\mathbf{E_{n+1}}$", color='red', fontsize=10)

ax.plot([pt_E1[0], pt_Rn[0]], [pt_E1[1], pt_Rn[1]], '-', color='purple', linewidth=1)
ax.plot([pt_En1[0], pt_R0[0]], [pt_En1[1], pt_R0[1]], '-', color='purple', linewidth=1)
ax.plot(*pt_M, 'o', color='purple', markersize=3)
ax.text(pt_M[0], pt_M[1] + 3, r"$\mathbf{M}$", color='purple', fontsize=10)

ax.plot(*pt_Mp, 'o', color='brown', markersize=4)
ax.text(pt_Mp[0], pt_Mp[1] - 3, r"$\mathbf{M'}$", color='brown', fontsize=10)
ax.plot(*pt_E1p, 'o', color='red', markersize=4)
ax.text(pt_E1p[0]-4, pt_E1p[1], r"$\mathbf{E'_{1}}$", color='red', fontsize=10)
ax.plot([pt_Rn[0], pt_E1p[0]], [pt_Rn[1], pt_E1p[1]], '-', color='brown', linewidth=1)

ax.legend()
plt.tight_layout()
plt.savefig('Fig4', bbox_inches='tight', dpi=300)
plt.show()

# %% 13. [Fig 5(a)] Solvent / Feed ratio (80:20)

fig, ax = plt.subplots(figsize=(8, 8))
setup_ternary_axis(ax)

# Plot R0, Rn, En1, E1
ax.plot(*pt_R0, 'bo', markersize=4)
ax.text(pt_R0[0] + 1.5, pt_R0[1] + 1.5, r"$\mathbf{R_0}$", color='blue', fontsize=10)
ax.plot(*pt_Rn, 'bo', markersize=4)
ax.text(pt_Rn[0] + 1.5, pt_Rn[1] + 1.5, r"$\mathbf{R_n}$", color='blue', fontsize=10)
ax.plot(*pt_E1, 'ro', markersize=4)
ax.text(pt_E1[0] - 3, pt_E1[1] + 1.5, r"$\mathbf{E_1}$", color='red', fontsize=10)
ax.plot(*pt_En1, 'ro', markersize=4)
ax.text(pt_En1[0] - 8, pt_En1[1] - 4, r"$\mathbf{E_{n+1}}$", color='red', fontsize=10)

ax.plot([pt_E1[0], pt_Rn[0]], [pt_E1[1], pt_Rn[1]], '-', color='purple', linewidth=1)
ax.plot([pt_En1[0], pt_R0[0]], [pt_En1[1], pt_R0[1]], '-', color='purple', linewidth=1)
ax.plot(*pt_M, 'o', color='purple', markersize=3)
ax.text(pt_M[0], pt_M[1] -3, r"$\mathbf{M}$", color='purple', fontsize=10)

# Solvent : Feed = 80:20
pt_Mp = (
    (0.2 * pt_R0[0] + 0.8 * pt_En1[0]),
    (0.2 * pt_R0[1] + 0.8 * pt_En1[1])
)

# Step 2: Rn-M' 선의 식과 equilibrium curve 교점 찾기
A_RnMp, B_RnMp, C_RnMp = line(pt_Rn, pt_Mp)
m_RnMp = (pt_Mp[1] - pt_Rn[1]) / (pt_Mp[0] - pt_Rn[0])
b_RnMp = pt_Rn[1] - m_RnMp * pt_Rn[0]
def diff_spline_vs_RnMp(x):
    return spline(x) - (m_RnMp * x + b_RnMp)

# 교점 x 좌표 찾기
x_check = np.linspace(0, min(pt_Rn[0], pt_Mp[0]), 10000)
xL, xR = None, None
for i in range(len(x_check) - 1):
    y1 = diff_spline_vs_RnMp(x_check[i])
    y2 = diff_spline_vs_RnMp(x_check[i + 1])
    if y1 * y2 < 0:
        xL = x_check[i]
        xR = x_check[i + 1]
        break

if xL and xR:
    x_E1p = brentq(diff_spline_vs_RnMp, xL, xR)
    y_E1p = spline(x_E1p)
    pt_E1p = (x_E1p, y_E1p)
else:
    pt_E1p = None

print(f"내분점 M' = ({pt_Mp[0]:.3f}, {pt_Mp[1]:.3f})")
print(f"\nE1' = ({pt_E1p[0]:.3f}, {pt_E1p[1]:.3f})")
print("PA: {:.3f} wt%, n-BP: {:.3f} wt%, water: {:.3f} wt%".format(*xy_to_comp(pt_E1p[0], pt_E1p[1])))

ax.plot(*pt_Mp, 'o', color='brown', markersize=4)
ax.text(pt_Mp[0], pt_Mp[1]-3, r"$\mathbf{M'}$", color='brown', fontsize=10)
ax.plot(*pt_E1p, 'o', color='red', markersize=4)
ax.text(pt_E1p[0]-4, pt_E1p[1], r"$\mathbf{E'_{1}}$", color='red', fontsize=10)
ax.plot([pt_Rn[0], pt_E1p[0]], [pt_Rn[1], pt_E1p[1]], '-', color='brown', linewidth=1)

ax.legend()
plt.tight_layout()
plt.savefig('Fig5(a)', bbox_inches='tight', dpi=300)
plt.show()

# %% 14. [Fig 5(b)] Solvent / Feed ratio (55:45)

fig, ax = plt.subplots(figsize=(8, 8))
setup_ternary_axis(ax)

# Plot R0, Rn, En1, E1
ax.plot(*pt_R0, 'bo', markersize=4)
ax.text(pt_R0[0] + 1.5, pt_R0[1] + 1.5, r"$\mathbf{R_0}$", color='blue', fontsize=10)
ax.plot(*pt_Rn, 'bo', markersize=4)
ax.text(pt_Rn[0] + 1.5, pt_Rn[1] + 1.5, r"$\mathbf{R_n}$", color='blue', fontsize=10)
ax.plot(*pt_E1, 'ro', markersize=4)
ax.text(pt_E1[0] - 3, pt_E1[1] + 1.5, r"$\mathbf{E_1}$", color='red', fontsize=10)
ax.plot(*pt_En1, 'ro', markersize=4)
ax.text(pt_En1[0] - 8, pt_En1[1] - 4, r"$\mathbf{E_{n+1}}$", color='red', fontsize=10)

ax.plot([pt_E1[0], pt_Rn[0]], [pt_E1[1], pt_Rn[1]], '-', color='purple', linewidth=1)
ax.plot([pt_En1[0], pt_R0[0]], [pt_En1[1], pt_R0[1]], '-', color='purple', linewidth=1)
ax.plot(*pt_M, 'o', color='purple', markersize=3)
ax.text(pt_M[0], pt_M[1] + 2, r"$\mathbf{M}$", color='purple', fontsize=10)

# Solvent : Feed = 55:45
pt_Mp = (
    (0.45 * pt_R0[0] + 0.55 * pt_En1[0]),
    (0.45 * pt_R0[1] + 0.55 * pt_En1[1])
)

# Step 2: Rn-M' 선의 식과 equilibrium curve 교점 찾기
A_RnMp, B_RnMp, C_RnMp = line(pt_Rn, pt_Mp)
m_RnMp = (pt_Mp[1] - pt_Rn[1]) / (pt_Mp[0] - pt_Rn[0])
b_RnMp = pt_Rn[1] - m_RnMp * pt_Rn[0]
def diff_spline_vs_RnMp(x):
    return spline(x) - (m_RnMp * x + b_RnMp)

# 교점 x 좌표 찾기
x_check = np.linspace(0, min(pt_Rn[0], pt_Mp[0]), 10000)
xL, xR = None, None
for i in range(len(x_check) - 1):
    y1 = diff_spline_vs_RnMp(x_check[i])
    y2 = diff_spline_vs_RnMp(x_check[i + 1])
    if y1 * y2 < 0:
        xL = x_check[i]
        xR = x_check[i + 1]
        break

if xL and xR:
    x_E1p = brentq(diff_spline_vs_RnMp, xL, xR)
    y_E1p = spline(x_E1p)
    pt_E1p = (x_E1p, y_E1p)
else:
    pt_E1p = None

print(f"내분점 M' = ({pt_Mp[0]:.3f}, {pt_Mp[1]:.3f})")
print(f"\nE1' = ({pt_E1p[0]:.3f}, {pt_E1p[1]:.3f})")
print("PA: {:.3f} wt%, n-BP: {:.3f} wt%, water: {:.3f} wt%".format(*xy_to_comp(pt_E1p[0], pt_E1p[1])))

ax.plot(*pt_Mp, 'o', color='brown', markersize=4)
ax.text(pt_Mp[0], pt_Mp[1] - 3, r"$\mathbf{M'}$", color='brown', fontsize=10)
ax.plot(*pt_E1p, 'o', color='red', markersize=4)
ax.text(pt_E1p[0]-4, pt_E1p[1], r"$\mathbf{E'_{1}}$", color='red', fontsize=10)
ax.plot([pt_Rn[0], pt_E1p[0]], [pt_Rn[1], pt_E1p[1]], '-', color='brown', linewidth=1)

ax.legend()
plt.tight_layout()
plt.savefig('Fig5(b)', bbox_inches='tight', dpi=300)
plt.show()

# %% 15. [Fig 6(a)] Feed concentration (40 wt% PA)

fig, ax = plt.subplots(figsize=(8, 8))
setup_ternary_axis(ax)

# Plot R0, Rn, En1, E1
ax.plot(*pt_R0, 'bo', markersize=4)
ax.text(pt_R0[0] + 1.5, pt_R0[1] + 1.5, r"$\mathbf{R_0}$", color='blue', fontsize=10)
ax.plot(*pt_Rn, 'bo', markersize=4)
ax.text(pt_Rn[0] + 1.5, pt_Rn[1] + 1.5, r"$\mathbf{R_n}$", color='blue', fontsize=10)
ax.plot(*pt_E1, 'ro', markersize=4)
ax.text(pt_E1[0] - 3, pt_E1[1] + 1.5, r"$\mathbf{E_1}$", color='red', fontsize=10)
ax.plot(*pt_En1, 'ro', markersize=4)
ax.text(pt_En1[0] - 8, pt_En1[1] - 4, r"$\mathbf{E_{n+1}}$", color='red', fontsize=10)

ax.plot([pt_E1[0], pt_Rn[0]], [pt_E1[1], pt_Rn[1]], '-', color='purple', linewidth=1)
ax.plot([pt_En1[0], pt_R0[0]], [pt_En1[1], pt_R0[1]], '-', color='purple', linewidth=1)
ax.plot(*pt_M, 'o', color='purple', markersize=3)
ax.text(pt_M[0], pt_M[1] - 3, r"$\mathbf{M}$", color='purple', fontsize=10)

# Feed concentration 40 wt% PA
wpa_R0p = 40
wbp_R0p = 60
x_R0p = wbp_R0p + 0.5 * wpa_R0p
y_R0p = (np.sqrt(3) / 2) * wpa_R0p
pt_R0p = (x_R0p, y_R0p)

# Step 1: R0-En+1 선분을 En1:R0 로 내분하는 점 M'
total = En1 + R0
pt_Mp = (
    (R0 * pt_R0p[0] + En1 * pt_En1[0]) / total,
    (R0 * pt_R0p[1] + En1 * pt_En1[1]) / total,
)

# Step 2: Rn-M' 선의 식과 equilibrium curve 교점 찾기
A_RnMp, B_RnMp, C_RnMp = line(pt_Rn, pt_Mp)
m_RnMp = (pt_Mp[1] - pt_Rn[1]) / (pt_Mp[0] - pt_Rn[0])
b_RnMp = pt_Rn[1] - m_RnMp * pt_Rn[0]
def diff_spline_vs_RnMp(x):
    return spline(x) - (m_RnMp * x + b_RnMp)

# 교점 x 좌표 찾기
x_check = np.linspace(0, min(pt_Rn[0], pt_Mp[0]), 10000)
xL, xR = None, None
for i in range(len(x_check) - 1):
    y1 = diff_spline_vs_RnMp(x_check[i])
    y2 = diff_spline_vs_RnMp(x_check[i + 1])
    if y1 * y2 < 0:
        xL = x_check[i]
        xR = x_check[i + 1]
        break

if xL and xR:
    x_E1p = brentq(diff_spline_vs_RnMp, xL, xR)
    y_E1p = spline(x_E1p)
    pt_E1p = (x_E1p, y_E1p)
else:
    pt_E1p = None

print(f"내분점 M' = ({pt_Mp[0]:.3f}, {pt_Mp[1]:.3f})")
print(f"\nE1' = ({pt_E1p[0]:.3f}, {pt_E1p[1]:.3f})")
print("PA: {:.3f} wt%, n-BP: {:.3f} wt%, water: {:.3f} wt%".format(*xy_to_comp(pt_E1p[0], pt_E1p[1])))

ax.plot(*pt_Mp, 'o', color='brown', markersize=4)
ax.text(pt_Mp[0], pt_Mp[1] + 3, r"$\mathbf{M'}$", color='brown', fontsize=10)
ax.plot(*pt_E1p, 'ro', markersize=4)
ax.text(pt_E1p[0]-6, pt_E1p[1] - 3, r"$\mathbf{E'_{1}}$", color='red', fontsize=10)
ax.plot([pt_Rn[0], pt_E1p[0]], [pt_Rn[1], pt_E1p[1]], '-', color='brown', linewidth=1)

ax.plot(*pt_R0p, 'o', color='blue', markersize=4)
ax.text(pt_R0p[0] + 1.5, pt_R0p[1] + 1.5, r"$\mathbf{R'_{0}}$", color='blue', fontsize=10)
ax.plot([pt_R0p[0], pt_En1[0]], [pt_R0p[1], pt_En1[1]], '-', color='brown', linewidth=1)

ax.legend()
plt.tight_layout()
plt.savefig('Fig6(a)', bbox_inches='tight', dpi=300)
plt.show()

# %% 16. [Fig 6(b)] Feed concentration (25 wt% PA)

fig, ax = plt.subplots(figsize=(8, 8))
setup_ternary_axis(ax)

# Plot R0, Rn, En1, E1
ax.plot(*pt_R0, 'bo', markersize=4)
ax.text(pt_R0[0] + 1.5, pt_R0[1] + 1.5, r"$\mathbf{R_0}$", color='blue', fontsize=10)
ax.plot(*pt_Rn, 'bo', markersize=4)
ax.text(pt_Rn[0] + 1.5, pt_Rn[1] + 1.5, r"$\mathbf{R_n}$", color='blue', fontsize=10)
ax.plot(*pt_E1, 'ro', markersize=4)
ax.text(pt_E1[0] - 3, pt_E1[1] + 1.5, r"$\mathbf{E_1}$", color='red', fontsize=10)
ax.plot(*pt_En1, 'ro', markersize=4)
ax.text(pt_En1[0] - 8, pt_En1[1] - 4, r"$\mathbf{E_{n+1}}$", color='red', fontsize=10)

ax.plot([pt_E1[0], pt_Rn[0]], [pt_E1[1], pt_Rn[1]], '-', color='purple', linewidth=1)
ax.plot([pt_En1[0], pt_R0[0]], [pt_En1[1], pt_R0[1]], '-', color='purple', linewidth=1)
ax.plot(*pt_M, 'o', color='purple', markersize=3)
ax.text(pt_M[0], pt_M[1] + 3, r"$\mathbf{M}$", color='purple', fontsize=10)

# Feed concentration 25 wt% PA
wpa_R0p = 25
wbp_R0p = 75
x_R0p = wbp_R0p + 0.5 * wpa_R0p
y_R0p = (np.sqrt(3) / 2) * wpa_R0p
pt_R0p = (x_R0p, y_R0p)

# Step 1: R0-En+1 선분을 En1:R0 로 내분하는 점 M'
total = En1 + R0
pt_Mp = (
    (R0 * pt_R0p[0] + En1 * pt_En1[0]) / total,
    (R0 * pt_R0p[1] + En1 * pt_En1[1]) / total,
)

# Step 2: Rn-M' 선의 식과 equilibrium curve 교점 찾기
A_RnMp, B_RnMp, C_RnMp = line(pt_Rn, pt_Mp)
m_RnMp = (pt_Mp[1] - pt_Rn[1]) / (pt_Mp[0] - pt_Rn[0])
b_RnMp = pt_Rn[1] - m_RnMp * pt_Rn[0]
def diff_spline_vs_RnMp(x):
    return spline(x) - (m_RnMp * x + b_RnMp)

# 교점 x 좌표 찾기
x_check = np.linspace(0, min(pt_Rn[0], pt_Mp[0]), 10000)
xL, xR = None, None
for i in range(len(x_check) - 1):
    y1 = diff_spline_vs_RnMp(x_check[i])
    y2 = diff_spline_vs_RnMp(x_check[i + 1])
    if y1 * y2 < 0:
        xL = x_check[i]
        xR = x_check[i + 1]
        break

if xL and xR:
    x_E1p = brentq(diff_spline_vs_RnMp, xL, xR)
    y_E1p = spline(x_E1p)
    pt_E1p = (x_E1p, y_E1p)
else:
    pt_E1p = None

print(f"내분점 M' = ({pt_Mp[0]:.3f}, {pt_Mp[1]:.3f})")
print(f"\nE1' = ({pt_E1p[0]:.3f}, {pt_E1p[1]:.3f})")
print("PA: {:.3f} wt%, n-BP: {:.3f} wt%, water: {:.3f} wt%".format(*xy_to_comp(pt_E1p[0], pt_E1p[1])))

ax.plot(*pt_Mp, 'o', color='brown', markersize=4)
ax.text(pt_Mp[0], pt_Mp[1] - 3, r"$\mathbf{M'}$", color='brown', fontsize=10)
ax.plot(*pt_E1p, 'ro', markersize=4)
ax.text(pt_E1p[0]-4, pt_E1p[1], r"$\mathbf{E'_{1}}$", color='red', fontsize=10)
ax.plot([pt_Rn[0], pt_E1p[0]], [pt_Rn[1], pt_E1p[1]], '-', color='brown', linewidth=1)

ax.plot(*pt_R0p, 'o', color='blue', markersize=4)
ax.text(pt_R0p[0] + 1.5, pt_R0p[1] + 1.5, r"$\mathbf{R'_{0}}$", color='blue', fontsize=10)
ax.plot([pt_R0p[0], pt_En1[0]], [pt_R0p[1], pt_En1[1]], '-', color='brown', linewidth=1)

ax.legend()
plt.tight_layout()
plt.savefig('Fig6(b)', bbox_inches='tight', dpi=300)
plt.show()

"""
고생하셨습니다~
"""
# %%
