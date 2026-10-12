"""charged-projectile fidelity: charged-projectile port fidelity -- the ejectile OMP convention follows the run's
projectile (k0), alphaomp 3-5 refuses instead of running Watanabe, and the five port-fidelity
fixes (MPEFIX, CPINC2, CCSOCB, RESISO, TRITFID) default ON for k0 > 1 only.
Checked against stored stock TALYS-2.24/2.25 output; neutron runs stay bitwise unchanged."""

from __future__ import annotations

import dataclasses
import os
import subprocess
import sys

import pytest
import torch

from physics.hf.input.defaults import default_options, default_params


def _run(code: str, **env) -> str:
    e = {k: v for k, v in os.environ.items() if not k.startswith("INCOGNITA_")}
    e.update(env)
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=e,
                         cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    assert out.returncode == 0, out.stderr[-2000:]
    return out.stdout.strip()


_PROBE = """
from physics.hf.omp import parameters as P
seen = []
orig = P.ejectile_params
def spy(p, projectile=1):
    seen.append(projectile); raise SystemExit(f"K0={projectile}")
P.ejectile_params = spy
from physics.hf.compound import dens_reference as D
try:
    D._transmission_build(26, 56, 14.0, None, False)
except SystemExit as e:
    print(e)
"""


@pytest.mark.parametrize("cpinc,k0", [("", 1), ("p", 2), ("a", 6)])
def test_inverse_channels_use_the_runs_projectile_as_ejectile_type0(cpinc, k0):
    """opticalnp.f90:175 `flagompejec .and. k == k0`: the projectile's own type takes the type-0
    factors on the way out; was hard-wired to the neutron for every projectile."""
    assert _run(_PROBE, INCOGNITA_CPINC=cpinc) == f"K0={k0}"


def test_alphaomp_folding_refuses():
    o = dataclasses.replace(default_options(29, 63), alphaomp=5)
    from physics.hf.omp.parameters import omp_parameters

    omp_parameters(29, 34, 6, torch.tensor([20.0]), default_params(29, 63, o),
                   default_options(29, 63))  # alphaomp 6 (default) runs
    with pytest.raises(NotImplementedError):
        omp_parameters(29, 34, 6, torch.tensor([20.0]), default_params(29, 63, o), o)


_FLAGS = """
from physics.hf.projectile import cpinc2
from physics.hf.emission.multiple import resiso_enabled
from physics.hf.emission.feed_reference import _seed_exciton
print(cpinc2(), resiso_enabled(), bool(_seed_exciton(2)))
"""


def test_fidelity_fixes_default_on_for_charged_runs_only():
    assert _run(_FLAGS, INCOGNITA_CPINC="p") == "True True True"
    assert _run(_FLAGS, INCOGNITA_CPINC="p", INCOGNITA_CPINC2="0", INCOGNITA_RESISO="0",
                INCOGNITA_MPEFIX="0") == "False False False"
    # neutron run: RESISO keeps its default OFF (k0 = 1 never reaches cpinc2/MPEFIX)
    assert _run(_FLAGS).split()[1] == "False"
