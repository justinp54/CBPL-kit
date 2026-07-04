"""Structural validation for a system YAML dict (post yaml.safe_load / jsyaml.load).

Single source of truth for the checks the browser (System tab, via Pyodide)
and the GitHub Action (system-submission issue template) both need — so a
submitted system gets the same verdict regardless of which path it came in
through.

Returns a list of human-readable problem strings; empty list means valid.
A "SORT:" prefix marks the one error the UI offers a one-click fix for
(equilibrium_data auto-sort) — callers that don't have that button (e.g. CI)
can just strip the prefix before displaying.
"""

_REQUIRED_KEYS = ('components', 'properties', 'equilibrium_data', 'tie_lines')
_REQUIRED_PROPS = ('rho_carrier', 'rho_solute', 'rho_solvent', 'mw_solute')
_SUM_TOL = 0.5


def validate(sys_data: dict) -> list[str]:
    if not isinstance(sys_data, dict):
        return ['System must be a YAML mapping (components/properties/equilibrium_data/tie_lines).']

    errors = []

    for key in _REQUIRED_KEYS:
        if key not in sys_data or sys_data[key] is None:
            errors.append(f'Missing required field: {key}.')
    if errors:
        return errors

    props = sys_data['properties'] or {}
    for key in _REQUIRED_PROPS:
        if key not in props or props[key] in (None, ''):
            errors.append(f'properties must include {key}.')
        elif _not_number(props[key]):
            errors.append(f'properties.{key} must be a number (got {props[key]!r}).')
    if errors:
        return errors

    eq_rows = sys_data['equilibrium_data']
    if not isinstance(eq_rows, list) or len(eq_rows) < 3:
        errors.append('equilibrium_data must have at least 3 rows.')
        return errors

    for i, row in enumerate(eq_rows):
        if not isinstance(row, (list, tuple)) or len(row) != 3 or any(_not_number(v) for v in row):
            errors.append(f'equilibrium_data row {i + 1} must have 3 numeric values: [Carrier, Solute, Solvent] wt%.')
            continue
        total = sum(float(v) for v in row)
        if abs(total - 100) > _SUM_TOL:
            errors.append(f'equilibrium_data row {i + 1} sums to {total:.2f}%, not 100%.')
    if errors:
        return errors

    for i in range(1, len(eq_rows)):
        if float(eq_rows[i][0]) < float(eq_rows[i - 1][0]):
            errors.append('SORT:Equilibrium data is not sorted by increasing carrier%. Click "Sort" to fix.')
            break

    tie_rows = sys_data['tie_lines']
    if not isinstance(tie_rows, list) or len(tie_rows) < 2:
        errors.append('tie_lines must have at least 2 rows (a single tie line can\'t define a conjugate curve).')
        return errors

    for i, row in enumerate(tie_rows):
        if not isinstance(row, (list, tuple)) or len(row) != 2 or any(_not_number(v) for v in row):
            errors.append(f'tie_lines row {i + 1} must have 2 numeric values: [Solute% solvent-rich, Solute% carrier-rich].')
    if errors:
        return errors

    # Both phases' solute fraction should converge toward the plait point
    # together — a tie line where one column advances while the other falls
    # back means the rows are out of order (or the data itself is bad), and
    # produces crossed/tangled tie lines on the ternary diagram.
    for i in range(1, len(tie_rows)):
        prev, cur = tie_rows[i - 1], tie_rows[i]
        if float(cur[0]) < float(prev[0]) or float(cur[1]) < float(prev[1]):
            errors.append(
                f'tie_lines rows {i} and {i + 1} are not both increasing — tie lines must be '
                'sorted so both phase compositions move toward the plait point together.'
            )
            break

    return errors


def _not_number(v) -> bool:
    try:
        float(v)
    except (TypeError, ValueError):
        return True
    return False
