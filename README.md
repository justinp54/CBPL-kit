# CBPL-kit — Chemical & Biological Process Lab Toolkit

Interactive simulation and visualization tools for CBPL experiments at SNU CBE.  
Runs in the browser with no installation, or as a Python package in Jupyter.

**🌐 Web App → [cbpl-kit.vercel.app](https://cbpl-kit.vercel.app)**

---

## Motivation

Chemical and Biological Process Lab (CBPL) is a core laboratory course in the department of [Chemical and Biological Engineering at Seoul National University](https://cbe.snu.ac.kr/cbe/main/main.do).
CBPL experiments are notorious for their complexity and difficulty of analysis, often involving complex thermodynamic modeling, data processing, and visualization. However, since the primary focus of the department is not on software engineering, students face challenges in developing their own efficient and reusable tool for analyzing their experimental data. As a result, a significant amount of time is spent on debugging and troubleshooting, rather than understanding the underlying scientific principles, which can hinder the overall learning experience and limit productivity.

Therefore, CBPL-KIT aims to provide a standardized, modular toolkit that can be easily adapted to each individual's experimental datasets, enabling more efficient and structured analysis workflows, and ultimately enhancing the learning experience for students.

---

## Available Experiments

| Experiment | Description | Web App | Notebook |
|------------|-------------|---------|----------|
| **Exp 06 — LLE Hunter-Nash** | n-BP / Propionic Acid / Water | ✅ Live | `demo.ipynb` |
| Exp 04 — VLE | Modified Raoult / PR EOS | Coming soon | Available |
| Exp 05 — McCabe-Thiele | Distillation stage count | Coming soon | Available |

---

## Quick Start

### Option 1 — Browser (no installation required)

Open **[cbpl-kit.vercel.app](https://cbpl-kit.vercel.app)** in any browser.

Enter your titration volumes → click **Calculate** → all figures update instantly.  
The first load takes ~20 seconds (Python runs in browser via Pyodide); subsequent visits are cached.

### Option 2 — Jupyter Notebook

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
experiments/
  experiment_06/     ← LLE Hunter-Nash Python modules
    config.py        ← experimental constants (edit here)
    equilibrium.py   ← spline fit of equilibrium curve
    conjugate.py     ← conjugate curve & plait point
    hunter_nash.py   ← graphical stage-counting algorithm
    lever_rule.py    ← material balance calculations
    plot_util.py     ← Plotly figure builders
    demo.ipynb       ← step-by-step Jupyter walkthrough
public/
  index.html         ← web app (Python runs in browser)
  exp06/             ← Python modules served for browser execution
```

---

## Authors

| Name | Student ID |
|------|-----------|
| Junsang Park | 2023-16582 |
| Seong Lee | 2020-11063 |

Department of Chemical and Biological Engineering, Seoul National University

---

## Citation

A citable DOI will be added via Zenodo before publication.  
Source: https://github.com/justinp54/CBPL-kit

---

## Contributing

See [`AGENTS.md`](AGENTS.md) for coding conventions and patterns, and
[`ROADMAP.md`](ROADMAP.md) for planned features.
