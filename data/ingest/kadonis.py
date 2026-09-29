"""KADoNiS v1.0 recommended Maxwellian-averaged capture cross sections (blueprint §3.1, §6.3).

Parses ``raw/kadonis/kadonis1.0_macs.tsv`` (fetched by ``data/ingest/download.py`` as
``kadonis1_macs`` from ``https://exp-astro.de/kadonis1.0/maketable.php?type=macs``; sha256
in ``raw/MANIFEST.json``). One row per target: ``Z A Isomer Sym`` then the MACS in mb at
kT = 5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100 keV and the uncertainty at 30 keV; ``-``
marks a missing value; ``Isomer`` is blank for the ground state, ``g``/``m`` where the
table distinguishes them.

    uv run python -m data.ingest.kadonis            # prints the 197Au row and the table size
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

REPO = Path(__file__).resolve().parents[2]
KADONIS_MACS = REPO / "raw" / "kadonis" / "kadonis1.0_macs.tsv"
KT_KEV: tuple[int, ...] = (5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100)


def _num(tok: str) -> float | None:
    tok = tok.strip()
    if tok in ("", "-"):
        return None
    return float(tok)


def read_macs(path: Path = KADONIS_MACS) -> pl.DataFrame:
    """Columns: Z, N, A, isomer, symbol, macs_<kT>_mb (11 columns), macs_30_err_mb."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        header = fh.readline()
        if not header.startswith("Z\tA"):
            raise ValueError(f"{path}: unexpected header {header[:40]!r}")
        for line in fh:
            if not line.strip():
                continue
            tok = line.rstrip("\n").split("\t")
            if len(tok) < 16:
                raise ValueError(f"{path}: short row {line[:60]!r}")
            Z, A = int(tok[0]), int(tok[1])
            rec = {
                "Z": Z,
                "N": A - Z,
                "A": A,
                "isomer": tok[2].strip(),
                "symbol": tok[3].strip(),
            }
            for kt, t in zip(KT_KEV, tok[4:15], strict=True):
                rec[f"macs_{kt}_mb"] = _num(t)
            rec["macs_30_err_mb"] = _num(tok[15])
            rows.append(rec)
    return pl.DataFrame(rows)


def ground_state_macs30(path: Path = KADONIS_MACS) -> pl.DataFrame:
    """Ground-state targets with a 30 keV value: Z, N, A, symbol, macs_30_mb, macs_30_err_mb."""
    df = read_macs(path)
    return (
        df.filter((pl.col("isomer") != "m") & pl.col("macs_30_mb").is_not_null())
        .select("Z", "N", "A", "symbol", "macs_30_mb", "macs_30_err_mb")
        .sort("Z", "A")
    )


if __name__ == "__main__":
    df = read_macs()
    print(f"{df.height} rows; {ground_state_macs30().height} ground states with a 30 keV MACS")
    print(df.filter((pl.col("Z") == 79) & (pl.col("A") == 197)))
