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

Repository layout is documented in `README.md` — read it there rather than duplicating
it here. What the tree does *not* tell you is below, and in the Dual-copy Rule that follows.

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

Full procedure, format, and field rules: `public/systems/CLAUDE.md` (loads automatically
when working in that directory). `validate_system.py` is the enforcing authority.

## Web App Structure

Module roles and JS entry points are documented in `README.md` and in each module's
docstring. What is worth knowing before editing:

- `validate_system.py` is the **single source of truth** for YAML structural rules,
  shared by the System tab (via Pyodide) and the submission GitHub Action. Change it
  in one place only.
- `main.py` lives only in `experiments/experiment_06/` — it is not copied to
  `public/exp06/`, so it is exempt from the dual-copy rule.
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
- Pushing to `main` auto-deploys to Vercel; this works for either collaborator's push

## Adding a New Experiment

See `AGENTS.md` → "How to Add a New Experiment" for the steps, and `ROADMAP.md` Phase 7
for the target multi-experiment structure. Do not start one without reading Phase 7.4
first — the dual-copy rule is scheduled for removal and a new experiment should not
entrench it further.
