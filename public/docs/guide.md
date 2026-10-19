## The reference experiment

This tool was initially built for the liquid-liquid extraction experiment in the **Chemical and Biological Process Laboratory** at **Seoul National University**.

Water is used to extract propionic acid out of n-bromopropane in a counter-current packed column. Once the column reaches steady state you sample the feed, extract, and raffinate, and titrate each against NaOH to find how much acid it carries. From those three numbers you determine how many equilibrium stages the separation needs, by the **Hunter-Nash** construction on a ternary phase diagram.

📄 **[Laboratory handout](/docs/laboratory_handout.pdf)** — apparatus, procedure, and safety in full

📄 **[Technical documentation](/docs/technical_documentation.pdf)** — the numerical methods behind every figure, for anyone who want to reuse

## What this tool does

There are two workflows, and you can stop after the first:

| Workflow | Input | Output |
|---|---|---|
| **I. Ternary Phase Equilibrium** | equilibrium + tie-line data for a system | binodal curve, full tie-line compositions, conjugate curve, plait point, selectivity |
| **II. LLE Hunter-Nash Analysis** | …plus your own run: each stream's solute content (titration, wt% or M) and flow rates | stage count *N*, lever-rule check, S/F and feed exploration |

## How to cite

> **Software**<br>
> Park, J., Lee, S., & Lee, Y.-W. (2026). *CBPL-kit: a web-based interactive toolkit for ternary phase equilibrium and liquid-liquid extraction*. Zenodo. [https://doi.org/10.5281/zenodo.21862135](https://doi.org/10.5281/zenodo.21862135)
>
> **Paper**<br>
> Coming soon

## 1. Choose a system

In the **System ✦** tab, you can select a bundled system from the dropdown, or enter your own measured data in the form — then **Apply System**.
The toolkit works for a **Type I** system: only carrier and solvent are partially miscible.

### Notation

The three components are numbered by role:

| | Role | Component (reference experiment) |
|---|---|---|
| **1** | carrier | n-bromopropane |
| **2** | solute | propionic acid |
| **3** | solvent | water |

Phase **1** is the carrier-rich phase, the raffinate; phase **3** is the solvent-rich phase, the extract.

Compositions are expressed in mass fraction $w_{ij}$, where the first index refers to the component and the second to the phase. For example:

$$w_{21} = \text{solute in the raffinate}, \qquad w_{23} = \text{solute in the extract}$$

- One subscript on its own is the overall mass fraction: $w_2$ is solute in the mixture as a whole
- Tables and figures use $100w_{ij}$, the same number written as a percentage

## 2. Workflow I
### Equilibrium

Ternary diagram: **binodal curve** fitted to the data, with every measured **tie-line**.

Side panel: the **distribution coefficients**, **selectivity**, and **Othmer-Tobias / Hand / Bachman correlations**.

### Conjugate Curve

Two constructions are available:

- **Diagonal** draws auxiliary lines parallel to two sides of the triangle from each tie-line end
- **Horizontal** replaces one of them with a horizontal line, picking whichever side keeps the auxiliary points inside the triangle

Each gives its own plait-point estimate (◆), and **Treybal's Hand-coordinate** method gives a third.

## 3. Workflow II

Enter your run in the sidebar, then **Calculate**.

### Sidebar inputs

Select **how the solute concentration was determined** at the top of the sidebar. The fields below change to match, and **Calculate** stays disabled until you choose.

| Method | What you enter, per stream |
|--------|----------------------------|
| **Titration volume (mL)** | the titre, with its dilution factor |
| **Mass fraction (wt%)** | the solute mass fraction |
| **Molar concentration (M)** | the solute molarity |

**Titration**:

$$C_{\mathrm{solute}} = \dfrac{C_{\mathrm{NaOH}} \cdot V_{\mathrm{NaOH}} \cdot f}{V_{\mathrm{aliquot}}}$$

The toolkit assumes NaOH titration (1:1 acid–base neutralisation).

- **Titration volume / molar concentration** is converted to a full composition using a volume-additive mixture density
- **mass fraction** fixes the stream point on the diagram directly

The annotation for each stream is shown on the table below, and the same letters are used in the diagram.

| Stream | On the diagram |
|---------|----------------|
| Feed | R<sub>0</sub> |
| Extract | E<sub>1</sub> |
| Raffinate | R<sub>N</sub> |
| Solvent | E<sub>N+1</sub> |

### Hunter-Nash

The full stage construction. **P** is the operating point — intersection of R<sub>0</sub>–E<sub>1</sub> and R<sub>N</sub>–E<sub>N+1</sub>; every pair of passing streams lies on a line through it. Stepping alternates between operating lines through P and interpolated tie lines.

- **N**, in the tab badge, is the theoretical stage count
- Side panel: stream compositions, mass flow rates, stage-by-stage compositions

### Stages

The tie line interpolated for each stage from the conjugate curve.

### Lever Rule

| Point | Meaning |
|-------|---------|
| **M** | Mixture point, from the construction: where E<sub>1</sub>–R<sub>N</sub> crosses E<sub>N+1</sub>–R<sub>0</sub> |
| **M′** | The same point from a mass balance |
| **E<sub>1</sub>′** | Predicted first extract — R<sub>N</sub>–M′ extended to the extract branch |

M′ is the mass-weighted average of the two inlet streams:

$$w_{M'} = \dfrac{\dot m_F\,w_F + \dot m_S\,w_S}{\dot m_F + \dot m_S}$$

where $\dot m_F$, $\dot m_S$ are the feed and solvent mass flow rates and $w_F$, $w_S$ their compositions.

### S:F Explorer ✦

Vary the solvent-to-feed ratio for the same feed and target raffinate. The operable span is computed in advance and the slider restricted to it; infeasible ranges are shaded.

- The trend plot shows N rising steeply toward (S/F)<sub>min</sub>

### Feed Explorer ✦

Vary the feed composition for the same solvent-to-feed ratio and target raffinate. The operable span is computed in advance and the slider restricted to it.

The trend is **not monotonic** — worth working out why. A richer feed must transfer more solute (raising N) but carries less carrier at fixed mass flow (lowering N); the crossover is the maximum in the curve.

## Export

The **Export** button saves every figure, the numerical results, and the system YAML as one ZIP for your report.

## Tips

- **Enter** recalculates; scroll to zoom, drag to pan
- Click legend entries to hide traces; hover a point for its composition
- Found a problem, or have a system you would like included? The **Contact** tab has the details
