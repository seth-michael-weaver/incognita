"""Where INCOGNITA's release scripts find their inputs and put their outputs.

Nothing in the release code hard-codes a home directory. Every location comes from an environment
variable, with a default relative to the user's home or to the repository:

  INCOGNITA_MAIN          the data directory of the main pipeline (staging/, curated/, raw/).
                        Default: the repository root (where data/ingest/download.py writes raw/ and staging/).
  INCOGNITA_EVALUATED   staged evaluated-library grids written by data/ingest/build_evaluated.py
                        (jendl5.parquet, tendl2025.parquet, endfb81.parquet, ...).
                        Default: $INCOGNITA_MAIN/staging/evaluated.
  INCOGNITA_INPUTS      inputs we do not redistribute, staged by the user (see docs/release/INPUTS.md):
                        the exam-row tables built from EXFOR, criticality / shielding models, ...
                        Default: ~/incognita-inputs.
  INCOGNITA_WORK        where the reproduce scripts write regenerated tables. Default: <repo>/out/reproduce.
  INCOGNITA_EVAL_PARAMS the per-nuclide correction table of the evaluation (a CSV with the columns of
                        incognita/eval/data/eval_v5_params.csv). Default: that file. Point it at a newer
                        fit (for example a v5b refit) to evaluate with it; nothing else changes.
  INCOGNITA_EVAL_CHOICE the per-channel base choice (eval_v3_choice.json). Default: the shipped file.
  TALYS_DIR             the TALYS source tree; only its structure/ database is read. Default: ~/opt/talys-src.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PKG = Path(__file__).resolve().parent


def _env_path(name: str, default: Path) -> Path:
    v = os.environ.get(name)
    return Path(v).expanduser() if v else default


def main_dir() -> Path:
    return _env_path("INCOGNITA_MAIN", REPO)


def evaluated_dir() -> Path:
    return _env_path("INCOGNITA_EVALUATED", main_dir() / "staging" / "evaluated")


def inputs_dir() -> Path:
    return _env_path("INCOGNITA_INPUTS", Path.home() / "incognita-inputs")


def work_dir() -> Path:
    return _env_path("INCOGNITA_WORK", REPO / "out" / "reproduce")


def talys_dir() -> Path:
    return _env_path("TALYS_DIR", Path.home() / "opt" / "talys-src")


def eval_params_path() -> Path:
    return _env_path("INCOGNITA_EVAL_PARAMS", PKG / "eval" / "data" / "eval_v5_params.csv")


def eval_choice_path() -> Path:
    return _env_path("INCOGNITA_EVAL_CHOICE", PKG / "eval" / "data" / "eval_v3_choice.json")


def require(path: Path, what: str, how: str) -> Path:
    """Return path if it exists, else stop with a message that says what is missing and how to get it."""
    if not Path(path).exists():
        raise SystemExit(f"missing input: {what}\n  expected at: {path}\n  how to get it: {how}")
    return Path(path)
