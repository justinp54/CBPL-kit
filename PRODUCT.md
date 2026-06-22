# Product

## Register

product

## Users

Chemical and Biological Engineering students at Seoul National University, running the CBPL (Chemical & Biological Process Lab) course. They arrive with lab data (titration volumes, flow rates) and need to compute Hunter-Nash stage counts and visualize ternary equilibrium diagrams. Their context is post-lab analysis: they've already collected samples and need to turn raw numbers into interpreted results under time pressure. Most are not software engineers — the tool must be self-evident from the interface.

## Product Purpose

CBPL-kit replaces ad-hoc Excel/MATLAB workflows with a browser-based LLE Hunter-Nash simulator that runs entirely client-side (Pyodide). Students enter titration data, and all equilibrium curves, conjugate curves, tie lines, lever-rule balances, and stage-stepping diagrams update instantly. Success means students spend their time understanding thermodynamics, not debugging code.

## Brand Personality

Expert, precise, confident. The tool speaks the language of chemical engineering — it doesn't simplify terminology or add unnecessary decoration. It earns trust through accuracy, fast feedback, and transparent calculation. Three words: **precise, authoritative, efficient**.

## Anti-references

- **Generic SaaS dashboards**: No KPI hero cards, growth metrics, gradient accents, or startup-product aesthetics. This is an engineering instrument, not a business analytics platform.
- **Overly playful / gamified UIs**: No achievement badges, confetti, cartoon illustrations, or "fun" color palettes. The subject matter is serious; the interface should reflect that.
- **Desmos's simplicity taken too far**: Desmos is a reference for clean interaction design, but CBPL-kit needs to show more data simultaneously (ternary plots, stage tables, multiple tabs). Don't strip information density in pursuit of minimalism.

## Design Principles

1. **Data first, chrome second** — Every pixel of UI should serve the calculation or its interpretation. Decorative elements earn their space or get cut.
2. **Show the work** — Engineering requires traceability. Stage breakdowns, stream compositions, and intermediate results are always accessible, not hidden behind progressive disclosure.
3. **Instrument confidence** — The interface should feel like a calibrated instrument: predictable inputs, immediate feedback, no ambiguity about what a number means or where it came from.
4. **Zero onboarding for the prepared** — A student who understands Hunter-Nash should be able to use this tool without reading instructions. Labels, layout, and flow should map directly to the method.

## Accessibility & Inclusion

No formal WCAG target. Practical baseline: readable text contrast, functional keyboard navigation for sidebar inputs, and legible Plotly chart labels. Color-blind-safe Plotly palettes are a plus but not a hard requirement.
