"""The physics.hf contract holds: every module imports, every ported routine is anchored to
real TALYS source, attribution is present, and T0's files exist (physics/hf/CONTRACT.md)."""

from __future__ import annotations

import importlib
import inspect
import os
import pkgutil
import re
from pathlib import Path

import pytest

import physics.hf as hf

HF = Path(hf.__file__).parent
TALYS_SRC = Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src")) / "source"
ANCHOR = re.compile(r"([A-Za-z0-9_]+\.f(?:90)?):(\d+) \(([A-Za-z0-9_]+)\)")
ATTRIBUTION = "Ported from TALYS-2.x (https://github.com/arjankoning1/talys), MIT License"

# the WP-26 toy predates the port and is not part of it (contract §2)
LEGACY = {"physics.hf.capture"}


def _modules():
    for m in pkgutil.walk_packages(hf.__path__, "physics.hf."):
        if m.name not in LEGACY:
            yield m.name


@pytest.mark.parametrize("name", sorted(_modules()))
def test_module_imports(name):
    importlib.import_module(name)


def _ported_modules():
    for name in _modules():
        mod = importlib.import_module(name)
        if mod.__doc__ and "TALYS routines ported here" in mod.__doc__:
            yield name, mod


def test_ported_modules_carry_attribution_task_and_test():
    found = 0
    for name, mod in _ported_modules():
        found += 1
        assert ATTRIBUTION in mod.__doc__, f"{name}: missing MIT attribution (contract §3)"
        assert re.search(r"Task: T\d+", mod.__doc__), f"{name}: no owning task"
        assert re.search(r"Acceptance test: [A-Z0-9-]+", mod.__doc__), f"{name}: no test id"
    assert found >= 30


def test_public_functions_name_their_talys_routine_and_test():
    for name, mod in _ported_modules():
        for fname, fn in inspect.getmembers(mod, inspect.isfunction):
            if fn.__module__ != name or fname.startswith("_"):
                continue
            doc = fn.__doc__ or ""
            assert "TALYS:" in doc, f"{name}.{fname}: no TALYS anchor"
            assert "Test:" in doc, f"{name}.{fname}: no acceptance test id"


@pytest.mark.skipif(not TALYS_SRC.is_dir(), reason="TALYS source not installed")
def test_anchors_point_at_the_routine_they_name():
    checked = 0
    for name in _modules():
        src = Path(importlib.import_module(name).__file__).read_text()
        for file, line, routine in ANCHOR.findall(src):
            path = TALYS_SRC / file
            assert path.is_file(), f"{name}: {file} not in TALYS source"
            text = path.read_text(errors="replace").splitlines()
            stmt = text[int(line) - 1].lower()
            assert re.search(r"\b(subroutine|function)\s+" + routine.lower() + r"\b", stmt), (
                f"{name}: {file}:{line} is not `{routine}`: {stmt.strip()[:80]}"
            )
            checked += 1
    assert checked > 100


def test_t0_owned_files_exist():
    for rel in (
        "CONTRACT.md",
        "NOTICE-TALYS.md",
        "yandf.py",
        "talys_reference.py",
        "reference.py",
        "core/units.py",
        "core/tensors.py",
        "ecis/bridge.py",
    ):
        assert (HF / rel).is_file(), rel


def test_notice_reproduces_the_talys_license_verbatim():
    lic = TALYS_SRC.parent / "LICENSE"
    if not lic.is_file():
        pytest.skip("TALYS LICENSE not installed")
    notice = (HF / "NOTICE-TALYS.md").read_text()
    assert lic.read_text().strip() in notice


def test_capture_toy_is_not_imported_by_the_port():
    for name in _modules():
        src = Path(importlib.import_module(name).__file__).read_text()
        # the toy module `physics.hf.capture`, not the port's `capture_fast*`/`capture_gpu*`
        assert not re.search(r"physics\.hf\.capture\b(?!_)|from \.capture\b(?!_)", src), name


def test_tensor_conventions():
    import torch

    from physics.hf.core.tensors import DTYPE, CaseBatch, pad_stack, spin_values

    assert DTYPE is torch.float64
    cb = CaseBatch(torch.tensor([26]), torch.tensor([56]), torch.tensor([1.0], dtype=DTYPE))
    assert cb.n == 1
    with pytest.raises(TypeError):
        CaseBatch(torch.tensor([26]), torch.tensor([56]), torch.tensor([1.0]))
    r = pad_stack([torch.ones(2), torch.ones(5)])
    assert r.values.shape == (2, 5) and r.masked_sum(1).tolist() == [2.0, 5.0]
    x = r.values.clone().requires_grad_(True)
    y = torch.where(r.mask, torch.log(torch.where(r.mask, x, torch.ones_like(x))), 0.0).sum()
    y.backward()
    assert torch.isfinite(x.grad).all()
    assert spin_values(2, half_integer=True).tolist() == [0.5, 1.5, 2.5]
