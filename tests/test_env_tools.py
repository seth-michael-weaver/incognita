"""WP-08: the physics binaries respond to a trivial input.

The same checks run in three places and must agree:

* on the dev box, against the root-less env (micromamba ``incognita-phys`` +
  TALYS built under ``~/opt``; see docs/environment.md, docs/talys-install.md);
* inside the container image (``docker/smoke.sh`` -> this file);
* in CI (``.github/workflows/containers.yml`` runs the image's smoke.sh).

Every test skips, rather than fails, when its binary is not present, so the
ordinary ``uv run pytest`` on a Python-only machine stays green.

Resolution order for each tool: ``$TALYS_BIN`` / ``$NJOY_BIN`` / ``$OPENMC_BIN``,
then ``PATH``, then the dev-box locations.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from physics.talys.runner import talys_binary, talys_dir

ROOTLESS_BIN = Path.home() / "micromamba" / "envs" / "incognita-phys" / "bin"
TIMEOUT = 120


def _find(name: str, env_var: str) -> Path | None:
    for cand in (os.environ.get(env_var), shutil.which(name), ROOTLESS_BIN / name):
        if cand and Path(cand).is_file() and os.access(cand, os.X_OK):
            return Path(cand)
    return None


def _run(cmd: list[str], stdin: str = "", **kw) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, input=stdin, capture_output=True, text=True, timeout=TIMEOUT, check=False, **kw
    )


TALYS = talys_binary() if os.access(talys_binary(), os.X_OK) else _find("talys", "TALYS_BIN")
NJOY = _find("njoy", "NJOY_BIN")
OPENMC = _find("openmc", "OPENMC_BIN")

needs_talys = pytest.mark.skipif(TALYS is None, reason="talys binary not found")
needs_njoy = pytest.mark.skipif(NJOY is None, reason="njoy (NJOY2016) binary not found")
needs_openmc = pytest.mark.skipif(OPENMC is None, reason="openmc binary not found")


# --- TALYS -------------------------------------------------------------------


@needs_talys
def test_talys_runs_and_rejects_empty_input():
    """Empty stdin must produce the input-validation error, not a crash."""
    proc = _run([str(TALYS)])
    assert proc.returncode == 0, proc.stderr
    assert "TALYS-error: projectile must be given" in proc.stdout


@needs_talys
def test_talys_fe56_capture_1mev(tmp_path):
    """Plan step 4: 56Fe(n,gamma) at 1 MeV completes and the DB is resolvable.

    Needs the full structure database (8.7 GB). Images built with
    TALYS_STRUCTURE=minimal only carry structure/abundance, so skip unless the
    levels directory is there (mount it at $TALYS_DIR/structure).
    """
    tdir = talys_dir() if TALYS == talys_binary() else TALYS.resolve().parent.parent
    if not (tdir / "structure" / "levels").is_dir():
        pytest.skip(f"full TALYS structure DB not present under {tdir}/structure")
    (tmp_path / "talys.inp").write_text("projectile n\nelement fe\nmass 56\nenergy 1.\n")
    with open(tmp_path / "talys.inp") as inp, open(tmp_path / "talys.out", "w") as out:
        proc = subprocess.run(
            [str(TALYS)],
            stdin=inp,
            stdout=out,
            stderr=subprocess.STDOUT,
            cwd=tmp_path,
            env={**os.environ, "TALYS_DIR": str(tdir)},
            timeout=TIMEOUT,
            check=False,
        )
    text = (tmp_path / "talys.out").read_text()
    assert proc.returncode == 0
    assert "TALYS-error" not in text, text[:2000]
    assert "TALYS-2" in text
    assert "successful calculation" in text


# --- NJOY2016 ------------------------------------------------------------------


@needs_njoy
def test_njoy_banner_on_stop():
    """A lone ``stop`` card prints the version banner and exits 0."""
    proc = _run([str(NJOY)], stdin="stop\n")
    assert proc.returncode == 0, proc.stderr
    assert "njoy 2016" in proc.stdout.lower(), proc.stdout[:500]


# --- OpenMC ------------------------------------------------------------------


@needs_openmc
def test_openmc_version():
    proc = _run([str(OPENMC), "--version"])
    assert proc.returncode == 0, proc.stderr
    assert "OpenMC version 0." in proc.stdout, proc.stdout[:500]


@needs_openmc
def test_openmc_python_api_matches_binary():
    """The conda env next to the binary exposes the same version via Python."""
    python = OPENMC.parent / "python"
    if not python.is_file():
        pytest.skip(f"no python next to {OPENMC}")
    ver = _run([str(OPENMC), "--version"]).stdout.split()[2]
    proc = _run([str(python), "-c", "import openmc; print(openmc.__version__)"])
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip().startswith(ver.split("-")[0])
