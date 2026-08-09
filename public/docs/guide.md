## The experiment

This tool was initially built for the liquid-liquid extraction experiment in the Chemical and Biological Process Laboratory at Seoul National University.

Water is used to extract propionic acid out of n-bromopropane in a counter-current packed column. Once the column reaches steady state you sample the feed, extract, and raffinate, and titrate each against NaOH to find how much acid it carries. From those three numbers you determine how many equilibrium stages the separation needs, by the **Hunter-Nash** construction on a ternary phase diagram.

📄 **Laboratory handout** *(coming soon)* — apparatus, procedure, and safety in full
<!-- Once public/docs/lab-handout.pdf exists, make the line above:
     📄 **[Laboratory handout](/docs/lab-handout.pdf)** — apparatus, procedure, and safety in full -->

## What this tool does

It runs the construction numerically, so changing one input and seeing the answer costs a click instead of a redraw. There are two workflows, and you can stop after the first:

| | You supply | You get |
|---|---|---|
| **Phase equilibrium** | equilibrium + tie-line data for a system | binodal curve, full tie-line compositions, conjugate curve, plait point, selectivity |
| **Hunter-Nash** | …plus your own run: titration volumes and flow rates | stage count *N*, lever-rule check, S/F and feed exploration |

## How to cite

Used CBPL-kit for a report or a paper? Please cite the archived release:

> Park, J., Lee, S., & Lee, Y.-W. (2026). *CBPL-kit: a web-based interactive toolkit for ternary phase equilibrium and liquid-liquid extraction*. Zenodo. [https://doi.org/10.5281/zenodo.21862135](https://doi.org/10.5281/zenodo.21862135)

The DOI always points at the most recent release, so it stays correct as the toolkit is updated. The **Cite this repository** button on [GitHub](https://github.com/justinp54/CBPL-kit) gives the same thing in BibTeX and other formats.

## 1. Choose a system

Everything below starts here. In the **System ✦** tab, pick a bundled system from the dropdown, or enter your own measured data in the form — then **Apply System**.
The method assumes a **Type I** system: only carrier and solvent are partially miscible.

## 2. Phase equilibrium

Both tabs are drawn as soon as a system loads.

### Equilibrium

Binodal curve fitted to the data, with every measured tie line.

Side panel: the **distribution coefficients** and **selectivity**,

$$D_1 = \dfrac{w_{13}}{w_{11}},\quad D_2 = \dfrac{w_{23}}{w_{21}},\quad S = \dfrac{D_2}{D_1}$$

plus **Othmer-Tobias / Hand / Bachman consistency fits**.

- Selectivity is highest at low solute fraction and falls to 1 at the plait point

### Conjugate Curve

Lets a tie line be interpolated anywhere, not only where one was measured. Two constructions are available:

- **Diagonal** draws auxiliary lines parallel to two sides of the triangle from each tie-line end
- **Horizontal** replaces one of them with a horizontal line, picking whichever side keeps the auxiliary points inside the triangle

Each gives its own plait-point estimate (◆), and **Treybal's Hand-coordinate** method gives a third.

- How far the three disagree tells you how well your data pins the plait point
- The curve **ends** at the plait point — beyond it the two phases are one

## 3. Hunter-Nash analysis

Enter your run in the sidebar, then **Calculate** (or press **Enter**). One calculation feeds every tab below.

### Sidebar inputs

$$C_{\mathrm{solute}} = \dfrac{C_{\mathrm{NaOH}} \cdot V_{\mathrm{NaOH}} \cdot f}{V_{\mathrm{aliquot}}}$$

Every term is a field you set, so enter what you actually did. The only thing assumed is 1:1 acid–base neutralisation.

- **C<sub>NaOH</sub>** and **V<sub>aliquot</sub>**, at the top — your titrant concentration and the aliquot you titrated
- Then for each stream, its **dilution factor `f`** and the **titration volume**. Enter the volume exactly as read from the burette; `f` is applied for you, and undiluted means `f` = 1

The annotation for each stream is shown on the table below, and the same letters are used in the diagram.

| Sidebar | On the diagram |
|---------|----------------|
| Feed | R<sub>0</sub> |
| Extract | E<sub>1</sub> |
| Raffinate | R<sub>N</sub> |

Turning a titre into a composition needs the sample's density. The tool solves for it under **volume additivity** rather than assuming the pure carrier or pure solvent, so its compositions differ slightly from a hand calculation.

Flow rates are the solvent (E<sub>N+1</sub>) and feed (R<sub>0</sub>) volumetric flows in mL/min. The construction is on a **mass** basis, so an S/F ratio by volume is a different number by mass.

### Hunter-Nash

The full stage construction. **P** is the operating point — intersection of R<sub>0</sub>–E<sub>1</sub> and R<sub>N</sub>–E<sub>N+1</sub>; every pair of passing streams lies on a line through it. Stepping alternates between operating lines through P and interpolated tie lines.

- **N**, in the tab badge, is the theoretical stage count
- Side panel: stream compositions, mass flow rates, stage-by-stage compositions

### Stages

The tie line interpolated for each stage, with its auxiliary lines back to the conjugate curve.

### Lever Rule

| Point | Meaning |
|-------|---------|
| **R<sub>0</sub>** | Feed — on the carrier–solute edge, no solvent |
| **E<sub>N+1</sub>** | Solvent inlet — the pure-solvent vertex |
| **M** | Mixture point, from the construction: where E<sub>1</sub>–R<sub>N</sub> crosses E<sub>N+1</sub>–R<sub>0</sub> |
| **M′** | The same point from a mass balance on your flow rates |
| **E<sub>1</sub>′** | Predicted first extract — R<sub>N</sub>–M′ extended to the extract branch |

M′ is the mass-weighted average of the two inlet streams:

$$w_{M'} = \dfrac{\dot m_F\,w_F + \dot m_S\,w_S}{\dot m_F + \dot m_S}$$

where $\dot m_F$, $\dot m_S$ are the feed and solvent mass flow rates and $w_F$, $w_S$ their compositions.

That gives you two cross-checks, and they matter because **the two routes rest on different measurements** — M on the compositions from titration, M′ on the flow rates you read off the rotameters.

### S:F Explorer ✦

Vary the solvent-to-feed ratio for the same feed and target raffinate. The operable span is computed in advance and the slider restricted to it; infeasible ranges are shaded.

- The trend plot shows N rising steeply toward (S/F)<sub>min</sub> — the solvent-versus-stages trade-off

### Feed Explorer ✦

Same, for the feed solute fraction.

The trend is **not monotonic** — worth working out why. A richer feed must transfer more solute (raising N) but carries less carrier at fixed mass flow (lowering N); the crossover is the maximum in the curve.

## Export

The **Export** button saves every figure, the numerical results, and the system YAML as one ZIP for your report. Available after a calculation.

## Tips

- **Enter** recalculates; scroll to zoom, drag to pan
- Click legend entries to hide traces; hover a point for its composition
- Found a problem, or have a system you would like included? The **Contact** tab has the details
