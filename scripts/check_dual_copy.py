#!/usr/bin/env python3
"""Verify dual-copy sync between public/exp06/ and experiments/experiment_06/.

Checks:
  1. Every *.py file in public/exp06/ has an identical copy in experiments/experiment_06/.
     Files that exist only in experiments/ (main.py, __init__.py, etc.) are ignored.
     A file present in public/ but missing from experiments/ is a failure.
  2. Every YAML system file listed in public/systems/index.json has an identical copy
     in experiments/experiment_06/systems/.  index.json itself lives only in public/ —
     that is expected and not checked.

Exits 0 with "OK" when all pairs match; exits 1 and prints unified diffs otherwise.
Uses only the Python standard library (difflib, json, pathlib).
"""

import json
import sys
from difflib import unified_diff
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_DIFF_LINES = 30  # cap diff output per file to keep terminal readable


def _diff_files(a: Path, b: Path, label_a: str, label_b: str) -> str | None:
    """Return a unified diff string if a and b differ, else None."""
    a_lines = a.read_text(encoding="utf-8").splitlines(keepends=True)
    b_lines = b.read_text(encoding="utf-8").splitlines(keepends=True)
    if a_lines == b_lines:
        return None
    diff_lines = list(unified_diff(a_lines, b_lines, fromfile=label_a, tofile=label_b, n=3))
    if len(diff_lines) > MAX_DIFF_LINES:
        diff_lines = diff_lines[:MAX_DIFF_LINES] + [f"... ({len(diff_lines) - MAX_DIFF_LINES} more lines)\n"]
    return "".join(diff_lines)


def check_py_files() -> list[str]:
    """Compare public/exp06/*.py vs experiments/experiment_06/*.py."""
    public_dir = REPO_ROOT / "public" / "exp06"
    exp_dir = REPO_ROOT / "experiments" / "experiment_06"
    failures: list[str] = []

    for pub_file in sorted(public_dir.glob("*.py")):
        exp_file = exp_dir / pub_file.name
        if not exp_file.exists():
            failures.append(f"MISSING in experiments/experiment_06/: {pub_file.name}\n")
            continue
        diff = _diff_files(
            pub_file,
            exp_file,
            f"public/exp06/{pub_file.name}",
            f"experiments/experiment_06/{pub_file.name}",
        )
        if diff:
            failures.append(diff)

    return failures


def check_yaml_files() -> list[str]:
    """Compare YAML system files listed in public/systems/index.json."""
    public_systems = REPO_ROOT / "public" / "systems"
    exp_systems = REPO_ROOT / "experiments" / "experiment_06" / "systems"
    index_path = public_systems / "index.json"
    filenames: list[str] = json.loads(index_path.read_text(encoding="utf-8"))

    failures: list[str] = []
    for fname in filenames:
        pub_file = public_systems / fname
        exp_file = exp_systems / fname
        if not exp_file.exists():
            failures.append(f"MISSING in experiments/experiment_06/systems/: {fname}\n")
            continue
        diff = _diff_files(
            pub_file,
            exp_file,
            f"public/systems/{fname}",
            f"experiments/experiment_06/systems/{fname}",
        )
        if diff:
            failures.append(diff)

    return failures


def main() -> None:
    py_failures = check_py_files()
    yaml_failures = check_yaml_files()
    all_failures = py_failures + yaml_failures

    if all_failures:
        for block in all_failures:
            print(block, end="" if block.endswith("\n") else "\n")
        sys.exit(1)

    print("OK: all dual-copy pairs are identical")


if __name__ == "__main__":
    main()
