"""Lab data that the public tree does not ship, and how a test says it needs it.

The public export (scripts/release/export_public.sh) carries code and small fixtures, not the
raw inputs or the generated feature sets. A test that reads one of those says so, and skips on
a fresh clone instead of erroring; in the lab checkout, where the files exist, it runs as
before.

    pytestmark = pytest.mark.needs_data(STANDARDS)        # whole module / class / function
    @pytest.mark.needs_data(BROAD_DESIGN)                 # one test
    need_data(STANDARDS)                                  # inside a fixture or helper
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# repo-relative paths of lab inputs that are not in the public tree
STANDARDS = "raw/standards/std2017"  # IAEA Neutron Standards 2017 point-wise tables
BROAD_DESIGN = "features/talys_sweep_broad/design.json"  # the 482-nuclide sweep design


def missing(*paths: str | Path) -> list[str]:
    """The repo-relative `paths` that do not exist."""
    return [str(p) for p in paths if not (REPO / p).exists()]


def need_data(*paths: str | Path) -> None:
    """Skip the running test unless every repo-relative path exists."""
    gone = missing(*paths)
    if gone:
        pytest.skip(f"lab file not in this checkout (not shipped in the public tree): "
                    f"{', '.join(gone)}")


def talys_structure_dir_or_missing() -> Path:
    """`talys_structure_dir()`, or a path that does not exist when TALYS is not installed, so a
    module-level `skipif(not (... / "density").exists())` skips instead of failing to collect."""
    from physics.hf.structure.files import talys_structure_dir

    try:
        return talys_structure_dir()
    except FileNotFoundError:
        return REPO / "no-TALYS-structure-set-TALYS_DIR"


def main_path(rel: str | Path) -> Path:
    """Where the code finds a data file of the main checkout: the repo copy if there is one, else
    `$INCOGNITA_MAIN/rel` (default: the repository root), as `models.stage_c_data` resolves it."""
    import os

    here = REPO / rel
    if here.exists():
        return here
    return Path(os.environ.get("INCOGNITA_MAIN", Path(__file__).resolve().parents[1])) / rel


def need_main(*rels: str | Path) -> None:
    """Skip the running test unless every main-checkout data file (see `main_path`) exists."""
    gone = [str(r) for r in rels if not main_path(r).exists()]
    if gone:
        pytest.skip(f"lab data not in this checkout or $INCOGNITA_MAIN (not shipped in the public "
                    f"tree): {', '.join(gone)}")


TALYS_MISSING = "TALYS structure database not found"  # what the structure locators raise


def need_talys() -> None:
    """Skip the running test unless the TALYS structure database is installed (for tests that
    swallow the locator's FileNotFoundError or hit it in a subprocess)."""
    if not talys_structure_dir_or_missing().is_dir():
        pytest.skip("TALYS structure database not installed: set TALYS_DIR "
                    "(docs/talys-install.md)")
