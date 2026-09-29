"""IAEA recommended cross sections for medical radionuclide production (WP-25 reference data).

Source: the IAEA Nuclear Data Section medical portal, https://www-nds.iaea.org/medical/ --
the recommended excitation functions of the IAEA Coordinated Research Projects on diagnostic
gamma and positron emitters, therapeutic radionuclides and charged-particle monitor reactions
(Hermanne et al., Nucl. Data Sheets 148 (2018) 338; Tárkányi et al., J. Radioanal. Nucl. Chem.
319 (2019) 487 and 533; Engle et al., Nucl. Data Sheets 155 (2019) 56; the 2017/2025 monitor
evaluations). Each reaction ships a zip holding a tab-separated table of the Padé/spline fit,
its uncertainty, and the thick-target yields the evaluators computed from it.

Why these files are worth more than one more EXFOR table: they are the numbers a producer
actually plans an irradiation with, and they come with the evaluators' own yields -- which is
an independent check on our stopping-power integral (``physics/charged/yields.py``) using
*their* cross section, before any question of whose cross section is right.

Three formats exist and the column labels are not reliable:

* the 2017+ layout -- ``Energy | Pade | Uncert. | Phys. yield MBq/uAh | mCi/uAh | 1 h MBq/uA |
  Saturation MBq/uA``;
* an older layout with a repeated ``Energy`` column between the fit and the yields;
* the Y1/Y2/A1/A2 layout -- ``Energy | sigma | Y1 GBq/C | Y2 MBq/uAh | A1 MBq | A2 MBq``, with
  no cross-section uncertainty at all.

In at least one Y1/Y2 file (``zn867gat``, 68Zn(p,2n)67Ga) Y2 is labelled MBq/uAh but is not
Y1 × 3.6, so the physical yield is taken from GBq/C when that column exists (1 GBq/C =
3.6 MBq/µAh exactly) and the disagreement is recorded rather than silently resolved.

Usage::

    uv run python -m data.ingest.iaea_medical fetch   # crawl + download into raw/iaea_medical/
    uv run python -m data.ingest.iaea_medical build   # parse into staging/iaea_medical.parquet
"""
from __future__ import annotations

import concurrent.futures as cf
import html
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "raw" / "iaea_medical"
STAGING = REPO / "staging" / "iaea_medical.parquet"
BASE = "https://www-nds.iaea.org/medical/"
CATEGORIES = ("positron_emitters", "gamma_emitters", "therapeutic", "monitor_reactions_2025")
UA = "Mozilla/5.0 (incognita research; contact via github.com/Near-Shore-Design)"
LICENSE = ("IAEA-NDS medical portal: open, cite Hermanne et al. NDS 148 (2018) 338, "
           "Tarkanyi et al. JRNC 319 (2019) 487/533, Engle et al. NDS 155 (2019) 56")

_SYMBOLS = (
    "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn "
    "Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce "
    "Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn "
    "Fr Ra Ac Th Pa U"
).split()
Z_OF = {s: i + 1 for i, s in enumerate(_SYMBOLS)}

PROJECTILE = {"p": "p", "d": "d", "α": "a", "a": "a", "3 He": "h", "3He": "h", "γ": "g",
              "n": "n"}

_LABEL = re.compile(
    r"^\s*(nat|\d+)\s*([A-Z][a-z]?)\s*\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)\s*"
    r"(\d+)\s*([a-z+]*)\s*([A-Z][a-z]?)\s*$")


def parse_label(label: str) -> dict:
    """``'100 Mo(p,2n) 99m Tc'`` -> target/projectile/product fields.

    ``state`` is ``''`` (the label names no state: ground + isomers, which is what an
    activation measurement of a nuclide with no long-lived isomer reports), ``'m'``, ``'g'``,
    or ``'g+m'``.
    """
    lab = html.unescape(label)
    m = _LABEL.match(lab)
    if not m:
        raise ValueError(f"unparseable IAEA reaction label {label!r}")
    ta, tsym, proj, ejec, pa, state, psym = m.groups()
    if proj not in PROJECTILE:
        raise ValueError(f"unknown projectile {proj!r} in {label!r}")
    return {
        "label": lab,
        "target_z": Z_OF[tsym],
        "target_a": 0 if ta == "nat" else int(ta),
        "projectile": PROJECTILE[proj],
        "ejectiles": ejec.replace(" ", ""),
        "product_z": Z_OF[psym],
        "product_a": int(pa),
        "product_state": state,
    }


def _get(url: str, timeout: int = 60) -> bytes | None:
    try:
        with urlopen(Request(url, headers={"User-Agent": UA}), timeout=timeout) as r:
            return r.read()
    except Exception:
        return None


def crawl() -> dict:
    """Reaction index: page stem -> label, categories, zip filename (None if none offered)."""
    out: dict[str, dict] = {}
    for cat in CATEGORIES:
        page = _get(BASE + cat + ".html")
        if page is None:
            raise RuntimeError(f"cannot fetch {BASE}{cat}.html")
        text = page.decode("utf-8", errors="replace")
        for m in re.finditer(r'href="([a-z0-9]+)0\.html"\s*>(.*?)</a>', text, re.S | re.I):
            lab = re.sub(r"<[^>]*>|\s+", " ", m.group(2)).strip()
            ent = out.setdefault(m.group(1), {"label": html.unescape(lab), "categories": []})
            ent["categories"].append(cat)

    def zip_for(stem: str) -> str | None:
        # The tabulated-values frames (<stem>4.html, <stem>6.html) link the zip; its name is
        # not always <stem>t.zip (nip61cu -> nip61cu25t.zip, which itself 404s).
        for suffix in ("4", "6"):
            page = _get(BASE + stem + suffix + ".html")
            if page:
                z = re.findall(r'href="([^"]+\.zip)"', page.decode("latin1"), re.I)
                if z:
                    return z[0]
        return None

    with cf.ThreadPoolExecutor(6) as ex:
        for stem, z in zip(list(out), ex.map(zip_for, list(out)), strict=True):
            out[stem]["zip"] = z
    return out


def fetch() -> None:
    sys.path.insert(0, str(REPO))
    from data.ingest.download import digest, load_manifest, now, save_manifest

    RAW.mkdir(parents=True, exist_ok=True)
    index = crawl()
    (RAW / "index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n")

    def dl(z: str) -> tuple[str, bool]:
        dest = RAW / "zips" / z
        if dest.is_file() and dest.stat().st_size > 0:
            return z, True
        blob = _get(BASE + z)
        if not blob:
            return z, False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
        return z, True

    zips = sorted({v["zip"] for v in index.values() if v["zip"]})
    with cf.ThreadPoolExecutor(6) as ex:
        results = dict(ex.map(dl, zips))
    missing = sorted(z for z, ok in results.items() if not ok)
    # Load-modify-save in one short window: other sessions write this manifest too.
    m = load_manifest()
    for z, ok in results.items():
        if not ok:
            continue
        p = RAW / "zips" / z
        m["files"][f"iaea_medical/zips/{z}"] = {
            "source": "iaea_medical", "url": BASE + z, "license": LICENSE, "phase": 3,
            "status": "adopted", "fetched_at": now(), "bytes": p.stat().st_size,
            "sha256": digest(p), "problems": None,
            "notes": "IAEA recommended medical-isotope cross section + yields (WP-25)",
        }
    ip = RAW / "index.json"
    m["files"]["iaea_medical/index.json"] = {
        "source": "iaea_medical", "url": BASE, "license": LICENSE, "phase": 3,
        "status": "adopted", "fetched_at": now(), "bytes": ip.stat().st_size,
        "sha256": digest(ip), "problems": ([f"404: {z}" for z in missing] or None),
        "notes": f"crawl of {', '.join(CATEGORIES)}; {len(index)} reactions",
    }
    save_manifest(m)
    print(f"[iaea_medical] {len(index)} reactions, {len(zips) - len(missing)} zips, "
          f"missing {missing}")


def _num(tok: str) -> float | None:
    try:
        return float(tok)
    except ValueError:
        return None


def parse_table(text: str) -> tuple[list[dict], list[str]]:
    """Rows of one IAEA table: e_mev, xs_mb, xs_unc_mb, phys_yield_mbq_uah, a1h_mbq_ua,
    asat_mbq_ua. Returns (rows, problems)."""
    lines = text.replace("﻿", "").replace("ï»¿", "").splitlines()
    problems: list[str] = []
    hdr = next((i for i, ln in enumerate(lines)
                if ln.split("\t")[0].strip().lower() == "energy"), None)
    if hdr is None or hdr + 1 >= len(lines):
        return [], ["no Energy header"]
    units_raw = [u.strip().strip("()").strip() for u in lines[hdr + 1].split("\t")]
    unit_pos = [j for j, u in enumerate(units_raw) if u]
    units_nonempty = [units_raw[j] for j in unit_pos]
    rows: list[dict] = []
    for ln in lines[hdr + 2:]:
        raw = [x.strip() for x in ln.split("\t")]
        if not raw or _num(raw[0]) is None:
            continue
        # Two alignments occur and neither holds everywhere. Positional (tab i is unit i)
        # survives an empty cell -- 44Ca(p,n) has no uncertainty on its first row -- but not
        # a units line padded with extra tabs ("Yield\t\tYield") above data rows that are
        # not. Collapsed (drop empties) handles the padding but misplaces an empty cell.
        # Positional wins when no number sits under an empty unit; else collapsed when the
        # widths agree; else only energy and cross section are trusted.
        stray = any(_num(t) is not None for j, t in enumerate(raw)
                    if t and (j >= len(units_raw) or not units_raw[j]))
        if not stray:
            units = [units_raw[j] if j < len(units_raw) else "" for j in range(len(raw))]
            vals = [_num(t) if t else None for t in raw]
        else:
            toks = [t for t in raw if t]
            if len(toks) == len(units_nonempty):
                units, vals = units_nonempty, [_num(t) for t in toks]
            else:
                problems.append(f"row width {len(toks)} != units width {len(units_nonempty)}; "
                                "kept energy and cross section only")
                units = units_nonempty[:2]
                vals = [_num(t) for t in toks[:2]]
        if len(units) < 2 or vals[0] is None:
            continue
        r = {"e_mev": vals[0], "xs_mb": None, "xs_unc_mb": None, "phys_yield_mbq_uah": None,
             "phys_yield_label_mbq_uah": None, "a1h_mbq_ua": None, "asat_mbq_ua": None}
        # col 1 is the recommended cross section in every layout
        if units[1].lower() == "mb":
            r["xs_mb"] = vals[1]
        if len(units) > 2 and units[2].lower() == "mb":
            r["xs_unc_mb"] = vals[2]
        # yields: first MBq/uAh (or GBq/C) after the cross-section columns; then activity
        # columns, 1 h first and saturation second
        act = []
        for j in range(2, len(units)):
            u = units[j].lower().replace(" ", "")
            if u == "gbq/c" and vals[j] is not None:
                r["phys_yield_mbq_uah"] = vals[j] * 3.6
            elif u == "mbq/uah" and r["phys_yield_label_mbq_uah"] is None:
                r["phys_yield_label_mbq_uah"] = vals[j]
            elif u in ("mbq/ua", "mbq"):
                act.append(vals[j])
        if r["phys_yield_mbq_uah"] is None:
            r["phys_yield_mbq_uah"] = r["phys_yield_label_mbq_uah"]
        if len(act) >= 2:
            r["a1h_mbq_ua"], r["asat_mbq_ua"] = act[0], act[1]
        rows.append(r)
    return rows, sorted(set(problems))


def build() -> Path:
    import polars as pl

    index = json.loads((RAW / "index.json").read_text())
    records, report = [], {}
    for stem, ent in sorted(index.items()):
        if not ent.get("zip"):
            report[stem] = "no zip offered"
            continue
        zp = RAW / "zips" / ent["zip"]
        if not zp.is_file():
            report[stem] = "zip not downloaded"
            continue
        try:
            meta = parse_label(ent["label"])
        except ValueError as exc:
            report[stem] = str(exc)
            continue
        zf = zipfile.ZipFile(zp)
        txt = [n for n in zf.namelist() if n.lower().endswith(".txt")]
        if not txt:
            report[stem] = "no .txt in zip"
            continue
        rows, problems = parse_table(zf.read(txt[0]).decode("utf-8", errors="replace"))
        if problems:
            report[stem] = "; ".join(problems)
        for r in rows:
            records.append({"stem": stem, "category": ",".join(ent["categories"]),
                            "zip": ent["zip"], **meta, **r})
    df = pl.DataFrame(records, infer_schema_length=None)
    STAGING.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(STAGING)
    (STAGING.with_suffix(".report.json")).write_text(json.dumps(report, indent=1) + "\n")
    print(f"[iaea_medical] {df['stem'].n_unique()} reactions, {len(df)} rows -> {STAGING}; "
          f"{len(report)} with problems")
    return STAGING


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    {"fetch": fetch, "build": build}[cmd]()
