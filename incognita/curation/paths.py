"""Input and output locations. ``INCOGNITA_MAIN`` (default: the repository root) holds raw/, staging/, curated/, features/.
The two curated EXFOR tables the register is built from ship in data/curation/inputs/ (EXFOR-derived, CC BY 4.0); a copy under
``INCOGNITA_MAIN`` is used instead when present."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAIN = Path(os.environ.get("INCOGNITA_MAIN", REPO)).expanduser()
SHIPPED = REPO / "data" / "curation" / "inputs"
_pick = lambda p, name: p if p.exists() else SHIPPED / name   # noqa: E731

CELLS = Path(os.environ.get("INCOGNITA_EXFOR_CELLS", _pick(MAIN / "features" / "validation_cache" / "exfor_cells.parquet", "exfor_cells.parquet")))
TRUST = _pick(MAIN / "curated" / "exfor_capture_Z26-92_trust.parquet", "exfor_capture_Z26-92_trust.parquet")      # EXFOR BIB flags per dataset (+ WP-12 layer)
POINTS = MAIN / "staging" / "exfor_capture_Z26-92.parquet"            # EXFOR points (for cell -> point lists)
ENTRY_ZIP = MAIN / "raw" / "exfor" / "entry.zip"                       # the IAEA EXFOR master

DATA = REPO / "data" / "curation"
RIPL_D0 = MAIN / "raw" / "ripl4" / "RIPL-4" / "resonances" / "resonances_L0.dat"  # RIPL-4 D0 (allowed)
RECORD_FINDINGS = DATA / "record_findings.jsonl"                       # human readings of EXFOR records, quoted
REGISTER_V1 = REPO / "data" / "curate" / "review_decisions.jsonl"      # the 524-line v1 register (md5 a84fc94d)
OUT = Path(os.environ.get("CURATION_OUT", DATA))
