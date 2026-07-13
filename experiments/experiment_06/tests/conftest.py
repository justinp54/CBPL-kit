"""Shared pytest fixtures for exp06 module tests.

The exp06 modules use flat imports (`import config`, `from ternary import ...`)
because they are loaded into a flat Pyodide filesystem in the browser, not as a
package. So the tests put experiments/experiment_06 on sys.path (done in
_helpers) and import the modules the same flat way.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from _helpers import DEFAULT_SYSTEM, SYSTEMS_DIR, system_files


@pytest.fixture(scope="session")
def systems_dir() -> Path:
    return SYSTEMS_DIR


@pytest.fixture(scope="session")
def system_paths() -> list[Path]:
    files = system_files()
    assert files, f"No system YAML files found in {SYSTEMS_DIR}"
    return files


@pytest.fixture(scope="session")
def loaded_systems(system_paths) -> dict[str, dict]:
    """All system YAMLs parsed into dicts, keyed by filename stem."""
    return {p.stem: yaml.safe_load(p.read_text()) for p in system_paths}


@pytest.fixture(scope="session")
def default_system_dict() -> dict:
    return yaml.safe_load((SYSTEMS_DIR / DEFAULT_SYSTEM).read_text())
