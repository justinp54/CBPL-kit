"""Test-collection helpers shared across test modules.

Kept dependency-free (no exp06 imports) so it can be imported at parametrize
time. pytest's default "prepend" import mode puts the tests/ directory on
sys.path, making this importable as a top-level module from the test files.
"""
from __future__ import annotations

import sys
from pathlib import Path

EXP06_DIR = Path(__file__).resolve().parent.parent
SYSTEMS_DIR = EXP06_DIR / "systems"

DEFAULT_SYSTEM = "bp_pa_w_snu_cbe.yaml"

# Ensure the exp06 modules (flat imports) are importable from the tests.
if str(EXP06_DIR) not in sys.path:
    sys.path.insert(0, str(EXP06_DIR))


def system_files() -> list[Path]:
    return sorted(SYSTEMS_DIR.glob("*.yaml"))


# IDs like "bp_pa_w_snu_cbe" so a failing parametrized case names its system.
SYSTEM_IDS = [p.stem for p in system_files()]
