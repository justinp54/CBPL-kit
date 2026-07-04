"""Validates the YAML pasted into a system-submission issue form and writes
a GitHub comment body + the pass/fail outcome, for the
validate-system-submission workflow.

Reads the submitted YAML from the SYSTEM_YAML env var (populated by the
stefanbuck/github-issue-parser step). Writes comment_body.md and appends
`ok=true`/`ok=false` to $GITHUB_OUTPUT.
"""
import os
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'experiments', 'experiment_06'))
import validate_system

yaml_text = os.environ.get('SYSTEM_YAML', '')
ok = True
problems = []

try:
    data = yaml.safe_load(yaml_text)
except yaml.YAMLError as e:
    ok = False
    problems.append(f'YAML parse error: {e}')
else:
    errors = validate_system.validate(data)
    if errors:
        ok = False
        problems.extend(e[5:] if e.startswith('SORT:') else e for e in errors)

if ok:
    body = (
        '### ✅ Validation passed\n\n'
        'This system YAML looks structurally valid — carrier%/tie-line '
        'ordering, sum-to-100 checks, and required fields all check out.'
    )
else:
    body = (
        '### ❌ Validation failed\n\n'
        + '\n'.join(f'- {p}' for p in problems)
        + '\n\nPlease fix and update the "System YAML" field above — this check reruns automatically.'
    )

with open('comment_body.md', 'w', encoding='utf-8') as fh:
    fh.write(body)

with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as fh:
    fh.write(f"ok={'true' if ok else 'false'}\n")
