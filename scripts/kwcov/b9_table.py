"""B9: per-T9 ratio table ours/stock for one file/column (reads the cached JSONs of b9_response.py)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import b9_response as B
t, kw, f, c = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s, o = B.stock(t, kw), B.ours(t, kw)
T = s["files"][f]["T"]
for i, x in enumerate(T):
    a, b = o["files"][f][c][i], s["files"][f][c][i]
    print(f"{x:8.4g} ours={a:.5e} stock={b:.5e} ratio={a / b if b else float('nan'):.4f}")
