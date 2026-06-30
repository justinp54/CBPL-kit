# How to Use — LLE Hunter-Nash Simulator

## Overview

This simulator applies the **Hunter-Nash graphical method** to liquid-liquid extraction (LLE) analysis. All computation runs entirely in your browser using Pyodide (Python in WebAssembly) — no server required.

**Default system:** n-Bromopropane (feed carrier) / Propionic Acid (solute) / Water (extracting solvent)

---

## Quick Start

1. Enter your **titration volumes** in the left sidebar
2. Enter your **flow rates**
3. Click **Calculate** (or press **Enter**)

Results appear in the sidebar and all figure tabs update automatically.

---

## Sidebar Inputs

### Titration Volumes

Titrations use **0.5 M NaOH**. Concentration is calculated as:

`c [mol/L] = 0.05 × V [mL]` (undiluted) — multiply by 10 for 10× diluted samples.

| Field | Stream | Sample preparation |
|-------|--------|--------------------|
| **V_R0** | Feed (R₀) | 10× diluted |
| **V_E1** | First extract (E₁) | 10× diluted |
| **V_Rn** | Final raffinate (Rₙ) | Undiluted |

Each value can be typed directly or adjusted with the slider below the field. The sliders auto-trigger recalculation after 250 ms.

### Flow Rates

| Field | Meaning |
|-------|---------|
| **Solvent (Water)** | Pure water (extracting solvent, Eₙ₊₁) volumetric flow [mL/min] |
| **Feed** | Feed stream volumetric flow [mL/min] |

---

## Figure Tabs

### Hunter-Nash *(default view)*

The main stepping diagram drawn on the ternary triangle.

- **Equilibrium curve** (binodal): phase boundary separating the two-phase region
- **Operating point P**: intersection of lines E₁–Rₙ and Eₙ₊₁–R₀
- **Tie lines**: each step connects a point on the left (extract) branch to the right (raffinate) branch, stepped via the conjugate curve
- **N_theoretical** (blue badge in the tab): number of equilibrium stages counted

### Equilibrium

Full ternary diagram with the equilibrium curve and all literature tie lines. The three vertices represent pure n-BP (right), pure PA (top), and pure Water (left).

### Conjugate Curve

Treybal's auxiliary-line construction for building the conjugate curve.

- Lines at ±60° from each tie-line endpoint intersect at one point on the **conjugate curve**
- The curve is fitted to a degree-4 polynomial through those intersection points
- It meets the binodal at the **plait point** (◆) — the critical point where the two phases become identical

### Tie Lines *(interpolated)*

Shows how the Hunter-Nash method interpolates new tie lines at each theoretical stage using the conjugate curve, rather than the original discrete data points.

### Lever Rule

Lever-rule mass-balance diagram at the experimental flow ratio.

| Point | Meaning |
|-------|---------|
| **R₀** | Feed (on BP–PA binary edge, no water) |
| **Eₙ₊₁** | Pure water inlet (left vertex, extracting solvent) |
| **M** | Overall mixing point (lever rule between R₀ and Eₙ₊₁) |
| **P** | Operating point (line M–Rₙ extended to the left branch) |
| **E₁′** | Predicted first extract — compare to your measured E₁ |

### S:F Explorer ✦

Real-time solvent-to-feed weight ratio explorer. Drag the slider or type a value to change the solvent fraction (40–97 wt%) and watch M and E₁′ update instantly.

- Find the **minimum solvent ratio** — when M approaches the equilibrium curve, the number of required stages goes to infinity
- Study trade-offs between solvent consumption and separation quality

### Feed Explorer ✦

Real-time feed composition explorer. Change the feed PA concentration (10–55 wt%) at your actual experimental flow rates to simulate a hypothetical richer or leaner feed.

> **Note:** The ✦ explorer tabs require at least one successful **Calculate** to initialise the shared computation state.

---

## System Configuration ✦

The **System** tab lets you load a different ternary system by pasting a YAML file.  
Edit the YAML directly in the text area and click **Apply System**.

A valid system YAML looks like this. The example below is the current default system, loaded live from `public/systems/nbp_pa_water.yaml` — edit that file and this example updates automatically:

```yaml
{{SYSTEM_YAML}}
```

After applying a new system, click **Calculate** to rebuild all figures.

---

## Tips

- Press **Enter** at any time to recalculate with the current sidebar values
- Scroll (mouse wheel) to zoom any figure; drag to pan
- Click legend entries to show or hide individual traces
- Hover over any data point for tooltips with exact composition values (wPA%, wBP%, wW%)
- The first page load takes ~20 seconds (Pyodide + packages); subsequent visits are cached by the browser
