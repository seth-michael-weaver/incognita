#!/usr/bin/env python3
"""KWCOV B7b: response of the JLM / folding-alpha keywords vs stock TALYS-2.25 (b2_response's metric through fidelity.py).

    PY=~/fastgate_data/eng/16606b356d6e/.venv/bin/python   # WSL
    $PY scripts/kwcov/b7b_response.py --target fe56 --response "jlmomp y" [--mode default,talys]

Stock runs are cached (trimmed: channel totals only) in ~/kwcov/stock/b7b, engine runs in ~/kwcov/b7b_eng (delete that
directory after a code change: the engine cache key is the deck, not the commit).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import b2_response as B  # noqa: E402
import fidelity as F  # noqa: E402

B.TARGETS.setdefault("pb208", ("pb", 82, 208))
F.STOCK_CACHE = Path(os.path.expanduser("~/kwcov/stock/b7b"))
F.ENGINE_CACHE = Path(os.path.expanduser("~/kwcov/b7b_eng"))
B.CACHE = F.STOCK_CACHE

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "_engine_child":
        B._engine_child(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    else:
        F.STOCK_CACHE.mkdir(parents=True, exist_ok=True)
        F.ENGINE_CACHE.mkdir(parents=True, exist_ok=True)
        # the engine child is spawned as `python <b2_response.py> _engine_child`, which is b2's own entry point
        F.main()
