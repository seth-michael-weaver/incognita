"""Regression tests for code outside physics/hf.

Covers the capture-set-v2 staging cache (scripts/build_capture_v2.py), the talysworld local tool (scripts/talysworld:
gridtop pad, cache key, library overlay), and the light-evaluation step of the site build
(scripts/add_light_evals.py); the site translations are checked in tests/test_site_i18n.py. No engine, no WSL data
and no network needed.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import types
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TW = REPO / "scripts" / "talysworld"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------------------------- capture set v2 staging


@pytest.fixture
def capv2():
    pytest.importorskip("pyarrow")
    sys.path.insert(0, str(REPO))
    from data.ingest import exfor as X
    old = (X.V2_FIXES, X.EXFOR_VERSION, {k: set(v) for k, v in X.V2_LOG.items()})
    yield _load(REPO / "scripts" / "build_capture_v2.py", "build_capture_v2_t"), X
    X.V2_FIXES, X.EXFOR_VERSION = old[0], old[1]
    X.V2_LOG.clear(); X.V2_LOG.update(old[2])


def _fake_main(tmp_path: Path) -> Path:
    main = tmp_path / "main"
    (main / "raw" / "exfor").mkdir(parents=True)
    with zipfile.ZipFile(main / "raw" / "exfor" / "entry_2026-10-14.zip", "w") as z:
        z.writestr("dummy.txt", "no capture here\n")   # no "(N,G)": staging writes an empty table
    return main


def test_capture_v2_stage_cache_is_keyed_by_fixes(capv2, tmp_path):
    """stage() reused work/stage_<tag>.parquet whenever it existed, whatever fixes, exfor.py or snapshot made it: after the
    D4 review fix (d32c3e04 changed what 'unc' writes) a rerun in the same --work directory would silently have shipped
    the pre-fix staging. A cache made with other fixes must not be returned."""
    B, X = capv2
    main, work = _fake_main(tmp_path), tmp_path / "work"
    work.mkdir()
    fresh = B.stage(main, work, "v2", X.V2_ALL)                       # builds (empty) staging and its log
    assert B.stage(main, work, "v2", X.V2_ALL) == fresh                # same inputs: the cache is used
    stale = dict(fresh, fixes=["numfix"], marker="stale")              # a log written by another fix set under the same tag
    stale.pop("cache_key", None)
    (work / "stage_v2.json").write_text(json.dumps(stale))
    again = B.stage(main, work, "v2", X.V2_ALL)
    assert again.get("marker") != "stale" and again["fixes"] == sorted(X.V2_ALL)


# ---------------------------------------------------------------------------------------------- talysworld


@pytest.fixture
def engine_grid(tmp_path, monkeypatch):
    """engine_grid with a stub engine_job (the real one rewrites os.environ on import and needs the engine)."""
    ej = types.ModuleType("engine_job")
    ej.INP, ej.ENG = str(tmp_path / "inputs"), str(tmp_path / "eng")
    ej.ARMS = {"P": ["P"]}
    ej.CH = {"capture": "capture_mb"}
    ej.cn_separation_mev = lambda z, a: [0.0, 9.1, -3.581234, 1.0, 2.0, 3.0, 4.0]
    monkeypatch.setitem(sys.modules, "engine_job", ej)
    monkeypatch.setitem(sys.modules, "prodrun", None)   # the run stops at the engine import, after writing its grid
    return _load(TW / "engine_grid.py", "engine_grid_t")


def test_gridtop_pad_does_not_depend_on_cached_smin(engine_grid, tmp_path):
    """The service runs a nucleus's first curve with S looked up by the job (full precision) and later curves with the
    s_min_mev that job returned (rounded to 1e-4 MeV), so the pad energy, the run's grid top and possibly the outgoing
    grid differed between the first and every later run of the same nucleus (state carried between runs)."""
    grids = []
    for i, smin in enumerate((None, -3.5812)):     # first run: looked up (-3.581234); later: the service's cached value
        out = engine_grid.run(53, 109, [1e3, 2e4], "P", "", str(tmp_path / f"w{i}"), gridtop=True, smin=smin, keep=True)
        assert out["s_min_mev"] == -3.5812
        grids.append(json.loads((tmp_path / f"w{i}" / "grid.json").read_text()))
    assert grids[0] == grids[1]


@pytest.fixture
def server(monkeypatch):
    monkeypatch.delenv("TW_ENG", raising=False)
    return _load(TW / "server.py", "tw_server_t")


def test_cache_key_follows_the_engine(server, tmp_path, monkeypatch):
    """TW_ENG selects the engine, but the cache key was hard-coded to 16606b356d6e: pointing the service at another engine
    returned the old engine's cached curves as if new."""
    keys = []
    for commit in ("16606b356d6e", "0123456789ab"):
        eng = tmp_path / commit
        eng.mkdir()
        (eng / "ENGINE_COMMIT").write_text(commit + "aaaa\n")
        monkeypatch.setattr(server, "ENG", str(eng))
        keys.append(server.cache_key(26, 56, "P", ""))
    assert keys[0] != keys[1]
    # the default install keeps its existing cache (same key as before the fix)
    monkeypatch.setattr(server, "ENG", str(tmp_path / "16606b356d6e"))
    tag = ["16606b356d6e", "libv02-inputs", 26, 56, "P", ""] + (["gridtop-pad1"] if server.GRIDTOP else [])
    import hashlib
    assert server.cache_key(26, 56, "P", "") == hashlib.sha256(json.dumps(tag).encode()).hexdigest()[:16]


def test_library_overlay_is_current_and_reads_anchor_factor(server):
    """The service overlaid library v0.2.1 while the site and the library are v0.2.2, and its anchor regex expected
    '(measured MACS30 anchor)' while v0.2.1/v0.2.2 write '(measured MACS30 anchor; centre-of-mass ...)': no ANCHORED nucleus
    got its factor, so the classic page never said that the library curve is the engine times a factor."""
    pytest.importorskip("pyarrow")
    server.load_library()
    assert "v0.2.2" in server.LIB
    anch = [d for d in server.LIBRARY.values() if d["tier"] == "ANCHORED"]
    assert len(anch) == 21 and all(d["anchored_factor"] for d in anch)
    fe60 = server.LIBRARY[(26, 60)]
    assert abs(fe60["anchored_factor"] - 0.817 * 1.0) < 0.05   # v0.2.2 factor of Fe-60 (anchored_rescale_v022.csv)


# ---------------------------------------------------------------------------------------------- light evaluations


def _site(tmp_path, evals):
    out, src = tmp_path / "data", tmp_path / "light_evals"
    (out / "n" / "6").mkdir(parents=True)
    src.mkdir()
    (out / "index.json").write_text(json.dumps({"rows": [], "light_evals": {"6-12": "OLD1"}}))
    (out / "n" / "6" / "12.json").write_text(json.dumps({"meas": {"ds": []}, "rm": {"id": "OLD1"}}))
    for name, ev in evals.items():
        (src / f"{name}.json").write_text(json.dumps(ev, ensure_ascii=False), encoding="utf-8")
    return out, src


def test_light_evals_read_utf8(tmp_path):
    """add_light_evals opened the evaluation JSON with the platform encoding: on Windows (cp1252) a UTF-8 'µ' in a label or
    caveat became 'Âµ' on the site, silently."""
    ae = _load(REPO / "scripts" / "add_light_evals.py", "add_light_evals_t")
    ev = {"id": "C12RM9", "Z": 6, "A": 12, "label": "R-matrix, 10 µeV – 1.80 MeV", "caveat": "χ²/dof 3.1"}
    out, src = _site(tmp_path, {"C12RM9": ev})
    ae.apply(out, src)
    rm = json.loads((out / "n" / "6" / "12.json").read_text(encoding="utf-8"))["rm"]
    assert rm["label"] == ev["label"] and rm["caveat"] == ev["caveat"]


def test_light_evals_withdrawn_evaluation_leaves_no_trace(tmp_path):
    """Run alone (its documented use), add_light_evals kept the 'rm' block of an evaluation that is no longer in
    data/light_evals: the page would go on showing a withdrawn evaluation."""
    ae = _load(REPO / "scripts" / "add_light_evals.py", "add_light_evals_t2")
    out, src = _site(tmp_path, {})
    ae.apply(out, src)
    assert "rm" not in json.loads((out / "n" / "6" / "12.json").read_text())
    assert json.loads((out / "index.json").read_text())["light_evals"] == {}
