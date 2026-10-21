"""GPRESFIX: residual-side photon strength of the residual itself for every non-neutron projectile.

TALYS: fstrength.f90:1 (fstrength(Zcomp, Ncomp, ...), S(Zcomp, Ncomp, k0) at :192), densprepare.f90:310, tgamma.f90:64
"""
import os
import subprocess
import sys

_PROBE = ("from physics.hf.projectile import residual_nucleus, gpres_active, pseudo_target, compound_of; "
          "print(residual_nucleus(41, 93), gpres_active(), compound_of(*pseudo_target(41, 93)))")


def _run(**env):
    e = {k: v for k, v in os.environ.items() if not k.startswith("INCOGNITA_")}
    e.update(env)
    out = subprocess.run([sys.executable, "-c", _PROBE], env=e, capture_output=True, text=True,
                         cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    assert out.returncode == 0, out.stderr[-2000:]
    return out.stdout.strip()


def test_neutron_keeps_the_pseudo_target_form():
    assert _run() == "None True (41, 93)"
    assert _run(INCOGNITA_GPRESFIX="0") == "None False (41, 93)"


def test_charged_projectiles_use_the_residual_itself_by_default():
    for p in ("p", "a"):
        assert _run(INCOGNITA_CPINC=p) == "(41, 93) True (41, 93)"


def test_legacy_switch_restores_the_neighbour_form():
    for p in ("p", "a"):
        assert _run(INCOGNITA_CPINC=p, INCOGNITA_GPRESFIX="0") == "None False (41, 93)"
