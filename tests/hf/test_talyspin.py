"""TALYSPIN: default TALYS root is the pinned structure copy; TALYS_DIR and INCOGNITA_TALYS_LIVE override."""
from pathlib import Path

import pytest

from physics.hf.core import constants


def test_default_root_pinned_or_legacy(monkeypatch):
    monkeypatch.delenv("INCOGNITA_TALYS_LIVE", raising=False)
    root = Path(constants.default_talys_root())
    if (constants.PINNED_TALYS_ROOT / "structure" / "abundance" / "H.abun").is_file():
        assert root == constants.PINNED_TALYS_ROOT
    else:
        assert root == Path.home() / "opt" / "talys-src"


def test_live_switch_gives_legacy(monkeypatch):
    monkeypatch.setenv("INCOGNITA_TALYS_LIVE", "1")
    assert Path(constants.default_talys_root()) == Path.home() / "opt" / "talys-src"


def test_talys_dir_wins(monkeypatch, tmp_path):
    (tmp_path / "structure" / "abundance").mkdir(parents=True)
    (tmp_path / "structure" / "abundance" / "H.abun").write_text("x")
    monkeypatch.setenv("TALYS_DIR", str(tmp_path))
    assert constants.talys_structure_path() == tmp_path / "structure"
