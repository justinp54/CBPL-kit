# CBPL-kit

SNU CBE Chemical Engineering Lab — experiment data analysis & visualization toolkit.
Experiment 06 = LLE Hunter-Nash simulator (main project).
Deployed at cbpl-kit.vercel.app (Pyodide — Python runs in browser, no server needed)

## Architecture

```
public/
  index.html              ← HTML structure only (307 lines)
  css/style.css           ← All CSS (314 lines)
  js/app.js               ← All JS logic (935 lines)
  exp06/                  ← Python modules (loaded into Pyodide FS)
  systems/                ← YAML system definition files
    index.json            ← Dropdown manifest
    nbp_pa_water.yaml     ← Default system
  docs/guide.md           ← Guide tab content (rendered by marked.js)
experiments/
  experiment_04/          ← Python modules only (no web integration)
  experiment_05/          ← Python modules only (no web integration)
  experiment_06/          ← Local dev copy of exp06 Python modules
    systems/              ← YAML definitions (must stay in sync with public/systems/)
dev_server.py             ← Local dev server (port 8080)
```

## Dual-copy Rule

`experiments/experiment_06/*.py` and `public/exp06/*.py` must always be identical.
After any edit: `cp public/exp06/plot_util.py experiments/experiment_06/plot_util.py` (or vice versa).
YAML files in `experiments/.../systems/` and `public/systems/` must also stay in sync.

## Adding a New YAML System

1. Create YAML file in `public/systems/` (follow existing format)
2. Add entry to `public/systems/index.json`
3. Copy to `experiments/experiment_06/systems/`
4. git push → Vercel auto-deploys

### YAML Format

```yaml
name: System Name
components:
  solvent: {name: Water, abbr: W}
  solute: {name: Propionic Acid, abbr: PA}
  carrier: {name: n-Bromopropane, abbr: BP}
properties:
  rho_solvent: 1.0
  rho_solute: 0.993
  rho_carrier: 1.354
  mw_solute: 74.08
equilibrium_data:
  - [5.1, 9.49, 85.41]
tie_lines:
  - [6.253, 2.564]
```

- equilibrium_data: [wCarrier%, wSolute%, wSolvent%] — must be sorted by increasing carrier%
- tie_lines: [wSolute% solvent-rich, wSolute% carrier-rich]

## Python Modules (exp06)

| File | Role |
|------|------|
| `equilibrium.py` | Equilibrium data loading, spline fitting, `EquilibriumSystem` dataclass |
| `conjugate.py` | Conjugate curve (aux point calculation, PCHIP display, plait point search) |
| `hunter_nash.py` | Hunter-Nash stage calculation solver |
| `plot_util.py` | All Plotly figure builders |
| `lever_rule.py` | Lever rule calculations (M point, P point, E1') |
| `ternary.py` | Cartesian ↔ ternary coordinate conversion |
| `config.py` | Physical constants (loaded from YAML properties) |

## Web App Structure

- **index.html**: HTML structure only (tabs, sidebar, form, data panel)
- **css/style.css**: All styles (teal-blue palette, IBM Plex Sans)
- **js/app.js**: All JS logic
  - `PY_COMPUTE`: Python string executed via `pyodide.runPythonAsync()`
  - `renderSystemFigs()`: Auto-renders Equilibrium/Conjugate on system load
  - `applySystem()`: Parses YAML → updates properties/labels → rebuilds system
  - `validateForm()`: Validates empty values and sort order
  - `collectFormToYaml()`: Converts form inputs → YAML string
- **Tab order**: Guide | System ‖ Equilibrium | Conjugate ‖ Hunter-Nash | Tie Lines | Lever Rule | S:F Explorer | Feed Explorer
- **Sidebar**: Auto-collapses on ternary tabs, auto-expands on extraction tabs

## Plotly Chart Modification Rules

- `_layout()` and `_cart_layout()` in plot_util.py are **shared functions**. Never modify them for a single chart.
- For chart-specific layout changes, use `fig.update_layout()` inside the specific `fig_*()` function.
- Cartesian charts use `scaleanchor="x"` which ignores margin changes — adjust y_range or text positioning instead.

## Component Naming Convention

| Role | Code key | Internal variables (do not rename) |
|------|---------|---------------------|
| Solute | `"solute"` | `wpa`, `RHO_PA`, `MW_PA` |
| Carrier | `"carrier"` | `wbp`, `RHO_BP` |
| Solvent | `"solvent"` | `ww`, `RHO_W` |

**Never rename** internal Python variables: `wpa`, `wbp`, `ww`, `RHO_PA`, `RHO_BP`, `RHO_W`.
Use `"carrier"` key and `labels.abbr` only in YAML and UI.

## Development Workflow

```bash
python dev_server.py        # localhost:8080
# Ctrl+Shift+R in browser (hard refresh, bypass cache)
```

## Git Rules

- Always confirm with user before committing
- Commit messages: short, conventional prefix (feat, fix, chore, docs)
- No Co-Authored-By needed
- Vercel Hobby plan: only repo owner triggers deploys (teammate push requires owner empty commit)

## Adding a New Experiment

1. Create `experiments/experiment_NN/` following exp06 patterns
2. Copy Python files to `public/expNN/`
3. Create `public/expNN/index.html` — share `public/css/style.css` for design consistency
4. Later: convert `public/index.html` to a landing page, each experiment at its own path
