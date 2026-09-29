#!/usr/bin/env python3
"""README "Uncertainties": the MEASURED-tier interval on post-cutoff measurements (RETRO-MEASURED; time split, sealed for
intervals, read once). Rows = the 286 rule-P-clean rows of docs/release/uq/retro_measured_rows.parquet; strata >= 15 rows.
    python scripts/release/score_retro_measured.py docs/release/uq/retro_measured_rows.parquet OUT.md
Same arithmetic as UQ_EVIDENCE / docs/release/uq/RETRO_MEASURED.md (PRIMARY section), via incognita.uq.calibration_report."""
import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from incognita.uq.calibration_report import prepare, report  # noqa: E402
d = pd.read_parquet(sys.argv[1]); d = d[~d.P.astype(bool)]
txt, _ = report(prepare(d), f"PRIMARY: {len(d)} clean rows", [], "nuclide_id", 2000, min_rows=15)
open(sys.argv[2], "w").write(txt); print(txt)
