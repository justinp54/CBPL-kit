# CBPL-kit Roadmap

## Vision

An interactive web toolkit for SNU CBE lab experiments: runs in the browser
with no installation, customizable with your own experimental data, and easy
to hand off to next year's students.

---

## Deployment

| Channel | URL | Status |
|---------|-----|--------|
| Web app (Vercel) | https://cbpl-kit.vercel.app | Live (main branch) |
| Source | https://github.com/justinp54/CBPL-kit | Public |
| Zenodo DOI | — | Pending (do before paper submission) |

**Architecture:** Pyodide — Python runs entirely in the browser (no server,
no cold start). Python modules served from `public/exp06/`.

> ⚠ `public/exp06/*.py` and `experiments/experiment_06/*.py` must be kept
> in sync. After editing experiment modules, copy to `public/exp06/`.

---

## Experiment Status

| Experiment | Python Modules | Web App | Notebook |
|------------|---------------|---------|----------|
| Exp 06 — LLE Hunter-Nash | Done | **Live** | `demo.ipynb` (partial) |
| Exp 04 — VLE (Modified Raoult / PR EOS) | Done | Not started | `exp_05.ipynb` (partial) |
| Exp 05 — McCabe-Thiele Distillation | Done | Not started | `test.ipynb` |
| Exp 01, 02, 03 | Not started | — | — |

---

## Phase 1 — Documentation ✓ Completed

- [x] Extract coding patterns → `CBPL_PATTERNS.md`
- [x] Write `ROADMAP.md`

## Phase 2 — Experiment 06 Web App ✓ Completed

- [x] Modular Python package (equilibrium, conjugate, hunter_nash, lever_rule, plot_util)
- [x] Pyodide deployment on Vercel (browser-side Python, no server)
- [x] Real-time S:F Explorer — slider computes single frame instantly (~20ms)
- [x] Real-time Feed Explorer — same approach
- [x] Auto-recalculate on sidebar input change (250ms debounce)
- [x] Number inputs + sliders for all parameters
- [x] Legend moved outside ternary for clean layout
- [x] `StreamPoints` dataclass, `conjugate.py` ValueError on solver failure
- [x] `experiments/experiment_04/__init__.py` added

## Phase 3 — Multi-System & Onboarding ✓ Completed

- [x] **Guide tab** — `public/docs/guide.md` rendered via marked.js; default active tab
  on load so users read usage instructions while Pyodide initialises
- [x] **System ✦ tab** — YAML textarea + Apply System; js-yaml parses in JS,
  rebuilds `EquilibriumSystem` + `ConjugateCurve` in Pyodide
- [x] **YAML system definition** — `systems/nbp_pa_water.yaml` covers equilibrium
  data, tie lines, and physical properties; human-editable without touching Python
- [x] **config.py → YAML** — thermodynamic data loaded from YAML; only experiment
  defaults (V_R0, V_E1, V_RN, flow rates) remain hardcoded in config.py
- [x] **`EquilibriumSystem.from_yaml()`** — classmethod for Python / Jupyter users
- [x] **Robustness fixes** — equilibrium data auto-sorted by ternary x; near-duplicate
  point detection with clear error; conjugate polynomial degree auto-fallback (4→3→2)

## Phase 4 — Paper Preparation (next)

- [ ] **Zenodo DOI** — GitHub release → Zenodo webhook (10 min, do first)
- [ ] **CITATION.cff** — machine-readable citation file (GitHub "Cite this repo" button)
- [ ] **`git tag v1.0.0`** — pin version before Zenodo snapshot
- [ ] **README** — add DOI badge after Zenodo

## Phase 5 — Future Features

- [ ] **Conjugate curve degree adaptive** — auto-set `degree = min(4, n_ties)` at init
- [ ] **Exp 04 web app** — VLE simulator (Python done, needs Plotly UI)
- [ ] **Exp 05 web app** — McCabe-Thiele (image digitization → canvas click)
- [ ] **Landing page** — experiment selector when multiple apps exist
- [ ] **Service Worker caching** — eliminate 20 s Pyodide cold start on repeat visits

---

## Design Constraints

- **Browser-first**: Pyodide runs Python client-side; no server dependency
- **ASCII-only** Python source (no Korean comments in `.py` files)
- **Config is overridable** — titration volumes / flow rates in `config.py`
- **Plot functions return figures** — never call `.show()` inside
- **public/exp06/ sync** — always copy edited modules before committing

## How to Run Locally

```bash
# Start dev server
python dev_server.py 8080
# Open http://localhost:8080
```

## How to Update Deployed Python Modules

```bash
# After editing experiments/experiment_06/*.py:
cp experiments/experiment_06/{config,ternary,equilibrium,conjugate,hunter_nash,lever_rule,plot_util}.py public/exp06/
git add public/exp06/ experiments/experiment_06/
git commit -m "..."
git push origin main
```
