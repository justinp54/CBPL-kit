# System YAML Definitions

Each file here defines one ternary system for the LLE simulator. The dropdown in the
System tab is built from `index.json`.

Component/phase numbering (`(1)`/`(2)`/`(3)`, `100w23`, `100w21`) follows the project's
numeric index convention — see "Numeric Index Convention" in the root `CLAUDE.md`.

## Adding a New System

1. Create the YAML file here in `public/systems/` (follow the format below)
2. Add the filename to `public/systems/index.json` — just the filename; the dropdown
   label is auto-built from `components` + `note`
3. Copy the file to `experiments/experiment_06/systems/` (dual-copy rule)
4. `python scripts/check_dual_copy.py` must print `OK`
5. git push → Vercel auto-deploys

## Format

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

## Field rules

- No top-level `name` — the dropdown label is auto-generated from `components` + `note`.
- `equilibrium_data`: `[wCarrier%, wSolute%, wSolvent%]` — must be sorted by increasing
  carrier%.
- `tie_lines`: `[wSolute% solvent-rich, wSolute% carrier-rich]`.
- `note`: free text (data source, temperature, etc.) — this is what distinguishes two
  systems with the same components in the dropdown.
- **Structural rules are enforced by `validate_system.py`, not by this document.** It is
  the single source of truth, shared by the System tab (via Pyodide) and the
  system-submission GitHub Action. If a rule here disagrees with the code, the code wins.

## Data provenance

Most bundled systems are transcribed from published literature, not measured here. When
adding one, record the full source — author, year, edition, table number — so the value
can be traced back. `note` is a dropdown label and is too short for this; a proper
citation belongs in the source list tracked for the paper.
