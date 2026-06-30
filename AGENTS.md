# CBPL-kit — Agent Operating Rules

Authoritative guide for AI coding assistants working in this repository.

## Project Overview

CBPL-kit provides interactive simulation tools for SNU CBE lab experiments.

- **Web app**: `cbpl-kit.vercel.app` — Pyodide (Python runs in browser, no server)
- **Python package**: `experiments/experiment_NN/` — importable modules + Jupyter notebooks
- **Current scope**: Experiment 06 (LLE Hunter-Nash) is the main web app. Experiments 04, 05 exist as Python modules only.

## Repository Layout

```
public/
  index.html           ← HTML structure only (307 lines)
  css/style.css        ← All CSS (teal-blue palette, IBM Plex Sans)
  js/app.js            ← All JS logic (Pyodide, Plotly, forms)
  exp06/               ← Python modules (browser serving copy)
  systems/             ← YAML system definition files
    index.json         ← Dropdown manifest
  docs/guide.md        ← Guide tab markdown
experiments/
  experiment_04/       ← Python only (no web integration)
  experiment_05/       ← Python only (no web integration)
  experiment_06/       ← Python module source + Jupyter notebooks
    systems/           ← YAML (must stay in sync with public/systems/)
dev_server.py          ← Local dev server (port 8080)
```

## Critical: File Sync Rule

`public/exp06/` and `experiments/experiment_06/` Python files must always be identical.

```bash
cp experiments/experiment_06/{config,ternary,equilibrium,conjugate,hunter_nash,lever_rule,plot_util}.py public/exp06/
```

Forgetting this means the web app uses stale code while the Python package is updated.

## Common Tasks

### Adding a YAML system

1. Create YAML file in `public/systems/` (follow existing format)
2. Add entry to `public/systems/index.json`
3. Copy to `experiments/experiment_06/systems/`
4. git push

### Modifying the System tab

- HTML structure: `public/index.html` (`.sys-*` class elements)
- Styles: `public/css/style.css` (`.sys-select`, `.sys-form-*`, `.sys-editable`, etc.)
- JS logic: `public/js/app.js` (`loadSystemTab`, `applySystem`, `validateForm`, `collectFormToYaml`)

### Modifying tab labels or UI copy

- Tab labels: `public/index.html` (`.tab-btn` elements)
- Error/status messages: `public/js/app.js` (`setSysMsg` call sites)
- Guide content: `public/docs/guide.md` (markdown)

### Modifying Python computation

- Modules: edit `public/exp06/*.py`, then sync to `experiments/experiment_06/`
- Charts: `plot_util.py` `fig_*()` functions
- **Warning**: `_layout()` and `_cart_layout()` are shared — override per-chart via `fig.update_layout()` only

## Coding Conventions

1. **ASCII-only Python source** — no Korean or non-ASCII in `.py` files
2. **Plot functions return `go.Figure`** — never call `.show()` inside
3. **Dataclasses with `__post_init__`** — build expensive objects (splines, polynomials) once at construction
4. **Pure functions** — no global state in calculation modules
5. **Type hints required** on all public functions
6. **No dead code** — delete commented-out code, no `# TODO` in user-facing text
7. **No comments** unless the WHY is non-obvious (a constraint, a workaround, a subtle invariant)

## Hard Guardrails

### Confirm before modifying
- `pyproject.toml` — check Pyodide compatibility before adding dependencies
- `vercel.json` — routing changes can break the deployed site
- `plot_util.py` `_layout()` / `_cart_layout()` — shared functions, never modify for a single chart

### Never rename
Python internal variables: `wpa`, `wbp`, `ww`, `RHO_PA`, `RHO_BP`, `RHO_W`, `MW_PA`.
Use `"carrier"` key and `labels.abbr` only in YAML and UI.

### Numerical correctness
Any algorithm change must be validated against legacy output in `experiments/experiment_06/legacy/`.
Do not change scipy solver bounds, tolerances, or polynomial degrees without understanding impact.

## How to Add a New Experiment

1. Create `experiments/experiment_NN/` following exp06 patterns (`config.py`, computation modules, `plot_util.py`)
2. Copy Python files to `public/expNN/`
3. Create `public/expNN/index.html` — share `public/css/style.css` for design consistency
4. Update `vercel.json` rewrite to exclude `/expNN` from SPA redirect
5. Later: `public/index.html` becomes a landing page (ROADMAP Phase 7)

## Web App Architecture (Pyodide)

- `initPyodide()` fetches `.py` files from `/exp06/`, writes to Pyodide virtual filesystem, imports modules
- `renderSystemFigs()` auto-renders Equilibrium + Conjugate charts on system load (no Calculate needed)
- `calculate()` sets config globals in Python, runs computation, returns Plotly JSON
- `computeExplorer('sf'|'feed')` computes a single frame for real-time slider interaction
- Sidebar auto-collapses on ternary tabs, auto-expands on extraction tabs
- System switching uses `Plotly.purge()` before `Plotly.newPlot()` to avoid stale chart state

## Local Development

```bash
python dev_server.py        # http://localhost:8080
# Ctrl+Shift+R in browser (hard refresh)
```

## Git Rules

- Confirm with user before committing
- Commit messages: short, conventional prefix (feat, fix, chore, docs)
- No Co-Authored-By needed
- Vercel Hobby: only repo owner triggers deploys (teammate push requires owner empty commit)
