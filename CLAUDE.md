# CBPL-kit

SNU CBE Chemical Engineering Lab — experiment data analysis & visualization toolkit.
Experiment 06 = LLE Hunter-Nash simulator (main project).
Deployed at cbpl-kit.vercel.app (Pyodide — Python runs in browser, no server needed)

## Domain Primer

**What this tool is.** Liquid-liquid extraction (LLE) separates a **solute** out of a
**carrier** liquid by contacting it with a **solvent** that dissolves the solute but
barely mixes with the carrier. The **Hunter-Nash method** determines how many
equilibrium stages a counter-current extraction column needs, by geometric construction
on a **ternary phase diagram**. Undergraduates normally draw this by hand on graph
paper; this tool does the construction numerically so they can explore "what-if"
instead of redrawing.

Read `public/docs/guide.md` for the student-facing explanation. This section is the
minimum needed to not make physically wrong changes to the code.

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

Tests and linters cannot catch a physically absurd result. Check any numerical change
against these before believing it:

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
  depends on its own solute content. Do not substitute the pure-carrier or
  pure-solvent density; avoiding exactly that approximation is one of the paper's
  claims.

### Mistakes this codebase has already made

Worth knowing so they are not repeated — each cost real debugging time:

- **`S_min` scanned only one leg of the sweep.** `P(frac)` moves non-monotonically
  along the Rn-En1 line and can pass through infinity. An earlier version checked only
  the `t > 1` leg; it happened to work for every system tried at the time, then
  reported "no S_min" for `w_acoh_dipe`, whose tie lines sit on the negative leg. See
  the docstring of `find_smin_construction` in `lever_rule.py`.
- **The conjugate curve used to be a degree-4 polynomial fit**, which produced sharp
  kinks near the plait point. It is now branch-Hermite with a clamped-tangent
  extension. Any document or comment still mentioning `degree` or `polyfit` for the
  conjugate curve is stale.
- A plait point / conjugate change propagates to **N**, so it is never a local edit.

## Architecture

```
public/
  index.html              ← HTML structure only (tabs, sidebar, form, data panel)
  css/style.css           ← All CSS (teal-blue palette, IBM Plex Sans)
  js/app.js               ← All JS logic (Pyodide, Plotly, forms, Contact pane)
  exp06/                  ← Python modules (loaded into Pyodide FS)
  systems/                ← YAML system definition files
    index.json            ← Dropdown manifest (filename list)
    bp_pa_w_snu_cbe.yaml  ← Default system
  docs/guide.md           ← Guide tab content (rendered by marked.js)
  images/                 ← Static assets (whitelisted in .gitignore)
experiments/
  experiment_04/          ← Python modules only (no web integration)
  experiment_05/          ← Python modules only (no web integration)
  experiment_06/          ← Local dev copy of exp06 Python modules
    systems/              ← YAML definitions (must stay in sync with public/systems/)
    tests/                ← pytest suite (the only testpaths entry)
scripts/check_dual_copy.py  ← Verifies the dual-copy rule below
.github/workflows/        ← ci.yml, validate-system-submission.yml
dev_server.py             ← Local dev server (port 8080)
```

External JS/CSS dependencies in `index.html` are **version-pinned with SRI hashes**
(Pyodide, Plotly, marked, js-yaml, JSZip, SheetJS, KaTeX). Keep it that way — the
pinning is what makes an archived snapshot of this repo reproducible years later.

## Dual-copy Rule

`experiments/experiment_06/*.py` and `public/exp06/*.py` must always be identical.
After any edit: `cp public/exp06/plot_util.py experiments/experiment_06/plot_util.py` (or vice versa).
YAML files in `experiments/.../systems/` and `public/systems/` must also stay in sync.

Verify with `python scripts/check_dual_copy.py` (exits 0 + `OK`, or prints diffs).
CI runs it on every push and PR, so a forgotten copy fails the build.
Files that live only in `experiments/experiment_06/` (`main.py`, `__init__.py`) are exempt.

> **Status: temporary.** This rule exists only because there is no build step. Phase 7.4
> of ROADMAP.md replaces it with a real Python package, at which point the rule, the
> script, and this note all get deleted.
>
> Until then it is **fully binding** — the deployed site runs the `public/exp06/` copy,
> so a missed sync means users get stale code. Do not weaken it, and do not invest in
> new tooling built around it.

## Adding a New YAML System

1. Create YAML file in `public/systems/` (follow existing format)
2. Add the filename to `public/systems/index.json` (just the filename — the dropdown label is auto-built from `components` + `note`)
3. Copy to `experiments/experiment_06/systems/`
4. git push → Vercel auto-deploys

### YAML Format

```yaml
# System Configuration

components:
  carrier: { name: "n-Bromopropane", abbr: "BP" }   # (1)
  solute: { name: "Propionic Acid", abbr: "PA" }   # (2)
  solvent: { name: "Water", abbr: "W" }   # (3)

properties:
  rho_carrier: 1.354   # g/mL
  rho_solute: 0.993   # g/mL
  rho_solvent: 1.0   # g/mL
  mw_solute: 74.08   # g/mol

# Each row: [Carrier wt%, Solute wt%, Solvent wt%]
# (100w1, 100w2, 100w3; sorted by increasing carrier)
equilibrium_data:
  - [5.1, 9.49, 85.41]

# Each row: [Solute wt% in solvent-rich phase (3), Solute wt% in carrier-rich phase (1)]
# (100w23, 100w21; sorted by increasing solute)
tie_lines:
  - [6.253, 2.564]

# data source, temperature, etc. - free text
note: "Seoul National University"
```

- No top-level `name` — the dropdown label is auto-generated from `components` + `note`.
- equilibrium_data: [wCarrier%, wSolute%, wSolvent%] — must be sorted by increasing carrier%
- tie_lines: [wSolute% solvent-rich, wSolute% carrier-rich]
- note: free text (data source, temperature, etc.) — distinguishes same-component systems in the dropdown
- The `(1)`/`(2)`/`(3)` markers and the `100w23`/`100w21` shorthand above follow the
  numeric index convention — see [Numeric Index Convention](#numeric-index-convention-papers-yaml-comments-correlation-code).
- Structural rules are enforced by `validate_system.py`, not by this document.

## Python Modules (exp06)

| File | Role |
|------|------|
| `equilibrium.py` | Equilibrium data loading, spline fitting, `EquilibriumSystem` dataclass |
| `conjugate.py` | Conjugate curve (aux point calculation, PCHIP display, plait point search) |
| `hunter_nash.py` | Hunter-Nash stage calculation solver |
| `plot_util.py` | All Plotly figure builders |
| `lever_rule.py` | Lever rule calculations (M point, P point, E1') |
| `correlation.py` | Othmer-Tobias / Hand / Bachman tie-line correlations, selectivity, Hand-coordinate plait point |
| `ternary.py` | Cartesian ↔ ternary coordinate conversion |
| `config.py` | Physical constants (loaded from YAML properties) |
| `validate_system.py` | Structural validation of a system YAML dict — shared by the System tab (Pyodide) and the submission GitHub Action |
| `main.py` | CLI entry point (`experiments/` only, not copied to `public/exp06/`) |

## Web App Structure

- **index.html**: HTML structure only (tabs, sidebar, form, data panel)
- **css/style.css**: All styles (teal-blue palette, IBM Plex Sans)
- **js/app.js**: All JS logic
  - `PY_COMPUTE`: Python string executed via `pyodide.runPythonAsync()`
  - `renderSystemFigs()`: Auto-renders Equilibrium/Conjugate on system load
  - `applySystem()`: Parses YAML → updates properties/labels → rebuilds system
  - `validateForm()`: Validates empty values and sort order
  - `collectFormToYaml()`: Converts form inputs → YAML string
  - `renderContactPane()`: Builds the Contact tab from `TEAM_DATA` (top of app.js)
- **Tab order** (`‖` = `.tab-sep` divider, `✦` = interactive/editable marker in the label):
  Guide | System ✦ ‖ Equilibrium | Conjugate Curve ‖ Hunter-Nash | Stages | Lever Rule | S:F Explorer ✦ | Feed Explorer ✦ ‖ Contact
- **Sidebar**: Auto-collapses on ternary tabs, auto-expands on extraction tabs

## Plotly Chart Modification Rules

- `_layout()` and `_cart_layout()` in plot_util.py are **shared functions**. Never modify them for a single chart.
- For chart-specific layout changes, use `fig.update_layout()` inside the specific `fig_*()` function.
- Cartesian charts use `scaleanchor="x"` which ignores margin changes — adjust y_range or text positioning instead.

## Component Naming Convention

| Role | Index | Code key | Internal variables (do not rename) |
|------|-------|---------|---------------------|
| Carrier | **1** | `"carrier"` | `wbp`, `RHO_BP` |
| Solute | **2** | `"solute"` | `wpa`, `RHO_PA`, `MW_PA` |
| Solvent | **3** | `"solvent"` | `ww`, `RHO_W` |

**Never rename** internal Python variables: `wpa`, `wbp`, `ww`, `RHO_PA`, `RHO_BP`, `RHO_W`.
Use `"carrier"` key and `labels.abbr` only in YAML and UI.

### Numeric Index Convention (papers, YAML comments, correlation code)

The manuscript, the YAML comments, and `correlation.py` all share one numbering scheme.
Use it consistently in any new code, comment, figure label, or paper text.

**Components** — 1 = carrier, 2 = solute, 3 = solvent (the order they appear in
`components:` and in every `equilibrium_data` row).

**Phases reuse the same digits**, named after the component that dominates them:

| Phase | Index | Extraction name |
|-------|-------|-----------------|
| Carrier-rich | **1** | Raffinate |
| Solvent-rich | **3** | Extract |

(There is no phase 2 — the solute is the distributed species, not a phase.)

**Two subscripts = `w_ij` = mass fraction of component `i` in phase `j`.**

| Symbol | Meaning |
|--------|---------|
| `w_1`, `w_2`, `w_3` | Overall mass fraction of a component (single subscript, no phase) |
| `w_11` | Carrier in the carrier-rich phase |
| `w_21` | Solute in the carrier-rich phase |
| `w_23` | Solute in the solvent-rich phase |
| `w_33` | Solvent in the solvent-rich phase |

Where each form shows up:

- `equilibrium_data` rows are `[100w_1, 100w_2, 100w_3]` — percentages, not fractions
- `tie_lines` rows are `[100w_23, 100w_21]` — solvent-rich first, then carrier-rich
- `correlation.py` uses **fractions** (`w11`, `w21`, `w23`, `w33`), e.g. the Hand
  correlation `ln(w23/w33) = a + b·ln(w21/w11)`
- The manuscript tables use the `$100w_1$` / `$100w_{23}$` LaTeX forms

**Watch out — this is not Treybal's lettering.** The manuscript cites Treybal, who
labels components `A`/`B`/`C`. Do not mix the two systems in one figure or table:

| This project | Treybal |
|--------------|---------|
| 1 = carrier | A = carrier (diluent) |
| 2 = solute | C = solute |
| 3 = solvent | B = solvent |

Note the mismatch: Treybal's `B` is the **solvent**, but our `2` is the **solute**.

## Development Workflow

```bash
python dev_server.py                    # localhost:8080
# Ctrl+Shift+R in browser (hard refresh, bypass cache)

python -m pytest experiments/experiment_06/tests/ -v   # tests (pyproject testpaths)
ruff check .                                           # lint
python scripts/check_dual_copy.py                      # dual-copy sync
```

CI (`.github/workflows/ci.yml`) runs those three on every push to `main` and every PR.

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
