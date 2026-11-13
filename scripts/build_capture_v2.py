"""Curated EXFOR capture set v2 (CAPSET-v2): the WP-12 curation re-run on a corrected staging, Z 1-92.

The shipped capture tables (data/curation/inputs/: Z 26-92 run on 2026-09-12, Z 1-25 run on 2026-11-06) carry ingestion
defects found by a read-only hunt on 2026-11-06. This script fixes them and writes a NEW versioned product to
data/curation/capture_v2/ (the old files are not touched). Every decision it adds is a review-decision line with a reason
and the EXFOR id (review_decisions_capture_v2.jsonl); nothing is deleted silently. README.md there lists every fix with
its counts before and after; ADOPTION.md says what would change downstream.

Fixes (numbers = the defect list of the 2026-11-06 hunt):
  D1 numfix    Fortran numbers "5.     -07" read as NaN (data/ingest/exfor.py _NUM_FIX).
  D2 parser    RATIO heading; EN-MIN-APX; KT-K in DEG-C; "(N,ABS)=(N,G)" equivalences filed under (N,G).
  D3 sums      REACTION combinations that are not one capture cross section (sums over targets / processes, weighted
               state sums such as G + 1.006 M x FCT) are excluded with the REACTION-code rule of
               research/scripts/channels/score_channels_fixed.reaction_flags (flags COMBO_SUM / COMBO_DIFF / COMBO_PROD).
  D4 unc       stat = ERR-S, sys = ERR-SYS or sqrt(ERR-T^2 - ERR-S^2); stat = sqrt(ERR-T^2 - ERR-SYS^2); an unsplit
               total stays stat_sigma (as v1). Peelle: absolute-unit uncertainties are re-based on the expected value of a
               first fit (sigma / exp(mu + bias) instead of sigma / observed mean) before the final fit.
  D5 dupes     a dataset whose EXFOR STATUS says (SPSDD,X) or (DEP,X), where X is in the set with the same comparable
               quantity, is excluded (also across entries) and left out of the consensus fit; STATUS PRELM -> downweight.
  D6 slips     three x1000-type slips reviewed by hand (lines with reasons).
  D7 version   exfor_version is the snapshot actually read (2026-10-14), not the hard-coded 2026-08-27.

CAPSET-v2.1 (2026-11-07, step S9 on top of the v2 result S8; S1-S8 are unchanged and reproduce v2):
  D8 encm      incident energies compiled in the centre-of-mass frame (EN-CM, EN-RES-CM, EN-CM-MIN/-MAX) are
               converted to the lab frame, E_lab = E_cm (A+1)/A for a neutron on target mass number A (exfor.py fix
               "encm", opt-in, not in V2_ALL).
  D9 dupes     the same measurement compiled twice (two entries of one paper, or two pointers with identical values):
               the later copy is excluded, the original kept (hand lines, HAND21).
  D10 slips    unit and energy slips found by the 2026-11-07 data hunt (hand lines, HAND21): fix-unit, exclude, or an
               energy-unit correction applied at staging (ENERGY_FIX; a line with "energy_fix" and no decision).

CAPSET-v2.2 (2026-11-07, step S10 on top of the v2.1 result S9; S1-S9 are unchanged and reproduce v2.1):
  D11 totals   thermal values compiled as (N,G) SIG that are the TOTAL cross section (capture + scattering) of the sample
               (hand lines, HAND22, exclude; checked against the EXFOR record). Staging is the v2.1 staging.

Steps (inside the research checkout given by --main; nothing there is written):
  1. Stage three times from raw/exfor/entry_2026-10-14.zip with this repository's data/ingest/exfor.py: v1 behaviour
     (no fix), numfix only, all fixes. Capture predicate and 20 MeV clip of `python -m data.ingest.exfor --subset
     capture`, Z 1-92. Checks: the numfix-only Z 26-92 staging against the research staging
     staging/exfor_capture_Z26-92_2026-10-14_x4fix1 (the 2026-10-22 EXFOR numeric-fix output).
  2. Rule lines (D3, D5 SPSDD/DEP) and the hand lines (D6), then quality_model.run (research data/curate, unchanged,
     with this repository's data/curate/discrepancy.py) on Z 1-92 with the human-decision file = research
     review_decisions.jsonl + data/curation/inputs/review_decisions_Z1-25.jsonl + the CAPSET-v2 lines. The consensus fit
     leaves out the cells of datasets excluded by a CAPSET-v2 rule line (as it already leaves out compilations).
  3. PRELM lines (only where pass 1 kept or down-weighted the dataset and no earlier human line names it), pass 2.
  4. Cells (discrepancy.cells_from_parquet on the v2 staging) joined to the trust table; split Z 1-25 / Z 26-92 into
     files with the shipped schemas; counts, provenance, SHA256SUMS.

usage (the research checkout's environment):
  cd MAIN && INCOGNITA_MAIN=MAIN .venv/bin/python <this repo>/scripts/build_capture_v2.py [--main MAIN] [--work DIR]
"""
from __future__ import annotations

import argparse, collections, hashlib, json, math, os, re, subprocess, sys, time, zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data" / "curation" / "capture_v2"
INP = REPO / "data" / "curation" / "inputs"
ZIPNAME = "entry_2026-10-14.zip"
RESEARCH_STAGING = "exfor_capture_Z26-92_2026-10-14_x4fix1.parquet"
EMAX = 20e6
TAG = "exfor_capture_Z1-92_v2"
DATE = "2026-11-06"
DATE21 = "2026-11-07"
VERSION = "2.2"
DATE22 = "2026-11-07"
REVIEWER_RULE = "rule:capset-v2"
REVIEWER_HAND = "agent:claude-opus-5.5"
COMBO_EXCLUDE = ("COMBO_SUM", "COMBO_DIFF", "COMBO_PROD")
PEELLE_CLIP = 3.0  # the re-basing factor mean/consensus is clipped to [1/3, 3]

# D6: hand-reviewed x1000-type slips (checked against the EXFOR record of the 2026-10-14 entry.zip)
HAND = [
    {"entry": "14657", "subentry": "14657002", "pointer": "", "decision": "fix-unit", "factor": 0.001,
     "reason": "Y-89(n,g)Y-90m thermal Maxwellian (SIG,,MXW), Krane 2020, EXFOR 14657002: DATA 1.02 / 0.98 / 1.06 B with "
               "ERR-T 0.01-0.03 B for three irradiation positions. The other EXFOR measurements of the same isomeric thermal "
               "cross section are 1 mb: Heath 1961 11870002 (0.001 B, MXW), De Corte 1988 23488032 (0.00104 B), Farina "
               "Arbocco 2013 23266090/91 (0.00107 B). The compiled unit B is a x1000 slip for MB. fix-unit, factor 0.001 "
               "(trust 0 until the correction is applied at ingest)."},
    {"entry": "13947", "subentry": "13947004", "pointer": "", "decision": "fix-unit", "factor": 0.001,
     "reason": "Ni-60(n,g)Ni-61 partial gamma-ray cross sections (PAR,SIG,,MXW), Raman et al. 2004, EXFOR 13947004 (Table 10): "
               "240 gamma lines compiled in B that sum to 3693 B (e.g. 812 B at E-gamma 283 keV), while the same quantity "
               "from Gippner 1971 (30150003, 31 lines compiled in MB) sums to 2744 MB; a thermal capture cross section of a "
               "few barns times a gamma multiplicity of a few cannot give thousands of barns of gamma lines. The values are "
               "millibarns. fix-unit, factor 0.001."},
    {"entry": "41639", "subentry": "41639002", "pointer": "", "decision": "exclude",
     "reason": "Sb-124(n,g)Sb-125 spectrum average (SIG,,SPA), Murin 1957 (At. Energy 2, 552), EXFOR 41639002: one DATA-APRX "
               "value 2000 B with no uncertainty, at an incident energy the compiler supposed (COMMENT: 'Incident neutron "
               "energy is not given in the article, supposed by compiler as 0.0253 eV'; HISTORY 2021 changed EN-DUMMY from "
               "1 MeV). Excluded on the record: an approximate value of a quantity whose energy is not defined. It is NOT "
               "proven to be a unit slip: Courtemanche 1966 (11990002, SPA) gives 6.5 B, x300 lower, but Elgart 1971 "
               "(10728004, MXW) gives 2990 B, the same magnitude as this value, so EXFOR alone does not settle Sb-124; "
               "10728004 and 11990002 are left to the automatic layer and listed for a person to read."},
]

# CAPSET-v2.1 hand lines (2026-11-07 data hunt), each checked against the EXFOR record of the 2026-10-14 entry.zip.
# D9: the same measurement compiled twice; the later copy is excluded, the original (first compiled) is kept.
_PAV = ("Cl-35(n,g) Pavetich et al. 2019 (PR C 99, 015801) is compiled twice: entry 23468 (area 2, compiled 2019-02-27, "
        "proof-read by the author) and entry 31796 (area 3, compiled 2020-08-13, same Table VI); the SACS of the KIT1 and "
        "SPI9 samples and the 30 keV MACS 8.33 +- 0.32 mb are identical in both. Original kept: 23468.")
_JOZ = ("Jozefowicz 1963 (Nukleonika 8, 437) thermal activation cross sections are compiled twice: entry 31099 (converted "
        "1977 from EXFOR 70099, combined with 70403) and entry 31472 (compiled 1978, HISTORY 1997: 'Data from previous entry "
        "70403 recompiled'); every value and uncertainty is identical. Original kept: 31099.")
_ALP = ("Alpatov et al.: the Te-122/Te-124 isomer cross sections and resonance integrals of report ITEF-32-90 (1990, entry "
        "41039) are republished in Yad. Fiz. 58, 15 (1995, entry 41168, Table 4) from the same samples (7.01 mg Te-122, "
        "11.09 mg Te-124) with the same values (0.44 +- 0.03 b, 5.08 +- 0.36 b, 1.12 +- 0.07 b, 1.40 +- 0.11 b); 41168 "
        "also gives EN-MIN 0.0253 eV for the resonance integrals (41039: the Cd cut-off 0.48 eV). Original kept: 41039.")
HAND21 = [
    {"entry": "22939", "subentry": "22939040", "pointer": "3", "decision": "exclude", "rule": "D9_DUPLICATE",
     "superseded_by": "22939/22939040/2",
     "reason": "Ba-132 MACS (SIG,,MXW,DERIV), Dillmann et al. 2010 (PR C 81, 015801), revised in INDC(GER)-0053 (2021), EXFOR "
               "22939040: three pointers derive the MACS at kT 5-100 keV from ONE measured SACS (STATUS DEP 22939016) with "
               "three evaluated shapes (1 ENDF/B-VII.0, 2 JEFF-3.0A/3.1, 3 JENDL-3.3). Pointers 2 and 3 are identical in all "
               "11 values and uncertainties (972, 676, 561, ... mb), so pointer 3 counts pointer 2 a second time. Pointer 3 "
               "excluded; pointers 1 and 2 kept (that 1 and 2 are themselves two derivations of one SACS is left open, as "
               "for the other Dillmann DERIV entries)."},
    *[{"entry": "31796", "subentry": f"317960{i:02d}", "pointer": "", "decision": "exclude", "rule": "D9_DUPLICATE",
       "superseded_by": f"23468/234680{i:02d}/", "reason": _PAV + f" Duplicate of 23468/234680{i:02d}/."} for i in (2, 3, 4)],
    *[{"entry": "31472", "subentry": f"314720{i:02d}", "pointer": "2", "decision": "exclude", "rule": "D9_DUPLICATE",
       "superseded_by": f"31099/310990{j:02d}/2", "reason": _JOZ + f" Duplicate of 31099/310990{j:02d}/2 ({what})."}
      for i, j, what in ((2, 6, "I-127 thermal capture, ratio to Na-23"), (3, 7, "I-127 thermal capture, ratio to Mn-55"),
                         (4, 5, "In-115 to In-116m"), (5, 3, "P-31 thermal capture"))],
    *[{"entry": "41168", "subentry": f"411680{i:02d}", "pointer": "", "decision": "exclude", "rule": "D9_DUPLICATE",
       "superseded_by": f"41039/410390{i:02d}/", "reason": _ALP + f" Duplicate of 41039/410390{i:02d}/."} for i in (2, 3, 4, 5)],
    # D10: unit and energy slips
    {"entry": "14797", "subentry": "14797006", "pointer": "", "decision": "fix-unit", "factor": 0.001, "rule": "D10_UNIT_SLIP",
     "reason": "Mo-95(n,g) MACS (SIG,,MXW), Koehler 2022 (PR C 105, 054306, Table 5), EXFOR 14797006: DATA 1018 ... 346 compiled "
               "in B at kT 5-30 keV (ERR-S 31 ... 10 B). The 30 keV MACS of Mo-95 is about 0.3 b (KADoNiS 292 mb), so 346 B "
               "is a x1000 slip for 346 mb; the automatic layer had set trust 0 (x1200 vs the consensus). fix-unit, factor "
               "0.001."},
    {"entry": "14165", "subentry": "14165012", "pointer": "", "decision": "exclude", "rule": "D10_UNIT_SLIP",
     "reason": "Te-120(n,g)Te-121g, Eastman+Krane 2008 (PR C 77, 024303), EXFOR 14165012: coded SIG,,MXW but STATUS 'data from "
               "table 3 of the reference', the table of resonance integrals (every other subentry from table 3, 013-021, is "
               "coded RI, all with EN-MIN 0.5 eV, the Cd cut-off); 20.5 +- 0.9 b is the Te-120 -> Te-121g resonance "
               "integral, not a Maxwellian average at kT = 0.5 eV. Excluded: a resonance integral filed as a Maxwellian "
               "average."},
    {"entry": "14248", "subentry": "14248005", "pointer": "", "rule": "D10_ENERGY_UNIT",
     "energy_fix": {"column": "KT", "compiled_unit": "EV", "unit": "KEV", "factor": 1000.0},
     "reason": "W-186(n,g) MACS (SIG,,MXW,DERIV), Marganiec et al. 2009 (PR C 80, 025804), revised in INDC(GER)-0053 (2021), "
               "EXFOR 14248005: the KT column (5, 10, 15, ... 100) is compiled in EV, but these are the Karlsruhe MACS at "
               "kT = 5-100 keV (ANALYSIS: 'MACS are derived from ENDF/B-VII.0 renormalized to the measured SACS'; COMMON of "
               "entry 14248: KT-NRM 25 KEV; 204 +- 10 mb at kT = 30 is the W-186 30 keV MACS). The stored temperature is "
               "x1000 too small. Corrected at staging: kT x 1000 (EV -> KEV); values unchanged, decision left to the "
               "automatic layer."},
]
# CAPSET-v2.2 hand lines (2026-11-07 bug hunt round 6). D11: total cross sections compiled as capture.
_CEL = ("Celenk, Demirel, Ozmen 1991 (J. Radioanal. Nucl. Chem. 148, 393, Table 5), EXFOR entry 22234: TITLE 'Measurement of "
        "macroscopic and microscopic thermal neutron cross sections of V, Co, In, Dy and Au using neutron self absorption "
        "properties'; ANALYSIS (subentry 001, common to every subentry): 'The gamma-photopeak areas as a function of foil "
        "thickness were model fitted to yield the total thermal neutron macroscopic cross section, from which the microscopic "
        "cross-section was calculated dividing the macroscopic cross section by the number of nuclei per cm3'. The six "
        "values (002-007) are therefore total (removal) cross sections of the natural-element foils, compiled as (N,G) SIG "
        "at EN-DUMMY 0.0253 eV with no uncertainty (ERR-ANALYS: 'No uncertainties on data are given'). ")
HAND22 = [
    {"entry": "22234", "subentry": f"22234{s}", "pointer": "", "decision": "exclude", "rule": "D11_TOTAL_XS",
     "reason": _CEL + "Total cross section, not capture: " + why}
    for s, why in (
        ("002", "V-51 10.13 B = the V total at 2200 m/s (EXFOR (N,TOT) thermal median 10.5 b: capture about 5 b + "
                "scattering about 5 b), twice the V-51 capture consensus of the set (5.1 b)."),
        ("003", "Co-59 -> Co-60m 46.94 B exceeds the TOTAL Co-59 capture (about 37 b; set consensus 37.8 b), which a "
                "partial cross section to the isomer cannot; it equals the Co total (capture + about 6 b scattering; "
                "EXFOR (N,TOT) thermal median 46.0 b)."),
        ("004", "Cu-63 11.24 B (natural Cu foils, 99.9999 %) is about the natural-Cu total (absorption 3.8 b + scattering "
                "about 8 b), 2.6 x the Cu-63 capture consensus of the set (4.4 b)."),
        ("005", "In-115 -> In-116m1+m2 191.78 B is about the natural-In total (absorption about 194 b + scattering about "
                "2.6 b); the partial cross section to In-116m1+m2 is about 160-170 b."),
        ("006", "Dy-164 -> Dy-165 (g, M+) 1056 B is the natural-Dy total (absorption about 994 b + scattering about 90 b), "
                "not Dy-164 capture (about 2.7 kb; set consensus 2720 b)."),
        ("007", "Au-197 107.55 B = the Au total at 2200 m/s (capture 98.7 b + scattering about 7.9 b), 9 % above the "
                "capture standard."),
    )
]
ENERGY_FIX = {f"{h['entry']}/{h['subentry']}/{h['pointer']}": h["energy_fix"]["factor"] for h in HAND21 if "energy_fix" in h}


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def setup(main: Path):
    """This repository's data package first (patched exfor.py, discrepancy.py); the research data/curate modules that
    are not here (quality_model, review_log) are found by extending the package path."""
    sys.path.insert(0, str(REPO))
    import data.curate, data.ingest  # noqa: F401
    data.curate.__path__.append(str(main / "data" / "curate"))
    from data.curate import standards as std, discrepancy as disc
    std.STANDARDS_DIR = main / "raw" / "standards" / "std2017"
    disc.REPO = main  # quality_model takes REPO from discrepancy: research review file, spot list (read-only)
    from data.curate import quality_model as qm
    assert qm.HUMAN_DECISIONS == main / "data" / "curate" / "review_decisions.jsonl", qm.HUMAN_DECISIONS
    sys.path.append(str(main / "research" / "scripts" / "channels"))


# ----------------------------------------------------------------------------------------------------- 1. staging

_REF = re.compile(r"\((SPSDD|DEP)\s*,([^)]*)\)")


def _refs(items) -> list[tuple[str, str]]:
    out = []
    for it in items or []:
        for flag, body in _REF.findall((it.code or "") + " " + (it.text or "")):
            for r in body.split(","):
                r = r.strip()
                if re.fullmatch(r"[0-9A-Z]{5}|[0-9A-Z]{8}", r):
                    out.append((flag, r))
    return out


def stage(main: Path, work: Path, tag: str, fixes: frozenset[str], energy_fix: dict | None = None) -> dict:
    """Parse every entry holding '(N,G)', keep capture (SF2 N, SF3 G, SF6 SIG/RI, Z 1-92), clip at 20 MeV.
    energy_fix: dataset key -> factor on energy_ev and energy_sigma_ev (CAPSET-v2.1 D10 energy-unit slips)."""
    import pyarrow as pa, pyarrow.parquet as pq
    from data.ingest import exfor as X
    out, logp = work / f"stage_{tag}.parquet", work / f"stage_{tag}.json"
    zp = main / "raw" / "exfor" / ZIPNAME
    # the cache is valid only for the same fixes, the same ingest code and the same snapshot (not just the same tag)
    zst = zp.stat()
    key = hashlib.sha256(json.dumps([sorted(fixes), sha(Path(X.__file__)), zp.name, zst.st_size, int(zst.st_mtime), EMAX]
                                    + ([sorted(energy_fix.items())] if energy_fix else [])).encode()).hexdigest()[:16]
    if out.exists() and logp.exists():
        info = json.loads(logp.read_text())
        if info.get("cache_key") == key:
            return info
        print(f"stage {tag}: cached staging was made with other inputs (fixes, exfor.py or snapshot): rebuilding", flush=True)
    X.V2_FIXES = frozenset(fixes)
    X.V2_LOG.clear()
    X.EXFOR_VERSION = X.exfor_version_of(zp) if fixes else "2026-08-27"
    keep = X._subset_filter("capture", 1, 92)
    writer = pq.ParquetWriter(out.with_suffix(".tmp"), X.ExforMeasurement.ARROW_SCHEMA, compression="zstd")
    stats, errs, buf, status = collections.Counter(), [], [], {}
    t0 = time.time()
    with zipfile.ZipFile(zp) as z:
        names = sorted(n for n in z.namelist() if n.endswith(".txt"))
        for name in names:
            text = z.read(name).decode("latin-1")
            if text.startswith("DICTION") or "(N,G)" not in text:
                continue
            stats["entries"] += 1
            e = X.parse_entry(text)
            first = e.subentries[0] if e.subentries and e.subentries[0].accession.endswith("001") else None
            ebib = first.bib if first else {}
            subs = {s.accession: s for s in e.subentries}
            for m in X.build_measurements(e, stats, errs):
                if not keep(m):
                    continue
                m2 = X._clip_energy(m, EMAX)
                if m2 is None:
                    stats["clipped_out"] += 1
                    continue
                row = m2.to_row()
                k = f"{m2.entry}/{m2.subentry}/{m2.pointer or ''}"
                if energy_fix and k in energy_fix:
                    f = energy_fix[k]
                    row["energy_ev"] = [x * f for x in row["energy_ev"]]
                    if row["energy_sigma_ev"] is not None:
                        row["energy_sigma_ev"] = [x * f for x in row["energy_sigma_ev"]]
                    stats["energy_fixed"] += 1
                buf.append(row)
                s = subs[m.subentry]
                st = X._status_flags(s.bib.get("STATUS"), ebib.get("STATUS"))
                status[m.subentry] = {"refs": _refs(s.bib.get("STATUS")) + _refs(ebib.get("STATUS")),
                                      "prelm": "PRELM" in st}
            if len(buf) >= 2000:
                writer.write_table(pa.Table.from_pylist(buf, schema=X.ExforMeasurement.ARROW_SCHEMA))
                buf = []
    if buf:
        writer.write_table(pa.Table.from_pylist(buf, schema=X.ExforMeasurement.ARROW_SCHEMA))
    writer.close()
    out.with_suffix(".tmp").replace(out)  # replace: a stale staging may be there
    info = {"tag": tag, "fixes": sorted(fixes), "cache_key": key, "exfor_version": X.EXFOR_VERSION, "seconds": round(time.time() - t0),
            "stats": {k: v for k, v in stats.items() if k in ("entries", "clipped_out", "subentries", "subentries_parsed",
                                                              "energy_fixed")},
            "v2_log": {k: sorted(v) for k, v in X.V2_LOG.items()}, "status": status}
    logp.write_text(json.dumps(info))
    print(f"staged {tag}: {pq.read_metadata(out).num_rows} capture measurements, {info['seconds']} s", flush=True)
    return info


def summarize(path: Path):
    """dataset_key -> (z, n_points, n_finite_stat, n_finite_sys, reaction)."""
    import pyarrow.parquet as pq
    t = pq.read_table(path, columns=["entry", "subentry", "pointer", "target_z", "reaction", "energy_ev", "original"]).to_pylist()
    fin = lambda l: sum(1 for x in (l or []) if x is not None and x == x)
    return {f"{r['entry']}/{r['subentry']}/{r['pointer'] or ''}":
            (r["target_z"], len(r["energy_ev"] or []), fin(r["original"]["stat_sigma"]), fin(r["original"]["sys_sigma"]),
             r["reaction"]) for r in t}


def check_research_staging(main: Path, path: Path) -> dict:
    """numfix-only Z 26-92 staging vs the research numeric-fix staging (exfor_version aside)."""
    import pyarrow.parquet as pq
    import pyarrow.compute as pc
    ours = pq.read_table(path)
    ours = ours.filter(pc.greater_equal(ours["target_z"], 26))
    theirs = pq.read_table(main / "staging" / RESEARCH_STAGING)
    fix = lambda v: ("nan" if isinstance(v, float) and math.isnan(v) else [fix(x) for x in v] if isinstance(v, list)
                     else {k: fix(x) for k, x in v.items() if k != "exfor_version"} if isinstance(v, dict) else v)
    norm = lambda T: {f"{r['subentry']}/{r['pointer'] or ''}": fix(r) for r in T.to_pylist()}
    a, b = norm(ours), norm(theirs)
    diff = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    return {"ours": len(a), "research": len(b), "only_ours": sorted(set(a) - set(b))[:50], "n_only_ours": len(set(a) - set(b)),
            "only_research": sorted(set(b) - set(a))[:50], "n_only_research": len(set(b) - set(a)),
            "n_differ": len(diff), "differ": diff[:50]}


# ----------------------------------------------------------------------------------------------- 2. rule lines


def line(key: str, decision: str, reason: str, rule: str, reviewer: str = REVIEWER_RULE, **extra) -> dict:
    entry, sub, ptr = key.split("/")
    return {"entry": entry, "subentry": sub, "pointer": ptr, "decision": decision, "rule": rule, "reason": reason,
            "reviewer": reviewer, "date": DATE, **extra}


def rule_lines(stg: Path, info: dict, prior: dict) -> tuple[list[dict], list[dict], dict]:
    """D3 sums + D6 hand lines, D5 SPSDD/DEP lines, and a per-dataset audit table. ``prior``: key -> earlier human
    Decision (research file + light file); a dataset an earlier line decides keeps that decision, and a dataset an
    earlier line excludes is not a valid 'original' for D5."""
    prior_keys = set(prior)
    gone = {k for k, d in prior.items() if d.decision in ("exclude", "fix-unit")}
    import pyarrow.parquet as pq
    from data.curate import discrepancy as disc
    from score_channels_fixed import reaction_flags
    t = pq.read_table(stg, columns=["entry", "subentry", "pointer", "target_z", "target_a", "target_id", "mt", "sf",
                                     "reaction", "energy_ev", "original", "renormalized"])
    idx = disc.index_table(t)
    keys = idx.dataset_key.tolist()
    groups = dict(zip(keys, idx.group_key.tolist()))
    rx = dict(zip(keys, t["reaction"].to_pylist()))
    sf9 = dict(zip(keys, [(x or "").upper() for x in t["sf"].combine_chunks().field("sf9").to_pylist()]))
    # a valid original for D5 is a measurement: not a V-entry compilation, not SF9 CALC / EVAL (auto-excluded anyway)
    not_meas = {k for k in keys if k.startswith("V") or sf9[k] in ("CALC", "EVAL")}
    lines, audit = [], {}
    hand = {f"{h['entry']}/{h['subentry']}/{h['pointer']}": h for h in HAND}
    for k in keys:
        fl = reaction_flags(rx[k], k.split("/")[0])
        combo = [f for f in fl if f in COMBO_EXCLUDE]
        audit[k] = {"reaction_flags": fl}
        if combo and k not in hand:
            lines.append(line(k, "exclude", f"CAPSET-v2 D3: REACTION {rx[k]!r} is a combination ({', '.join(combo)}) of "
                              "different targets, processes or weighted states, not one capture cross section; it was filed "
                              "under its first component. Flags of score_channels_fixed.reaction_flags: " + ", ".join(fl),
                              "D3_SUM_REACTION"))
    for k, h in hand.items():
        if k in groups:
            lines.append(line(k, h["decision"], "CAPSET-v2 D6: " + h["reason"], "D6_HAND_SLIP", REVIEWER_HAND,
                              **({"factor": h["factor"]} if "factor" in h else {})))
    excluded = {l["entry"] + "/" + l["subentry"] + "/" + l["pointer"] for l in lines} | gone
    lines36, lines = lines, []
    # D5: SPSDD / DEP references to a dataset of the same comparable quantity
    by_sub = collections.defaultdict(list)
    for k in keys:
        by_sub[k.split("/")[1]].append(k)
    by_entry = collections.defaultdict(list)
    for k in keys:
        by_entry[k.split("/")[0]].append(k)
    cand = {}
    for k in keys:
        sub = k.split("/")[1]
        if k in not_meas:  # a compilation / calculated dataset is excluded by the automatic layer already
            continue
        for flag, ref in info["status"].get(sub, {}).get("refs", []):
            targets = by_sub.get(ref, []) if len(ref) == 8 else by_entry.get(ref, [])
            same = [q for q in targets if q != k and groups[q] and groups[q] == groups[k] and q not in excluded
                    and q not in not_meas]
            if same:
                cand.setdefault(k, (flag, ref, same))
    dropped = set()
    for k in sorted(cand):
        flag, ref, same = cand[k]
        if all(q in dropped for q in same):  # mutual reference: never drop both members
            audit[k]["d5_skipped"] = "every referenced dataset is itself dropped (mutual reference)"
            continue
        if k in prior_keys:
            audit[k]["d5_skipped"] = "an earlier human review line decides this dataset"
            continue
        if k in hand:
            continue
        dropped.add(k)
        cross = ref[:5] != k.split("/")[0]
        what = ("superseded by" if flag == "SPSDD" else "dependent on (derived from)")
        lines.append(line(k, "exclude", f"CAPSET-v2 D5: EXFOR STATUS ({flag},{ref}): this dataset is {what} "
                          f"{', '.join(same)}, which is in the set with the same comparable quantity ({groups[k]}); counting "
                          f"both counts one measurement twice{' (cross-entry pair)' if cross else ''}. The referenced "
                          "dataset carries the measurement.", "D5_SPSDD" if flag == "SPSDD" else "D5_DEP",
                          superseded_by=same[0], cross_entry=cross))
    for k in keys:
        audit[k]["group_key"] = groups[k]
    return lines36, lines, audit


def prelm_lines(info: dict, q1, prior_keys: set[str], decided: set[str]) -> list[dict]:
    out = []
    for r in q1.select("dataset_key", "subentry", "decision").iter_rows(named=True):
        k = r["dataset_key"]
        if k.startswith("STD2017") or k in prior_keys or k in decided:
            continue
        if info["status"].get(r["subentry"], {}).get("prelm") and r["decision"] in ("keep", "downweight"):
            out.append(line(k, "downweight", "CAPSET-v2 D5: EXFOR STATUS PRELM (preliminary data, not the final published "
                            "result). Rule: preliminary data are down-weighted (trust x0.25) wherever the automatic layer "
                            f"kept or down-weighted them (pass-1 decision: {r['decision']}).", "D5_PRELM"))
    return out


def write_jsonl(path: Path, lines: list[dict], header: str):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(header)
        for l in lines:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------------------------------------- 3. curation


def run_qm(stg: Path, work: Path, hd: Path, fit_excluded: set[str], peelle: set[str], name: str):
    """quality_model.run with the consensus fit (i) leaving out fit_excluded datasets and (ii) re-basing the uncertainty
    of absolute-unit datasets (peelle) on the expected value exp(mu + bias) of a first fit."""
    import numpy as np, polars as pl
    from data.curate import discrepancy as disc
    from data.curate import quality_model as qm
    orig = disc.fit_scatter_model
    pstat = collections.Counter()

    def fit(cells, cfg=None):
        cells = cells.filter(~pl.col("dataset_key").is_in(sorted(fit_excluded)))
        f1 = orig(cells, cfg)
        if not peelle:
            return f1
        # expected value of the cell = consensus x the dataset's own normalisation, exp(mu + bias) (d'Agostini / Peelle)
        b = f1.cells.select("dataset_key", "bin", (pl.col("mu") + pl.col("bias")).alias("_mu")).unique(["dataset_key", "bin"])
        c = cells.join(b, on=["dataset_key", "bin"], how="left", maintain_order="left")
        absu = c["dataset_key"].is_in(sorted(peelle)).to_numpy()
        mu = c["_mu"].to_numpy()
        ok = absu & np.isfinite(mu) & (c["mean_b"].to_numpy() > 0)
        fac = np.where(ok, np.clip(c["mean_b"].to_numpy() / np.exp(np.where(ok, mu, 0.0)), 1 / PEELLE_CLIP, PEELLE_CLIP), 1.0)
        pstat["cells_rebased"] = int(ok.sum())
        pstat["cells_abs_units"] = int(absu.sum())
        pstat["median_abs_log_factor_x1000"] = int(1000 * float(np.median(np.abs(np.log(fac[ok]))))) if ok.any() else 0
        c = c.with_columns((pl.col("stat_rel") * pl.Series(fac)).alias("stat_rel"),
                           (pl.col("sys_rel") * pl.Series(fac)).alias("sys_rel")).drop("_mu")
        return orig(c, cfg)

    disc.fit_scatter_model = fit
    try:
        res = qm.run(stg, work / name, tag=TAG, verbose=True, human_decisions=hd)
    finally:
        disc.fit_scatter_model = orig
    print(f"{name}: peelle {dict(pstat)}", flush=True)
    return res, dict(pstat)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--main", type=Path, default=Path("~/nucleus").expanduser())
    ap.add_argument("--work", type=Path, default=Path("~/capv2_work").expanduser())
    ap.add_argument("--stage-only", action="store_true")
    a = ap.parse_args()
    a.work.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    setup(a.main)
    import numpy as np, polars as pl
    from data.ingest import exfor as X

    # 1. staging
    i_v1 = stage(a.main, a.work, "v1", frozenset())
    i_nf = stage(a.main, a.work, "numfix", frozenset({"numfix"}))
    i_v2 = stage(a.main, a.work, "v2", X.V2_ALL)
    stg = a.work / "stage_v2.parquet"
    chk = check_research_staging(a.main, a.work / "stage_numfix.parquet")
    print("research staging check:", {k: v for k, v in chk.items() if not isinstance(v, list)}, flush=True)
    if a.stage_only:
        return

    # 2. lines
    from data.curate import quality_model as qm
    from data.curate import review_log as rl
    light_review = INP / "review_decisions_Z1-25.jsonl"
    prior_text = qm.HUMAN_DECISIONS.read_text(encoding="utf-8").rstrip("\n") + "\n" + light_review.read_text(encoding="utf-8")
    pf = a.work / "prior_human.jsonl"
    pf.write_text(prior_text, encoding="utf-8")
    prior = rl.parse_decisions_jsonl(pf)
    lines36, lines5, audit = rule_lines(stg, i_v2, prior)
    kk = lambda ls: {f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in ls if l.get("decision") in ("exclude", "fix-unit")}
    peelle = set(i_v2["v2_log"].get("unc_abs_units", []))
    peelle = {k for k in summarize(stg) if k.split("/", 1)[1] in peelle}
    hdr = ("# CAPSET-v2 review decisions (data/curation/capture_v2/README.md), format of the research repository's\n"
           "# data/curate/review_decisions.jsonl: entry, subentry, pointer, decision, reason (EXFOR id), reviewer, date; plus\n"
           "# rule (D3/D5/D6 code of the README) and, for D5, superseded_by / cross_entry. Applied AFTER the research file and\n"
           "# data/curation/inputs/review_decisions_Z1-25.jsonl (a later line overrides). reviewer 'rule:capset-v2' = written by\n"
           "# scripts/build_capture_v2.py from the EXFOR record; 'agent:claude-opus-5.5' = checked by hand against the entry.\n")

    def hfile(name, ls):
        write_jsonl(a.work / f"{name}_lines.jsonl", ls, hdr)
        p = a.work / f"{name}_human.jsonl"
        p.write_text(prior_text + (a.work / f"{name}_lines.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
        return p

    # ladder: one fix at a time, so every decision change is attributed to the step that made it
    stage(a.main, a.work, "v2parse", X.V2_ALL - {"unc"})
    steps = [("S1_baseline", "v1", [], False), ("S2_numfix", "numfix", [], False), ("S3_parser", "v2parse", [], False),
             ("S4_uncertainty", "v2", [], False), ("S5_peelle", "v2", [], True), ("S6_sums_slips", "v2", lines36, True),
             ("S7_spsdd_dep", "v2", lines36 + lines5, True)]
    lad, pstats = {}, {}
    for name, st, ls, pe in steps:
        r, pst = run_qm(a.work / f"stage_{st}.parquet", a.work, hfile(name, ls), kk(ls), peelle if pe else set(), "q_" + name)
        lad[name] = r.quality.select("dataset_key", "target_z", "decision", "trust")
        pstats[name] = pst
    q1 = lad["S7_spsdd_dep"]
    decided = kk(lines36 + lines5) | {f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in lines36 + lines5}
    lines8 = prelm_lines(i_v2, r.quality, set(prior), decided)
    lines = lines36 + lines5 + lines8
    write_jsonl(a.work / "v2_lines.jsonl", lines, hdr)
    hd = a.work / "final_human.jsonl"
    hd.write_text(prior_text + (a.work / "v2_lines.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
    r2, p2 = run_qm(stg, a.work, hd, kk(lines), peelle, "q_final")
    lad["S8_prelm_final"] = r2.quality.select("dataset_key", "target_z", "decision", "trust")
    mine = {f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in lines}
    got = set(r2.quality.filter(pl.col("dataset_key").is_in(sorted(mine)))["dataset_key"].to_list())
    assert got == mine, f"CAPSET-v2 lines without a dataset: {sorted(mine - got)[:10]}"

    # S9: CAPSET-v2.1 = v2 + D8 centre-of-mass energies + D9/D10 hand lines (energy-unit fixes applied at staging)
    i_v21 = stage(a.main, a.work, "v21", X.V21_ALL, ENERGY_FIX)
    stg21 = a.work / "stage_v21.parquet"
    keys21 = set(summarize(stg21))
    lines21 = []
    for h in HAND21:
        k = f"{h['entry']}/{h['subentry']}/{h['pointer']}"
        assert k in keys21, f"CAPSET-v2.1 line without a dataset: {k}"
        l = {"entry": h["entry"], "subentry": h["subentry"], "pointer": h["pointer"]}
        if "decision" in h:
            l["decision"] = h["decision"]
        l.update({x: h[x] for x in ("factor", "superseded_by", "energy_fix") if x in h})
        l.update({"rule": h["rule"], "reason": f"CAPSET-v2.1 {h['rule'].split('_')[0]}: " + h["reason"],
                  "reviewer": REVIEWER_HAND, "date": DATE21, "version": "2.1"})
        lines21.append(l)
    hdr21 = hdr + ("# CAPSET-v2.1 (2026-11-07): the lines with \"version\": \"2.1\" (rules D9_DUPLICATE, D10_UNIT_SLIP,\n"
                   "# D10_ENERGY_UNIT) are applied after the v2 lines. A line with \"energy_fix\" and no decision is an energy-unit\n"
                   "# correction applied at staging (energy x factor); it is not passed to the decision reader.\n")
    hd21 = a.work / "final_human_v21.jsonl"
    write_jsonl(a.work / "v21_lines.jsonl", [l for l in lines21 if "decision" in l], "")
    hd21.write_text(hd.read_text(encoding="utf-8") + (a.work / "v21_lines.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
    peelle21 = set(i_v21["v2_log"].get("unc_abs_units", []))
    peelle21 = {k for k in keys21 if k.split("/", 1)[1] in peelle21}
    r3, p3 = run_qm(stg21, a.work, hd21, kk(lines + lines21), peelle21, "q_v21")
    q = r3.quality
    lad["S9_v21"] = q.select("dataset_key", "target_z", "decision", "trust")
    mine21 = {f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in lines21}
    got = set(q.filter(pl.col("dataset_key").is_in(sorted(mine | mine21)))["dataset_key"].to_list())
    assert got == mine | mine21, f"CAPSET-v2.1 lines without a dataset: {sorted((mine | mine21) - got)[:10]}"

    # S10: CAPSET-v2.2 = v2.1 + the D11 hand lines (same staging)
    lines22 = []
    for h in HAND22:
        k = f"{h['entry']}/{h['subentry']}/{h['pointer']}"
        assert k in keys21, f"CAPSET-v2.2 line without a dataset: {k}"
        lines22.append({"entry": h["entry"], "subentry": h["subentry"], "pointer": h["pointer"], "decision": h["decision"],
                        "rule": h["rule"], "reason": f"CAPSET-v2.2 {h['rule'].split('_')[0]}: " + h["reason"],
                        "reviewer": REVIEWER_HAND, "date": DATE22, "version": VERSION})
    hdr22 = hdr21 + ("# CAPSET-v2.2 (2026-11-07): the lines with \"version\": \"2.2\" (rule D11_TOTAL_XS: a total cross section\n"
                     "# compiled as capture) are applied after the v2.1 lines.\n")
    write_jsonl(OUT / "review_decisions_capture_v2.jsonl", lines + lines21 + lines22, hdr22)
    write_jsonl(a.work / "v22_lines.jsonl", lines22, "")
    hd22 = a.work / "final_human_v22.jsonl"
    hd22.write_text(hd21.read_text(encoding="utf-8") + (a.work / "v22_lines.jsonl").read_text(encoding="utf-8"), encoding="utf-8")
    r21 = r3
    r3, p3 = run_qm(stg21, a.work, hd22, kk(lines + lines21 + lines22), peelle21, "q_v22")
    q = r3.quality
    lad["S10_v22"] = q.select("dataset_key", "target_z", "decision", "trust")
    mine22 = {f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in lines22}
    got = set(q.filter(pl.col("dataset_key").is_in(sorted(mine | mine21 | mine22)))["dataset_key"].to_list())
    assert got == mine | mine21 | mine22, f"CAPSET-v2.2 lines without a dataset: {sorted((mine | mine21 | mine22) - got)[:10]}"

    # 3. tables with the shipped schemas
    from data.curate.discrepancy import cells_from_parquet, split_group_key
    ship_t = pl.read_parquet(INP / "exfor_capture_Z26-92_trust.parquet")
    ship_c = pl.read_parquet(INP / "exfor_cells.parquet")
    q = q.select(ship_t.columns).cast(ship_t.schema)
    q21 = r21.quality.select(ship_t.columns).cast(ship_t.schema)
    cells = cells_from_parquet(stg21, verbose=False)
    parts = [split_group_key(k) for k in cells["group_key"].to_list()]
    cells = cells.with_columns(
        nuclide=pl.Series([p[0] for p in parts], dtype=pl.Utf8), mt=pl.Series([p[1] for p in parts], dtype=pl.Int32),
        branch=pl.Series([p[2] for p in parts], dtype=pl.Utf8), kind=pl.Series([p[3] for p in parts], dtype=pl.Utf8),
        state=pl.Series([p[4] for p in parts], dtype=pl.Utf8)).rename({"y": "ln_mean"})
    cells = cells.join(q.select("dataset_key", "trust", "inflation", "year", "decision", "usable"), on="dataset_key", how="left")
    cells = cells.select(ship_c.columns).cast(ship_c.schema)
    cells = cells.join(q.select("dataset_key", "target_z"), on="dataset_key", how="left")
    for lab, lo, hi in (("Z26-92", 26, 200), ("Z1-25", 1, 25)):
        q.filter(pl.col("target_z").is_between(lo, hi)).write_parquet(OUT / f"exfor_capture_{lab}_trust_v2.parquet")
        cells.filter(pl.col("target_z").is_between(lo, hi)).drop("target_z").write_parquet(OUT / f"exfor_cells_{lab}_v2.parquet")

    # 4. counts and audit
    q8 = r2.quality.select(ship_t.columns).cast(ship_t.schema)
    cells8 = cells_from_parquet(stg, verbose=False).select("dataset_key").join(q8.select("dataset_key", "decision"),
                                                                                on="dataset_key", how="left")
    cells21 = cells.select("dataset_key").join(q21.select("dataset_key", "decision"), on="dataset_key", how="left")
    counts = report(a, i_v1, i_nf, i_v2, chk, lines, audit, q, cells.drop("target_z"), lad, pstats, p3, r3, i_v21, lines21,
                    q8, cells8, lines22, q21, cells21)
    (OUT / "counts_v2.json").write_text(json.dumps(counts, indent=1, default=str) + "\n")
    prov = {
        "product": "CAPSET-v2.2 curated EXFOR capture set, Z 1-92 (data/curation/capture_v2)",
        "version": VERSION,
        "built": time.strftime("%Y-%m-%d %H:%M"),
        "script": "scripts/build_capture_v2.py",
        "public_commit_base": (subprocess.run(["git", "-C", str(REPO), "log", "-1", "--format=%H"], capture_output=True, text=True).stdout.strip()
                               or os.environ.get("CAPSET_BASE", "")),  # a Windows worktree is not readable by WSL git
        "research_commit": subprocess.run(["git", "-C", str(a.main), "log", "-1", "--format=%H"], capture_output=True, text=True).stdout.strip(),
        "curation_code": "research data/curate/quality_model.py + review_log.py (unchanged) with this repository's "
                         "data/curate/discrepancy.py (unchanged) and data/ingest/exfor.py (V2_FIXES = all six for S1-S8; "
                         "V21_ALL = the six + encm, and the ENERGY_FIX of the D10 lines, for the v2.1 and v2.2 tables; v2.2 = v2.1 + "
                         "the D11 lines on the same staging)",
        "entry_zip": {"path": f"raw/exfor/{ZIPNAME}", "sha256": sha(a.main / "raw" / "exfor" / ZIPNAME), "exfor_version": i_v2["exfor_version"]},
        "staging_v2": {"sha256": sha(stg), "rows": counts["staging"]["v2"], "where": "work directory, not shipped (rebuilt by this script)"},
        "staging_v21": {"sha256": sha(stg21), "rows": counts["staging"]["v21"], "fixes": sorted(X.V21_ALL),
                        "energy_fix": ENERGY_FIX, "where": "work directory, not shipped (rebuilt by this script)"},
        "human_decision_files": {"research data/curate/review_decisions.jsonl": sha(qm.HUMAN_DECISIONS),
                                 "data/curation/inputs/review_decisions_Z1-25.jsonl": sha(light_review),
                                 "data/curation/capture_v2/review_decisions_capture_v2.jsonl": sha(OUT / "review_decisions_capture_v2.jsonl")},
        "fit": {"left_out_of_consensus_fit": len(kk(lines + lines21 + lines22)), "peelle_rebased_datasets": len(peelle21),
                "peelle_final": p3, "peelle_clip": PEELLE_CLIP, "summary": {k: r3.summary.get(k) for k in ("fit", "n_cells", "n_datasets")}},
        "gates": {k: v.get("pass") for k, v in r3.gates.items()},
        "research_staging_check": {k: v for k, v in chk.items() if not isinstance(v, list)},
        "shipped_v1": {n: sha(INP / n) for n in ("exfor_capture_Z26-92_trust.parquet", "exfor_cells.parquet",
                                                  "exfor_capture_Z1-25_trust.parquet", "exfor_cells_Z1-25.parquet")},
    }
    (OUT / "provenance.json").write_text(json.dumps(prov, indent=1, default=str) + "\n")
    names = sorted(p.name for p in OUT.iterdir() if p.is_file() and p.name != "SHA256SUMS" and not p.name.endswith(".md"))
    (OUT / "SHA256SUMS").write_text("".join(f"{sha(OUT / n)}  {n}\n" for n in names))
    print(json.dumps({k: counts[k] for k in ("summary", "ladder")}, indent=1, default=str))


def changed_mask(cur, prev):
    """Datasets whose decision differs between two ladder steps: a different decision, or present in one step only.
    Absent in both (null == null) is not a change (polars' null != null is null, and null | False stays null)."""
    return (cur != prev).fill_null(False) | (cur.is_null() != prev.is_null())


def changed_count(cur, prev) -> int:
    return int(changed_mask(cur, prev).sum())


def report(a, i_v1, i_nf, i_v2, chk, lines, audit, q, cells, lad, pstats, p2, r2, i_v21, lines21, q8, cells8,
           lines22, q21, cells21) -> dict:
    """Before/after counts per defect, the decision ladder (ladder_v2.csv) and the change table (changes_v1_v2.csv)."""
    import polars as pl
    w = a.work
    s1, sn, s2 = summarize(w / "stage_v1.parquet"), summarize(w / "stage_numfix.parquet"), summarize(w / "stage_v2.parquet")
    s21 = summarize(w / "stage_v21.parquet")
    pts = lambda d, ks: sum(d[k][1] for k in ks if k in d)
    zsplit = lambda ks, d: {"Z26-92": sum(1 for k in ks if d[k][0] >= 26), "Z1-25": sum(1 for k in ks if d[k][0] <= 25)}
    # D1 numfix: v1-mode staging vs numfix-only staging
    new_nf = set(sn) - set(s1)
    more_nf = {k for k in set(sn) & set(s1) if sn[k][1:4] != s1[k][1:4]}

    def d1(sel):
        n = {k for k in new_nf if sel(sn[k][0])}
        m = {k for k in more_nf if sel(sn[k][0])}
        return {"datasets_recovered": len(n), "datasets_with_more_points_or_uncertainties": len(m),
                "points_recovered": pts(sn, n) + sum(sn[k][1] - s1[k][1] for k in m),
                "uncertainty_values_recovered": sum(sn[k][2] + sn[k][3] for k in n) + sum((sn[k][2] + sn[k][3]) - (s1[k][2] + s1[k][3]) for k in m)}
    D1 = {"Z26-92": d1(lambda z: z >= 26), "Z1-25": d1(lambda z: z <= 25), "examples": sorted(new_nf)[:15],
          "in_shipped_v1_Z26-92_trust": None}
    log = i_v2["v2_log"]
    lg = lambda f: {k for k in s2 if k.split("/", 1)[1] in set(log.get(f, []))}
    D2 = {f: {"datasets": len(lg(f)), "by_Z": zsplit(lg(f), s2), "new_in_capture_set": len(lg(f) - set(sn)),
              "points": pts(s2, lg(f)), "keys": sorted(lg(f))} for f in ("ratio", "enminapx", "ktdegc", "eqroute")}
    D4 = {"datasets_by_uncertainty_mode": {m[4:]: len(lg(m)) for m in sorted(log) if m.startswith("unc:")},
          "abs_unit_datasets_peelle": len(lg("unc_abs_units")), "peelle_final": p2}
    byrule = collections.Counter(l["rule"] for l in lines)
    d5x = [l for l in lines if l["rule"] in ("D5_SPSDD", "D5_DEP")]
    final = dict(zip(q["dataset_key"].to_list(), q["decision"].to_list()))
    orphan = [f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in d5x if final.get(l["superseded_by"]) in ("exclude", "fix-unit")]
    D5 = {"SPSDD_excluded": byrule["D5_SPSDD"], "DEP_excluded": byrule["D5_DEP"],
          "cross_entry": sum(1 for l in d5x if l.get("cross_entry")), "PRELM_downweighted": byrule["D5_PRELM"],
          "already_excluded_by_an_earlier_human_line": sum(1 for v in audit.values() if v.get("d5_skipped", "").startswith("an earlier")),
          "mutual_references_kept": sum(1 for v in audit.values() if v.get("d5_skipped", "").startswith("every")),
          "referenced_dataset_excluded_in_final": orphan}
    D3 = {"excluded": byrule["D3_SUM_REACTION"],
          "keys": sorted(f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in lines if l["rule"] == "D3_SUM_REACTION")}
    D6 = {l["subentry"]: {"line": l["decision"], "final": final.get(f"{l['entry']}/{l['subentry']}/{l['pointer']}")}
          for l in lines if l["rule"] == "D6_HAND_SLIP"}
    # CAPSET-v2.1
    s8 = dict(zip(lad["S8_prelm_final"]["dataset_key"].to_list(), lad["S8_prelm_final"]["decision"].to_list()))
    s9 = dict(zip(lad["S9_v21"]["dataset_key"].to_list(), lad["S9_v21"]["decision"].to_list()))
    cm = {k for k in s21 if k.split("/", 1)[1] in set(i_v21["v2_log"].get("encm", []))}
    D8 = {"datasets": len(cm), "points": pts(s21, cm), "by_Z": zsplit(cm, s21),
          "points_by_Z": {"Z26-92": pts(s21, {k for k in cm if s21[k][0] >= 26}), "Z1-25": pts(s21, {k for k in cm if s21[k][0] <= 25})},
          "decisions_v21": dict(collections.Counter(s9.get(k) for k in cm)),
          "decision_changed_v2_to_v21": sorted(k for k in cm if s8.get(k) != s9.get(k)),
          "keys": sorted(cm)}
    D9_10 = {f"{l['entry']}/{l['subentry']}/{l['pointer']}": {"rule": l["rule"], "line": l.get("decision") or "energy_fix",
                                                               "v2": s8.get(f"{l['entry']}/{l['subentry']}/{l['pointer']}"),
                                                               "v21": s9.get(f"{l['entry']}/{l['subentry']}/{l['pointer']}"),
                                                               "v22": final.get(f"{l['entry']}/{l['subentry']}/{l['pointer']}")}
             for l in lines21}
    k22 = {f"{l['entry']}/{l['subentry']}/{l['pointer']}" for l in lines22}
    D11 = {"lines": {k: {"rule": "D11_TOTAL_XS", "line": "exclude", "v21": s9.get(k), "v22": final.get(k)} for k in sorted(k22)}}
    # v1 shipped vs v2
    real = lambda t: t.filter(~pl.col("dataset_key").str.starts_with("STD2017"))
    v1t = pl.concat([pl.read_parquet(INP / "exfor_capture_Z26-92_trust.parquet"), pl.read_parquet(INP / "exfor_capture_Z1-25_trust.parquet")])
    v1c = pl.concat([pl.read_parquet(INP / "exfor_cells.parquet"), pl.read_parquet(INP / "exfor_cells_Z1-25.parquet")])
    D1["in_shipped_v1_Z26-92_trust"] = len(new_nf & set(v1t["dataset_key"].to_list()))
    # ladder
    lt = real(v1t).select("dataset_key", "target_z", pl.col("decision").alias("S0_shipped_v1"))
    for name, t in lad.items():
        lt = lt.join(real(t).select("dataset_key", pl.col("target_z").alias("_z"), pl.col("decision").alias(name)),
                     on="dataset_key", how="full", coalesce=True).with_columns(pl.coalesce("target_z", "_z").alias("target_z")).drop("_z")
    rule_of = {f"{l['entry']}/{l['subentry']}/{l['pointer']}": l["rule"] for l in lines}
    lt = lt.with_columns(pl.col("dataset_key").replace_strict(rule_of, default=None).alias("capset_v2_rule")).sort("dataset_key")
    lt.write_csv(OUT / "ladder_v2.csv")
    cols = ["S0_shipped_v1"] + list(lad)
    ladder = {}
    for lab, lo, hi in (("Z26-92", 26, 200), ("Z1-25", 1, 25)):
        x = lt.filter(pl.col("target_z").is_between(lo, hi))
        ladder[lab] = []
        for i, c in enumerate(cols):
            row = {"step": c, **{d: int((x[c] == d).sum()) for d in ("keep", "downweight", "exclude", "fix-unit")},
                   "datasets": int(x[c].is_not_null().sum())}
            if i:
                p = cols[i - 1]
                row["changed_vs_previous"] = changed_count(x[c], x[p])
            ladder[lab].append(row)
    trans = {}
    for lab, lo, hi in (("Z26-92", 26, 200), ("Z1-25", 1, 25)):
        x = lt.filter(pl.col("target_z").is_between(lo, hi))
        trans[lab] = {f"{r['S0_shipped_v1']}->{r['S10_v22']}": r["len"]
                      for r in x.group_by("S0_shipped_v1", "S10_v22").len().sort("len", descending=True).iter_rows(named=True)}
        trans[lab + "_v2_to_v21"] = {f"{r['S8_prelm_final']}->{r['S9_v21']}": r["len"]
                                     for r in x.filter(pl.col("S8_prelm_final") != pl.col("S9_v21"))
                                     .group_by("S8_prelm_final", "S9_v21").len().sort("len", descending=True).iter_rows(named=True)}
        ch = x.filter(changed_mask(x["S10_v22"], x["S9_v21"]))
        trans[lab + "_v21_to_v22"] = {f"{r['S9_v21']}->{r['S10_v22']}": r["len"]
                                      for r in ch.group_by("S9_v21", "S10_v22").len().sort("len", descending=True).iter_rows(named=True)}
        auto = ch.filter(~pl.col("dataset_key").is_in(sorted(k22)))
        D11[lab] = {"changed_v21_to_v22": ch.height,
                    "by_review_lines": ch.height - auto.height,
                    "by_automatic_relearning": auto.height,
                    "relearning_transitions": {f"{r['S9_v21']}->{r['S10_v22']}": r["len"] for r in
                                               auto.group_by("S9_v21", "S10_v22").len().sort("len", descending=True)
                                               .iter_rows(named=True)}}

    def side(t, c, lo, hi):
        t = real(t).filter(pl.col("target_z").is_between(lo, hi))
        c = c.filter(pl.col("dataset_key").is_in(t["dataset_key"].to_list()))
        return {"datasets": t.height, "points": int(t["n_points"].sum()), "cells": c.height,
                "decisions": dict(sorted(collections.Counter(t["decision"].to_list()).items())),
                "cells_by_decision": dict(sorted(collections.Counter(c["decision"].to_list()).items()))}
    summ = {lab: {"v1": side(v1t, v1c, lo, hi), "v2": side(q8, cells8, lo, hi), "v2.1": side(q21, cells21, lo, hi),
                  "v2.2": side(q, cells, lo, hi)}
            for lab, lo, hi in (("Z26-92", 26, 200), ("Z1-25", 1, 25))}
    return {"version": VERSION, "summary": summ, "ladder": ladder, "transitions_v1_to_v2": trans, "D1_numfix": D1,
            "D2_parser": D2, "D3_sums": D3, "D4_uncertainty": D4, "D5_duplicates": D5, "D6_slips": D6,
            "D8_centre_of_mass_energy": D8, "D9_D10_v21_lines": D9_10, "D11_v22_lines": D11,
            "D7_version": {"v1_parser_staged": i_v1["exfor_version"], "v2_staged": i_v2["exfor_version"]},
            "staging": {"v1_mode": len(s1), "numfix_only": len(sn), "v2": len(s2), "v21": len(s21)}, "research_staging_check": chk,
            "gates_final": {k: v.get("pass") for k, v in r2.gates.items()}, "peelle_by_step": pstats,
            "d5_skips": {k: v["d5_skipped"] for k, v in audit.items() if "d5_skipped" in v}}


if __name__ == "__main__":
    main()
