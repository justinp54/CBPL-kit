# CBPL-kit — Chemical & Biological Process Lab Toolkit

Liquid-liquid extraction analysis for the process laboratory course at SNU CBE:
the Hunter-Nash construction carried out numerically on a ternary phase diagram.  
Runs in the browser with no installation, or as a Python package in Jupyter.

**🌐 Web App → [cbpl-kit.vercel.app](https://cbpl-kit.vercel.app)**

---

## Motivation

Chemical and Biological Process Lab (CBPL) is a core laboratory course in the department of [Chemical and Biological Engineering at Seoul National University](https://cbe.snu.ac.kr/cbe/main/main.do).
CBPL experiments are notorious for their complexity and difficulty of analysis, often involving complex thermodynamic modeling, data processing, and visualization. However, since the primary focus of the department is not on software engineering, students face challenges in developing their own efficient and reusable tool for analyzing their experimental data. As a result, a significant amount of time is spent on debugging and troubleshooting, rather than understanding the underlying scientific principles, which can hinder the overall learning experience and limit productivity.

Therefore, CBPL-KIT aims to provide a standardized, modular toolkit that can be easily adapted to each individual's experimental datasets, enabling more efficient and structured analysis workflows, and ultimately enhancing the learning experience for students.

---

## What it does

In the reference experiment, water extracts propionic acid out of n-bromopropane in a
counter-current packed column. You sample the feed, extract, and raffinate, titrate each
against NaOH, and from those three numbers determine how many equilibrium stages the
separation needs — by the **Hunter-Nash** construction on a ternary phase diagram, which
is normally drawn by hand on graph paper.

CBPL-kit runs that construction numerically, so changing one input and seeing the answer
costs a click instead of a redraw. There are two workflows:

| | You supply | You get |
|---|---|---|
| **Phase equilibrium** | equilibrium + tie-line data for a system | binodal curve, full tie-line compositions, conjugate curve, plait point, selectivity, Othmer-Tobias / Hand / Bachman correlations |
| **Extraction design** | …plus your own run: titration volumes and flow rates | stage count *N*, operating point, lever-rule check, S/F and feed-composition exploration |

The method assumes a **Type I** system — only carrier and solvent are partially miscible.
---

## Bundled systems

Seven ternary systems ship with the toolkit. Any of them can be loaded from the
**System** tab, and your own data can be entered there in the same form.

| Carrier | Solute | Solvent | Source |
|---------|--------|---------|--------|
| n-Bromopropane | Propionic acid | Water | SNU CBE — the reference experiment |
| Water | Acetic acid | Diisopropyl ether | Treybal (1980), 20 °C |
| Water | Acetone | 1,1,2-Trichloroethane | Seader (2006), 25 °C |
| Water | Ethylene glycol | Furfural | Seader (2006), 25 °C |
| Water | *tert*-Butyl alcohol | Diisobutylene | J. Chem. Eng. Data **33**, 258 (1988), 25 °C |
| Butyl acetate | Acetic acid | Water | Braz. J. Chem. Eng. **21**, 647 (2004), 25 °C |
| Cyclohexane | Propionic acid | Water | Braz. J. Chem. Eng. **21**, 647 (2004), 25 °C |

---

## Quick Start

### Option 1 — Browser (no installation required)

Open **[cbpl-kit.vercel.app](https://cbpl-kit.vercel.app)** in any browser.

Enter your titration volumes → click **Calculate** → all figures update instantly.  
The first load takes ~20 seconds (Python runs in browser via Pyodide); subsequent visits are cached.

### Option 2 — Jupyter Notebook

Python 3.10 or newer.

```bash
git clone https://github.com/justinp54/CBPL-kit.git
cd CBPL-kit
pip install -e .
jupyter notebook experiments/experiment_06/demo.ipynb
```

### Option 3 — Python Package

Override your experimental values and run:

```python
import experiments.experiment_06.config as cfg

cfg.V_R0 = 10.78   # feed titration volume [mL, 10× diluted]
cfg.V_E1 = 3.80    # extract titration volume [mL, 10× diluted]
cfg.V_RN = 0.64    # raffinate titration volume [mL, undiluted]
cfg.FLOW_SOLVENT_ML_MIN = 100.0
cfg.FLOW_FEED_ML_MIN    = 40.0

from experiments.experiment_06 import main
main(output_dir="experiments/experiment_06/outputs")
```

---

## Repository Structure

```
experiments/experiment_06/   ← the calculation modules, tests, and demo.ipynb
public/                      ← the web app: index.html, css/, js/, docs/guide.md
public/exp06/                ← the same calculation modules, served to the browser
*/systems/                   ← ternary system definitions, one YAML each
```

Each calculation module is one step of the analysis — `equilibrium.py` fits the binodal,
`conjugate.py` builds the conjugate curve and plait point, `hunter_nash.py` steps off the
stages, `lever_rule.py` closes the material balance, `correlation.py` fits the tie-line
correlations. `plot_util.py` draws every figure; nothing else touches Plotly.

**The two copies of those modules are byte-identical, and that is enforced.** The web app
runs Python in the browser through Pyodide, which needs the files under `public/`; there
is no build step to put them there. `scripts/check_dual_copy.py` compares the pair and CI
fails the push if they have drifted. Edit one, copy to the other, run the check.

---

## Development

```bash
pip install -e ".[dev]"

ruff check .                                         # lint
python scripts/check_dual_copy.py                    # the two module copies match
python -m pytest experiments/experiment_06/tests/    # 176 tests
python dev_server.py                                 # serve public/ at localhost:8080
```

CI runs the first three on every push and pull request.

---

## Authors

| Name | Student ID |
|------|-----------|
| Junsang Park | 2023-16582 |
| Seong Lee | 2020-11063 |

Department of Chemical and Biological Engineering, Seoul National University

---

## Citation

<!-- On the first Zenodo release, replace this block with the concept DOI badge and a
     BibTeX entry, and add the journal reference once the paper is accepted. -->
A citable DOI will be minted through Zenodo at the first release.  
Source: https://github.com/justinp54/CBPL-kit

---

## Contributing

See [`AGENTS.md`](AGENTS.md) for coding conventions and patterns.
