# CBPL-kit — Agent Operating Rules

Authoritative guide for AI coding assistants working in this repository.

## Project Overview

CBPL-kit provides interactive simulation tools for SNU CBE lab experiments.

- **Web app**: `cbpl-kit.vercel.app` — Pyodide (Python runs in browser, no server)
- **Python package**: `experiments/experiment_NN/` — importable modules + Jupyter notebooks
- **Current scope**: Experiment 06 (LLE Hunter-Nash) is the main web app. Experiments 04, 05 exist as Python modules only.

**Read `CLAUDE.md` → "Domain Primer" before touching any calculation module.** This is
liquid-liquid extraction: the numbers have physical meaning, and neither ruff nor pytest
can tell you that a result is thermodynamically impossible. The primer lists the
invariants and the mistakes this codebase has already made.

## Repository Layout

```
public/
  index.html           ← HTML structure only (tabs, sidebar, form, data panel)
  css/style.css        ← All CSS (teal-blue palette, IBM Plex Sans)
  js/app.js            ← All JS logic (Pyodide, Plotly, forms, Contact pane)
  exp06/               ← Python modules (browser serving copy)
  systems/             ← YAML system definition files
    index.json         ← Dropdown manifest (filename list)
  docs/guide.md        ← Guide tab markdown
  images/              ← Static assets (whitelisted in .gitignore)
experiments/
  experiment_04/       ← Python only (no web integration)
  experiment_05/       ← Python only (no web integration)
  experiment_06/       ← Python module source + Jupyter notebooks
    systems/           ← YAML (must stay in sync with public/systems/)
    tests/             ← pytest suite (the only pyproject testpaths entry)
scripts/
  check_dual_copy.py   ← Enforces the file sync rule below
.github/workflows/
  ci.yml               ← ruff + dual-copy check + pytest, on push to main and every PR
  validate-system-submission.yml  ← Runs validate_system.py on `system`-labelled issues
dev_server.py          ← Local dev server (port 8080)
```

External JS/CSS in `index.html` is **version-pinned with SRI hashes** (Pyodide, Plotly,
marked, js-yaml, JSZip, SheetJS, KaTeX). Never loosen a pin to `@latest` — the pinning is
what lets an archived snapshot of this repo reproduce the same results years later.

## Critical: File Sync Rule

`public/exp06/` and `experiments/experiment_06/` Python files must always be identical.

```bash
cp experiments/experiment_06/{config,ternary,equilibrium,conjugate,correlation,hunter_nash,lever_rule,plot_util,validate_system}.py public/exp06/
python scripts/check_dual_copy.py    # exits 0 + "OK", or prints unified diffs
```

Forgetting this means the web app uses stale code while the Python package is updated.
CI runs the check on every push and PR, so a missed copy fails the build. Files that
exist only in `experiments/experiment_06/` (`main.py`, `__init__.py`) are exempt; the
check also compares every YAML listed in `public/systems/index.json`.

> **Status: temporary.** Only needed because there is no build step. ROADMAP Phase 7.4
> replaces it with a Python package; the rule, `scripts/check_dual_copy.py`, the CI step,
> and this note are all deleted together at that point.
>
> Until then it is **fully binding**, and it is not a rule to route around — if it feels
> like an obstacle, that is Phase 7.4's problem, not something to solve locally.

## Common Tasks

### Adding a YAML system

1. Create YAML file in `public/systems/` (follow existing format)
2. Add the filename to `public/systems/index.json` (just the filename — dropdown label auto-built from `components` + `note`)
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
- Tie-line correlations (Othmer-Tobias / Hand / Bachman), selectivity, Hand-coordinate
  plait point: `correlation.py`
- YAML structural rules: `validate_system.py` — single source of truth for both the
  System tab (via Pyodide) and the submission GitHub Action. Change it in one place only.
- **Warning**: `_layout()` and `_cart_layout()` are shared — override per-chart via `fig.update_layout()` only
- After editing, run the checks in "Local Development" below

## Coding Conventions

1. **ASCII-only Python source** — no Korean or non-ASCII in `.py` files
2. **Plot functions return `go.Figure`** — never call `.show()` inside
3. **Dataclasses with `__post_init__`** — build expensive objects (splines, polynomials) once at construction
4. **Pure functions** — no global state in calculation modules
5. **Type hints required** on all public functions
6. **No dead code** — delete commented-out code, no `# TODO` in user-facing text
7. **No comments** unless the WHY is non-obvious (a constraint, a workaround, a subtle invariant)

## Patterns

Worked examples of the rules above. The audience is a student running Jupyter, not a
CLI power user — that constraint drives most of these choices.

### Package structure

Every experiment directory needs `__init__.py`, or it is not a package and imports fail:

```python
# experiments/experiment_05/__init__.py
from .main import load_vle_data, main
from .mccabe import compute_total_reflux, digitize_curve_from_image, set_equilibrium_data

__all__ = ["main", "load_vle_data", ...]
```

### Config is overridable because imports are live references

All experimental constants live in `config.py` as module-level values:

```python
V_R0: float = 10.78   # feed titration volume [mL]
FLOW_SOLVENT_ML_MIN: float = 100.0
```

A student overrides them in a notebook cell before calling `main()`:

```python
import experiments.experiment_06.config as cfg
cfg.V_E1 = 3.95   # my measured titration volume
```

This works because a Python import is a live reference to the module object — reassigning
the attribute changes what every function reading it sees. Do not defeat this by copying
config values into local variables at import time.

### Build derived state once, in `__post_init__`

```python
@dataclass
class EquilibriumSystem:
    _spline: CubicSpline = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._spline = CubicSpline(...)
```

`field(init=False, repr=False)` keeps the cache out of the constructor signature and out
of `repr()`. Never rebuild a spline inside a method.

### Return a named dataclass, not a bare tuple

```python
# Bad — the caller has to remember that position 0 is R0
pt_R0, pt_E1, pt_Rn, pt_En1, wpa, wbp = compute_stream_points(system)

# Good — self-describing in any notebook cell
sp = compute_stream_points(system)
fig = plot_lever_rule(sp.pt_R0, sp.pt_Rn, ...)
```

### Early return for preconditions

```python
def find_E1_prime(...) -> tuple[float, float] | None:
    if abs(b2 - b1) < 1e-12:
        return None   # parallel lines; no intersection exists
    ...
```

Main logic stays at indentation level 1, never buried in an `else`.

### numpy types at the boundary

Annotate arrays with `npt.NDArray[np.float64]`, and **wrap scalar returns in `float()`** —
callers expect a Python `float`, not an `np.float64`:

```python
return float(x_pp), float(self.eval(x_pp))
```

### Raise on solver failure; never fall back silently

```python
raise ValueError(
    "Conjugate-curve extension never re-enters the equilibrium "
    "curve's domain — check this system's tie-line data."
)
```

A silent fallback produces a plausible-looking but wrong figure, which is worse than a
crash. The message must say what to inspect — these errors surface directly in the
browser UI, where the reader is a student, not a developer.

### Plotting

Plotly builders return the figure so the caller decides what to do with it:

```python
fig = fig_ternary_equilibrium(system)
fig.show()                          # notebook
fig.write_html("outputs/fig1.html") # sharing
```

Matplotlib (exp04/05) takes `show` and `save_path` as separate parameters, and **always**
calls `plt.close()` — open figures accumulate:

```python
def plot_vle_comparison(..., save_path: Path | None = None, show: bool = True) -> None:
    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    plt.close()
```

### `Path`, never `os`

```python
output_dir = Path(__file__).resolve().parent / "outputs"
output_dir.mkdir(parents=True, exist_ok=True)
```

## What NOT to use here

These are competent patterns from other projects that are deliberately excluded. Rejecting
them is a decision, not an oversight — do not reintroduce them without a reason.

| Pattern | Why excluded |
|---------|-------------|
| Typer / Click CLI | Users run notebook cells, not terminal commands |
| Pydantic `BaseModel` | Overkill for a config of ~10 floats; `validate_system.py` covers the real validation need |
| `joblib.Parallel`, multiprocessing | Single-experiment jobs; overhead exceeds benefit, and Pyodide is single-threaded anyway |
| `uv` / `pre-commit` / `mypy` | Infrastructure barrier for student contributors; ruff + pytest in CI is the whole toolchain |
| `try/except` import blocks | Fix the package structure instead |
| Heavy deps (networkx, pandas) | Every import costs Pyodide load time in the browser |

## Pattern Index

| Pattern | Reference file |
|---------|------|
| Package export | `experiment_05/__init__.py` |
| Config override in Jupyter | `experiment_06/config.py` |
| Dataclass + `__post_init__` | `experiment_06/equilibrium.py` |
| Named result dataclass | `experiment_06/main.py` (`StreamPoints`) |
| Pure functions, no global state | `experiment_06/ternary.py` |
| Early return for edge cases | `experiment_06/lever_rule.py` |
| `npt.NDArray` + `float()` wrap | `experiment_06/conjugate.py` |
| Raise on solver failure | `experiment_06/conjugate.py` |
| Plotly figure return | `experiment_06/plot_util.py` |
| Matplotlib show/save params | `experiment_04/plot_util.py` |
| `Path` over `os` | `experiment_04/main.py` |

## Hard Guardrails

### Confirm before modifying
- `pyproject.toml` — check Pyodide compatibility before adding dependencies
- `vercel.json` — routing changes can break the deployed site
- `plot_util.py` `_layout()` / `_cart_layout()` — shared functions, never modify for a single chart

### Never rename
Python internal variables: `wpa`, `wbp`, `ww`, `RHO_PA`, `RHO_BP`, `RHO_W`, `MW_PA`.
Use `"carrier"` key and `labels.abbr` only in YAML and UI.

### Numeric index convention
Components are numbered **1 = carrier, 2 = solute, 3 = solvent**. Phases reuse the same
digits: **1 = carrier-rich (raffinate), 3 = solvent-rich (extract)**; there is no phase 2.
Two subscripts mean `w_ij` = mass fraction of component `i` in phase `j` — so `w21` is
solute in the carrier-rich phase and `w23` is solute in the solvent-rich phase.

This is shared by the YAML comments, `correlation.py`, and the manuscript, and it is
**not** Treybal's `A`/`B`/`C` lettering (Treybal's `B` is the solvent; our `2` is the
solute). Never mix the two in one figure or table. Full table with worked examples:
`CLAUDE.md` → "Numeric Index Convention".

### Numerical correctness
The regression baseline is `experiments/experiment_06/tests/`, which pins expected values
to full precision (e.g. `n_theory == pytest.approx(3.6118384065055205)`). Any algorithm
change must keep those tests green.

If a change is *supposed* to move a number, say so explicitly and update the expected value
in the same commit — never loosen `TOL` to make a test pass.

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
- `renderContactPane()` builds the Contact tab from `TEAM_DATA` at the top of `app.js`
- Sidebar auto-collapses on ternary tabs, auto-expands on extraction tabs
- System switching uses `Plotly.purge()` before `Plotly.newPlot()` to avoid stale chart state
- Tab order: Guide | System ✦ ‖ Equilibrium | Conjugate Curve ‖ Hunter-Nash | Stages |
  Lever Rule | S:F Explorer ✦ | Feed Explorer ✦ ‖ Contact
  (`‖` = `.tab-sep` divider, `✦` = interactive/editable marker in the label text)

## Local Development

```bash
python dev_server.py        # http://localhost:8080
# Ctrl+Shift+R in browser (hard refresh)
```

Before claiming a change is done, run all three — these are exactly what CI runs:

```bash
ruff check .
python scripts/check_dual_copy.py
python -m pytest experiments/experiment_06/tests/ -v
```

Test files: `test_equilibrium`, `test_conjugate`, `test_correlation`, `test_hunter_nash`,
`test_ternary`, `test_validate_system` (shared fixtures in `conftest.py` / `_helpers.py`).
A new computation module should arrive with its own `test_*.py`.

## Git Rules

- Confirm with user before committing
- Commit messages: short, conventional prefix (feat, fix, chore, docs)
- No Co-Authored-By needed
- Vercel Hobby: only repo owner triggers deploys (teammate push requires owner empty commit)
