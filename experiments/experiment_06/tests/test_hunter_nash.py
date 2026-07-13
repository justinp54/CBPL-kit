"""Regression test for the Hunter-Nash solver on the default system.

These are GOLDEN VALUES pinned to the CURRENT behavior of the code as of this
commit — a regression tripwire, NOT independently verified ground truth. If a
deliberate algorithm change moves them, update the constants here; if an
unrelated change moves them, that is the regression this test exists to catch.

The wiring (titration -> stream points -> M/P -> solve) mirrors
main.compute_stream_points / main.main exactly, so the numbers match what the
web app's Hunter-Nash tab computes for the default bp_pa_w_snu_cbe system with
config.py's default titration volumes.
"""
from __future__ import annotations

import pytest

from conjugate import ConjugateCurve
from equilibrium import EquilibriumSystem
from hunter_nash import HunterNashSolver
from lever_rule import find_M_and_P
from main import compute_stream_points

TOL = 1e-4


@pytest.fixture(scope="module")
def solved():
    system = EquilibriumSystem()          # default system from config.py
    conjugate = ConjugateCurve(system)
    sp = compute_stream_points(system)
    _, pt_P = find_M_and_P(sp.pt_E1, sp.pt_Rn, sp.pt_En1, sp.pt_R0)
    solver = HunterNashSolver(system, conjugate, pt_P, sp.pt_E1, sp.pt_Rn)
    steps, n_theory = solver.solve()
    return solver, steps, n_theory


def test_status_converged(solved):
    solver, _, _ = solved
    assert solver.status == "converged"


def test_stage_count(solved):
    _, steps, n_theory = solved
    assert len(steps) == 4
    assert n_theory == pytest.approx(3.6118384065055205, abs=TOL)


def test_stage1_extract_composition(solved):
    _, steps, _ = solved
    wpa, wbp, ww = steps[0].comp_E
    assert wpa == pytest.approx(13.92850058295453, abs=TOL)
    assert wbp == pytest.approx(5.291787423219221, abs=TOL)
    assert ww == pytest.approx(80.77971199382625, abs=TOL)


def test_stage1_raffinate_composition(solved):
    _, steps, _ = solved
    wpa, wbp, ww = steps[0].comp_R
    assert wpa == pytest.approx(7.857165692789956, abs=TOL)
    assert wbp == pytest.approx(85.50510891688036, abs=TOL)
    assert ww == pytest.approx(6.637725390329678, abs=TOL)


def test_final_stage_raffinate_solute(solved):
    _, steps, _ = solved
    # Last stage raffinate PA wt% (deepest extraction reached)
    assert steps[-1].comp_R[0] == pytest.approx(0.060256057582777724, abs=TOL)


def test_operating_point_P(solved):
    """P is derived, but pin it too — it feeds every stage's R->E line."""
    system = EquilibriumSystem()
    sp = compute_stream_points(system)
    _, pt_P = find_M_and_P(sp.pt_E1, sp.pt_Rn, sp.pt_En1, sp.pt_R0)
    assert pt_P[0] == pytest.approx(-39.97135520099838, abs=1e-3)
    assert pt_P[1] == pytest.approx(-0.06765956258672941, abs=1e-3)
