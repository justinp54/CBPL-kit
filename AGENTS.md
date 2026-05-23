# CBPL-kit — Agent Operating Rules

This is the authoritative guide for AI coding assistants working in this repository.

## Project Overview

CBPL-kit provides interactive simulation tools for SNU CBE lab experiments.

- **Web app**: `cbpl-kit.vercel.app` — Pyodide (Python runs in browser, no server)
- **Python package**: `experiments/experiment_NN/` — importable modules + Jupyter notebooks
- **Current scope**: Experiment 06 (LLE Hunter-Nash). Experiments 04, 05 exist as Python modules only.

## Repository Layout

```
experiments/
  experiment_06/     ← Python computation modules (source of truth)
    config.py        ← all experimental constants (V_R0, V_E1, V_RN, flow rates, EQUIL_DATA)
    equilibrium.py   ← EquilibriumSystem dataclass
    conjugate.py     ← ConjugateCurve dataclass
    hunter_nash.py   ← HunterNashSolver, Step dataclasses
    lever_rule.py    ← find_M_and_P, mixing_point, find_E1_prime
    ternary.py       ← comp_to_xy, xy_to_comp
    plot_util.py     ← Plotly figure builders (fig_*)
    main.py          ← orchestration, StreamPoints dataclass
    demo.ipynb       ← Jupyter walkthrough
public/
  index.html         ← Single-page web app (Pyodide)
  exp06/             ← COPY of experiment_06 Python files for browser serving
api/
  compute.py         ← Legacy Vercel serverless handler (kept as fallback)
dev_server.py        ← Local development server
```

## Critical: File Sync Rule

`public/exp06/` is a copy of `experiments/experiment_06/` Python files.  
**After editing any `.py` file under `experiments/experiment_06/`, always copy:**

```bash
cp experiments/experiment_06/{config,ternary,equilibrium,conjugate,hunter_nash,lever_rule,plot_util}.py public/exp06/
```

Forgetting this means the web app uses stale code while the Python package is updated.

## Coding Conventions (see CBPL_PATTERNS.md for full detail)

1. **ASCII-only Python source** — no Korean or other non-ASCII in `.py` files.
2. **Plot functions return `go.Figure`** — never call `.show()` or save inside a plot function.
3. **Config is module-level constants** — users override via `import config; config.V_E1 = 3.95`.
4. **Dataclasses with `__post_init__`** — build expensive objects (splines, polynomials) once at construction.
5. **Pure functions** — no global state in calculation modules.
6. **Type hints required** on all public functions.
7. **`Path` over `os`** everywhere for file I/O.

## How to Add a New Experiment

1. Create `experiments/experiment_NN/` with `config.py`, computation modules, `plot_util.py`, `__init__.py`.
2. Follow the pattern in `experiments/experiment_06/` (see `CBPL_PATTERNS.md`).
3. Copy Python files to `public/expNN/`.
4. Create `public/expNN/index.html` based on `public/index.html` — change only the module paths and Python computation code.
5. Update `vercel.json` rewrite to exclude `/expNN` from SPA redirect.

## Web App Architecture (Pyodide)

The web app runs Python in the browser via WebAssembly:
- `initPyodide()` fetches `.py` files from `/exp06/`, writes to Pyodide's virtual filesystem, imports modules.
- `calculate()` sets config globals in Python, runs the computation, returns Plotly JSON.
- `computeExplorer('sf'|'feed')` computes a single frame (~20ms) for real-time slider interaction.
- Equilibrium system (`_system`, `_conjugate`) is built once and cached in Python builtins.

## Local Development

```bash
python dev_server.py 8080   # serves public/ + legacy experiments/ paths
# Open http://localhost:8080
```

## Code Style & Quality Tools

### Recommended: ruff (linter + formatter)

```bash
pip install ruff
ruff check experiments/     # lint
ruff format experiments/    # format (black-compatible)
```

Key rules enforced (see `pyproject.toml`):
- **E/W** — PEP 8 style
- **F** — Pyflakes (unused imports, undefined names)
- **I** — isort (import ordering: stdlib → third-party → local)
- **N** — naming conventions (functions snake_case, classes PascalCase)
- **UP** — use modern Python syntax (`list[float]` over `List[float]`, etc.)

### Type hints
All public functions must have type annotations.  
Use `float | None` (Python 3.10+ union) not `Optional[float]`.  
Use `npt.NDArray[np.float64]` for numpy array parameters.

### Naming
- Functions: `snake_case` — `find_M_and_P`, `comp_to_xy`
- Classes: `PascalCase` — `EquilibriumSystem`, `ConjugateCurve`
- Constants in `config.py`: `UPPER_CASE` — `EQUIL_DATA`, `V_R0`
- Private helpers: prefix `_` — `_line_coeffs`, `_titration_c`

### Comments
Write **no comments** unless the WHY is non-obvious (a constraint, a workaround, a subtle invariant).  
Do not comment WHAT the code does — well-named identifiers already do that.

### Docstrings
One-line docstrings on classes and public functions only.  
No multi-paragraph docstrings. No parameter lists in docstrings.

---

## Standard Workflow

When uncertain, choose the safest action — prefer explaining the design over making risky patches.

1. Reuse existing modules and utilities before writing new code.
2. For any non-trivial change, verify the computation result matches the legacy file (`experiments/experiment_06/legacy/`) before committing.
3. If you cannot run the code in the current environment, instruct the developer to run it and paste failures — do not claim it was tested.
4. Provide a brief summary of what changed and why at the end of any patch.

## Hard Guardrails

### Never modify without explicit instruction
- `requirements.txt` — Pyodide compatibility must be verified first
- `vercel.json` — routing changes can break the deployed site
- `public/index.html` — test locally before committing

### Code quality
- No `# type: ignore`, `# noqa`, or suppression comments — fix the root cause instead.
- No dead code left as comments — delete it cleanly.
- No placeholder strings like `"coming soon"` or `"TODO"` in user-facing text.
- Keep functions short and single-purpose. If a function is doing two things, split it.

### Import discipline
- New modules should use unconditional top-level imports.
- The existing `try/except ImportError` pattern in `experiments/` is a legacy compatibility shim — do not extend it to new files.
- Do not use `sys.path` manipulation outside of `dev_server.py` and `api/compute.py`.

### Numerical correctness
- Any algorithm change in the computation modules must be validated against the legacy output in `experiments/experiment_06/legacy/Exp_6_LLE_Hunter_Nash_revised.py`.
- Do not change scipy solver bounds, tolerances, or polynomial degrees without understanding the impact on the conjugate curve and plait point.

## Constraints

- Do not modify `requirements.txt` without checking Pyodide compatibility — packages must be installable via `micropip` or available as Pyodide built-ins.
- Do not add `try/except` import blocks in new modules — use proper package structure.
- Keep `public/exp06/` in sync with `experiments/experiment_06/` at every commit.
