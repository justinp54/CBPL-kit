# CBPL-kit — Agent Operating Rules

Single source of truth for AI coding assistants. `CLAUDE.md` imports this file, so both
Claude Code and other agents read the same instructions — edit here, never in two places.

**Humans should read `README.md` instead** — it covers what the project is, how to run it,
and the repository layout. This file is about how to change the code without breaking it.

- **Web app**: `cbpl-kit.vercel.app` — Pyodide (Python runs in the browser, no server)
- **Scope**: Experiment 06 (LLE Hunter-Nash) — the deployed tool and the subject of the
  paper — is the whole of this repository.

---

## Domain Primer

**Read this before touching any calculation module.** Neither ruff nor pytest can tell you
that a result is thermodynamically impossible.

Liquid-liquid extraction (LLE) separates a **solute** out of a **carrier** liquid by
contacting it with a **solvent** that dissolves the solute but barely mixes with the
carrier. The **Hunter-Nash method** determines how many equilibrium stages a
counter-current extraction column needs, by geometric construction on a **ternary phase
diagram**. Undergraduates normally draw this by hand on graph paper; this tool does the
construction numerically so they can explore "what-if" instead of redrawing.

`public/docs/guide.md` is the student-facing explanation. This section is the minimum
needed to avoid making physically wrong changes.

### Vocabulary

| Term | Meaning |
|------|---------|
| **Ternary diagram** | Triangle where each point is one 3-component composition; each vertex is a pure component |
| **Binodal / equilibrium curve** | Boundary of the two-phase region. Inside it a mixture splits into two phases; outside it stays one phase |
| **Tie line** | Segment joining the two phases that a mixture inside the envelope actually splits into. Both endpoints lie **on** the binodal |
| **Conjugate curve** | Auxiliary construction used to interpolate a tie line at any composition, rather than only at the measured ones |
| **Plait point** | Where the two phases become identical and the tie line shrinks to zero length. The conjugate curve **terminates** here |
| **Raffinate (R)** | Carrier-rich product, depleted of solute — **phase 1** |
| **Extract (E)** | Solvent-rich product, enriched in solute — **phase 3** |
| **Mixing point M** | Composition of the overall mixture; found by the lever rule |
| **Operating point P** | Construction pole. Every stage's passing streams lie on a line through P |
| **S/F ratio** | Solvent-to-feed ratio — the main design knob |
| **N** | Number of theoretical stages |
| **S_min** | Smallest S/F at which the separation is still possible with finite stages |
| **Type I system** | Only the carrier-solvent pair is partially miscible; the solute is miscible with both. Hunter-Nash as implemented here assumes this |

### Physical invariants

Check any numerical change against these before believing it:

- The three mass fractions of a composition **always sum to 100 %**. A change that
  adjusts two of them and leaves the third is wrong.
- **Tie-line endpoints lie on the binodal.** An endpoint drifting off the curve means
  the interpolation is broken, not that the data is unusual.
- **The conjugate curve ends at the plait point.** Extrapolating past it is meaningless
  — beyond that point there are no two phases to connect.
- **N is a positive real, and a fractional value is correct**, not a bug to be rounded
  away. It means the last stage is partial.
- **S_min is derived from real measured tie lines only** — never from interpolated
  ones. Changing this silently changes every published S_min number.
- Composition ↔ concentration conversion is **iterative**, because a sample's density
  depends on its own solute content. Do not substitute the pure-carrier or pure-solvent
  density; avoiding exactly that approximation is one of the paper's claims.

### Mistakes this codebase has already made

- **`S_min` scanned only one leg of the sweep.** `P(frac)` moves non-monotonically along
  the Rn-En1 line and can pass through infinity. An earlier version checked only the
  `t > 1` leg; it happened to work for every system tried at the time, then reported
  "no S_min" for `w_acoh_dipe`, whose tie lines sit on the negative leg. The `JUMP`
  constant in `find_smin_construction` guards the infinity crossing — do not remove it.
- **The conjugate curve used to be a degree-4 polynomial fit**, which produced sharp
  kinks near the plait point. It is now branch-Hermite with a clamped-tangent extension.
  Any document or comment still mentioning `degree` or `polyfit` for it is stale.
- A plait point / conjugate change propagates to **N**, so it is never a local edit.

---

## Pyodide constraints

Anything imported by `public/exp06/*.py` is **downloaded into the user's browser**. The
runtime already loads numpy, scipy, pyyaml, and plotly, and cold start is already slow;
every added dependency is paid by every user, every first visit.

Pyodide is also single-threaded with no process fork, so `multiprocessing` / `joblib`
cannot run there at all. Its filesystem is flat, which is why these modules use flat
imports (`from ternary import ...`) rather than package-relative ones — do not paper over
that with `try/except` import blocks.

These limits apply to modules that ship to `public/exp06/`. Code under `experiments/` that
never reaches the browser is not bound by them.

External JS/CSS in `index.html` is **version-pinned with SRI hashes** (Pyodide, Plotly,
marked, js-yaml, JSZip, SheetJS, KaTeX). Never loosen a pin to `@latest` — the pinning is
what lets an archived snapshot of this repo reproduce the same results years later.

---

## Dual-copy Rule

`public/exp06/*.py` and `experiments/experiment_06/*.py` must always be identical.

```bash
cp experiments/experiment_06/{config,ternary,equilibrium,conjugate,correlation,hunter_nash,lever_rule,plot_util,validate_system}.py public/exp06/
python scripts/check_dual_copy.py    # exits 0 + "OK", or prints unified diffs
```

The deployed site runs the `public/exp06/` copy, so a missed sync means users get stale
code. CI runs the check on every push and PR. Files that exist only in
`experiments/experiment_06/` (`main.py`, `__init__.py`) are exempt; the check also
compares every YAML listed in `public/systems/index.json`.

> **Status: temporary.** Only needed because there is no build step. The internal roadmap
> replaces it with an installable Python package, at which point the rule,
> `scripts/check_dual_copy.py`, the CI step, and this note are all deleted together.
>
> Until then it is **fully binding**, and it is not a rule to route around — if it feels
> like an obstacle, that is the packaging work's problem, not something to solve locally.

---

## Component and phase numbering

| Role | Index | Code key | Internal variables (never rename) |
|------|-------|---------|---------------------|
| Carrier | **1** | `"carrier"` | `wbp`, `RHO_BP` |
| Solute | **2** | `"solute"` | `wpa`, `RHO_PA`, `MW_PA` |
| Solvent | **3** | `"solvent"` | `ww`, `RHO_W` |

Use the `"carrier"` key and `labels.abbr` in YAML and UI only. The manuscript, the YAML
comments, and `correlation.py` all share the numbering above — keep it consistent in any
new code, comment, figure label, or paper text.

**Phases reuse the same digits**, named after the component that dominates them: phase
**1** = carrier-rich = raffinate, phase **3** = solvent-rich = extract. There is no phase
2 — the solute is the distributed species, not a phase.

**Two subscripts mean `w_ij` = mass fraction of component `i` in phase `j`.**

| Symbol | Meaning |
|--------|---------|
| `w_1`, `w_2`, `w_3` | Overall mass fraction of a component (no phase) |
| `w_11` | Carrier in the carrier-rich phase |
| `w_21` | Solute in the carrier-rich phase |
| `w_23` | Solute in the solvent-rich phase |
| `w_33` | Solvent in the solvent-rich phase |

- `equilibrium_data` rows are `[100w_1, 100w_2, 100w_3]` — percentages, not fractions
- `tie_lines` rows are `[100w_23, 100w_21]` — solvent-rich first, then carrier-rich
- `correlation.py` uses **fractions**, e.g. the Hand correlation
  `ln(w23/w33) = a + b·ln(w21/w11)`
- The manuscript tables use the `$100w_1$` / `$100w_{23}$` LaTeX forms

**This is not Treybal's lettering.** The manuscript cites Treybal, who labels components
`A`/`B`/`C`: `A` = carrier, `B` = **solvent**, `C` = **solute**. Note the mismatch against
our `2` = solute. Never mix the two schemes in one figure or table.

---

## Coding Conventions

1. **ASCII-only Python source** — no Korean or non-ASCII in `.py` files
2. **Plot functions return `go.Figure`** — never call `.show()` inside
3. **Dataclasses with `__post_init__`** — see Patterns below
4. **Pure functions** — no global state in calculation modules
5. **Type hints required** on all public functions
6. **No dead code** — delete commented-out code, no `# TODO` in user-facing text
7. **No comments** unless the WHY is non-obvious (a constraint, a workaround, an invariant)

## Patterns

Only the things the code cannot tell you on its own.

### `__post_init__` establishes the object's invariants

`@dataclass` generates `__init__` for you, so `__post_init__` is the only hook into it.
`EquilibriumSystem` uses it for three jobs, in order:

```python
def __post_init__(self) -> None:
    x_raw = self.equil_data[:, 0] + 0.5 * self.equil_data[:, 1]   # derive
    idx = np.argsort(x_raw)                                       # normalize:
    self.x_equil = x_raw[idx]                                     #   YAML row order must not matter
    if np.any(np.diff(self.x_equil) < 0.05):
        raise ValueError(...)                                     # validate: reject degenerate input
    self.spline = self._build_spline(...)                         # derive: fit once
```

The point is not speed, it is that **after the constructor returns, all of these are
guaranteed** — sorted, no near-duplicates, curve fitted. Every downstream method can
assume them without checking, and invalid YAML fails at construction where the System tab
surfaces the message, instead of producing a plausible-looking wrong figure later.

There are four construction paths (`from_yaml()`, `main.py`, and two in `app.js`); a
separate `setup()` function would have to be remembered by all of them.

Not rebuilding the curve per call is a side effect, but a large one: fitting costs ~400×
a single evaluation, and one `S_min` construction evaluates the curve ~1500 times.

### Config is overridable because imports are live references

Experimental constants live at module level in `config.py`:

```python
V_R0: float = 10.78   # feed titration volume [mL]
```

A student overrides them in a notebook cell before calling `main()`:

```python
import experiments.experiment_06.config as cfg
cfg.V_E1 = 3.95
```

This works because a Python import is a live reference to the module object. **Do not
defeat it** by copying config values into local variables at import time.

### Return a named dataclass, not a bare tuple

```python
# Bad — the caller has to remember that position 0 is R0
pt_R0, pt_E1, pt_Rn, pt_En1, wpa, wbp = compute_stream_points(system)

# Good — self-describing in any notebook cell
sp = compute_stream_points(system)
fig = plot_lever_rule(sp.pt_R0, sp.pt_Rn, ...)
```

### Convert numpy scalars at the JS boundary

Wrap scalar returns in `float()` and arrays in `.tolist()`:

```python
return float(x_pp), float(self.eval(x_pp))
```

This is not style. These values cross **Pyodide → JavaScript**, where `np.float64` does
not survive cleanly; there are ~87 such casts across `exp06`. Rounding is a display
concern handled once in JS (`toFixed` / Plotly hover format), never here.

### Raise on solver failure; never fall back silently

```python
raise ValueError(
    "Conjugate-curve extension never re-enters the equilibrium "
    "curve's domain — check this system's tie-line data."
)
```

A silent fallback produces a plausible-looking but wrong figure, which is worse than a
crash. The message must say what to inspect — these errors surface directly in the browser
UI, where the reader is a student, not a developer.

### Plotting

`_layout()` and `_cart_layout()` in `plot_util.py` are **shared** — never modify them for
one chart; use `fig.update_layout()` inside that chart's `fig_*()` instead. Cartesian
charts use `scaleanchor="x"`, which ignores margin changes, so adjust `y_range` or text
positioning instead.

---

## Common Tasks

| Task | Where |
|------|-------|
| Add a YAML system | `public/systems/CLAUDE.md` (loads when working in that directory) |
| Add a new experiment | Ask first — the internal roadmap routes each experiment behind its own path and drops the dual-copy rule, so a second experiment added under today's layout would entrench what is being removed |
| System tab | `public/index.html` (`.sys-*`), `css/style.css`, `app.js` (`loadSystemTab`, `applySystem`, `validateForm`, `collectFormToYaml`) |
| Tab labels / UI copy | `public/index.html` (`.tab-btn`); messages at `setSysMsg` call sites |
| Guide content | `public/docs/guide.md` |
| Charts | `plot_util.py` `fig_*()` |
| Tie-line correlations, selectivity, Hand plait point | `correlation.py` |
| YAML structural rules | `validate_system.py` — single source of truth for both the System tab (via Pyodide) and the submission GitHub Action. Change it in one place only. |

**Web app notes.** `initPyodide()` fetches `.py` files from `/exp06/` into the Pyodide
filesystem; `calculate()` sets config globals and returns Plotly JSON;
`computeExplorer('sf'|'feed')` computes a single frame for real-time slider interaction;
system switching calls `Plotly.purge()` before `Plotly.newPlot()` to avoid stale state.
The sidebar auto-collapses on ternary tabs and auto-expands on extraction tabs.

Tab order (`‖` = `.tab-sep` divider, `✦` = interactive/editable marker in the label):
Guide | System ✦ ‖ Equilibrium | Conjugate Curve ‖ Hunter-Nash | Stages | Lever Rule |
S:F Explorer ✦ | Feed Explorer ✦ ‖ Contact

---

## Verification

Before claiming a change is done, run all three — these are exactly what CI runs:

```bash
ruff check .
python scripts/check_dual_copy.py
python -m pytest experiments/experiment_06/tests/ -v
```

Local dev: `python dev_server.py` → `http://localhost:8080`, then Ctrl+Shift+R to bypass
cache.

The test suite is the **regression baseline** and pins expected values to full precision
(e.g. `n_theory == pytest.approx(3.6118384065055205)`). If a change is *supposed* to move
a number, say so explicitly and update the expected value in the same commit — never
loosen `TOL` to make a test pass. A new computation module arrives with its own
`test_*.py`.

### Confirm before modifying

- `pyproject.toml` — check Pyodide compatibility before adding dependencies
- `vercel.json` — routing changes can break the deployed site
- `plot_util.py` `_layout()` / `_cart_layout()` — shared, never for a single chart

## Git Rules

- Always confirm with the user before committing
- Commit messages: short, conventional prefix (feat, fix, chore, docs), single line
- No Co-Authored-By
- Pushing to `main` auto-deploys to Vercel; this works for either collaborator's push
