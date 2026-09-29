"""REDTEAM M8: KADoNiS theory-only entries are dropped by default (INDEP_FIX item 3)."""
import numpy as np

from models.macs_constraint import _kadonis_keep, load_macs


def test_keep_list_shipped():
    k = _kadonis_keep()
    assert k[(26, 56)] == "all" and len(k) == 187   # 155 measured + 32 measured at 30 keV only


def test_theory_rows_dropped(tmp_path, monkeypatch):
    tsv = tmp_path / "k.tsv"
    tsv.write_text("Z\tA\tIsomer\t30\t40\tError\n26\t56\t\t11.7\t10.0\t0.5\n26\t99\t\t5.0\t4.0\t0.5\n")
    macs, w, kt = load_macs(["Z026N030M0", "Z026N073M0"], tsv, exfor=False)
    assert w[0].sum() > 0 and w[1].sum() == 0          # Fe-99 is not on the keep list
    monkeypatch.setenv("INCOGNITA_KADONIS_KEEP", "all")
    macs, w, kt = load_macs(["Z026N030M0", "Z026N073M0"], tsv, exfor=False)
    assert w[1].sum() > 0
