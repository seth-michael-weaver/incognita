#!/usr/bin/env python3
"""TALYS reference dumps for the Python port: run TALYS at defaults with every diagnostic on.

The port (`physics/hf/`) is tested component by component against what TALYS itself computed
for the same nucleus and energy -- transmission coefficients, level densities, strength
functions, first-chance populations, exclusive channels -- not only against final cross
sections, so a disagreement can be traced to one routine. This module produces those dumps.

    # on a compute box (stdlib only; TALYS_DIR must point at the install root)
    python3 physics/hf/talys_reference.py run --out ~/hf_reference/raw --workers 3 \\
        --shard 0 --nshards 2
    # back on the laptop (numpy + pandas + pyarrow)
    uv run python -m physics.hf.talys_reference parse --raw features/hf_reference/raw \\
        --out features/hf_reference
    uv run python -m physics.hf.talys_reference check --out features/hf_reference

Three rules, each learned from a TALYS run that exited 0 and was wrong:

1. **Defaults means keyword absent.** Pinning `ldmodel 1`, the documented default, collapsed
   U-238 (n,f) 17x (docs/results/wp24-fission-ldmodel-trap.md). The input therefore contains
   the projectile, target, energy file and *output* keywords only. Physics keywords appear only
   in a named variant (`wfc_off`), and the variant says so.
2. **Energies ascend strictly** or TALYS truncates silently at the first descent. `ENERGIES_MEV`
   is checked at import.
3. **Output flags must not move the physics.** The `minimal` variant reruns a subset with only
   the four keywords the production sweeps use; `check` requires every cross section in the
   full-output run to match it. A dump whose diagnostics changed its own answer is not a
   reference.

Population files are written but not kept. `outdecay y` forces population output on
(`if (flagdecay) flagpop = .true.`, checkvalue.f90:1164) and so does `outbasic y`
(input_output.f90:115); `outpopulation n` does not win against either. Population output is
also the only switch under which TALYS writes `levels*.out` and `ld*.gs` for the *residual*
nuclei (multiple.f90:333-338), which A-struct and A-ld need, so it stays on -- but
`populationE*.out` is ~5 GB of text per run at 23 energies (Ca-40: 516 MB at 14 MeV alone), so
`run_one` deletes it before archiving. The first-chance population per (Ex bin, J, parity) is
kept in `binE*.out`; the on-demand `population` variant keeps the multi-chance files at two
energies for the compound/multiple-emission component.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------------------------
# The reference set
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Target:
    symbol: str
    Z: int
    A: int
    shape: str  # "spherical" | "deformed" | "actinide"
    note: str

    @property
    def tag(self) -> str:
        return f"{self.symbol}{self.A:03d}"


# 24 targets, A 40-241. `spherical` targets define the 5% end-to-end gate; `deformed` rare
# earths go through TALYS's spherical OMP + DWBA collective levels by default; `actinide`
# targets default to RIPL OMP 2408 with ECIS coupled channels (input_omppar.f90:181-188) and
# to `fission y` (A > fislim), so their gate is deferred until the ECIS task lands.
REFERENCE_SET: tuple[Target, ...] = (
    Target("Ca", 20, 40, "spherical", "doubly magic, lightest"),
    Target("Fe", 26, 56, "spherical", "structural, even-even"),
    Target("Co", 27, 59, "spherical", "odd Z, target spin 7/2"),
    Target("Ni", 28, 58, "spherical", "Z=28, (n,p) strong"),
    Target("Zr", 40, 90, "spherical", "N=50"),
    Target("Nb", 41, 93, "spherical", "odd Z, spin 9/2, dosimetry"),
    Target("Mo", 42, 98, "spherical", "mid-shell even"),
    Target("Sn", 50, 120, "spherical", "Z=50"),
    Target("I", 53, 127, "spherical", "odd Z, spin 5/2"),
    Target("Ba", 56, 138, "spherical", "N=82"),
    Target("Ce", 58, 140, "spherical", "N=82"),
    Target("Au", 79, 197, "spherical", "capture standard, odd"),
    Target("Pb", 82, 208, "spherical", "doubly magic, WFC outlier in widthmode scan"),
    Target("Bi", 83, 209, "spherical", "odd, next to Pb-208"),
    Target("Nd", 60, 150, "deformed", "transitional"),
    Target("Sm", 62, 152, "deformed", "onset of deformation"),
    Target("Gd", 64, 157, "deformed", "odd, largest capture in the widthmode scan"),
    Target("Er", 68, 166, "deformed", "well deformed"),
    Target("W", 74, 184, "deformed", "structural, deformed"),
    Target("Th", 90, 232, "actinide", "fertile, CC OMP"),
    Target("U", 92, 235, "actinide", "fissile, odd"),
    Target("U", 92, 238, "actinide", "fertile, fission standard"),
    Target("Pu", 94, 239, "actinide", "fissile, odd"),
    Target("Am", 95, 241, "actinide", "odd, edge of the RIPL-2408 range"),
)

# Incident neutron energies, MeV. Dense below 1 MeV where capture and compound elastic live,
# through every (n,2n)/(n,np) threshold region up to 20 MeV where pre-equilibrium dominates.
ENERGIES_MEV: tuple[float, ...] = (
    1.0e-3,
    2.0e-3,
    5.0e-3,
    1.0e-2,
    2.3e-2,
    5.0e-2,
    0.1,
    0.2,
    0.5,
    1.0,
    1.5,
    2.0,
    3.0,
    4.0,
    5.0,
    6.0,
    8.0,
    10.0,
    12.0,
    14.0,
    16.0,
    18.0,
    20.0,
)
assert all(b > a for a, b in zip(ENERGIES_MEV, ENERGIES_MEV[1:])), (  # noqa: B905 (py3.9 boxes)
    "TALYS truncates on descent"
)

# Output-only keywords. Every one was verified to exist as a keyword in the TALYS-2.x source
# (grep "key == '<name>'" source/*.f90) and none selects a model. `filediscrete` is absent on
# purpose: it takes a level number, and `filediscrete y` stops TALYS with "Error in value" (the
# .L files are written anyway).
OUTPUT_KEYWORDS: dict[str, str] = {
    "channels": "y",
    "filechannels": "y",
    "filetotal": "y",
    "fileelastic": "y",
    "fileresidual": "y",
    "filepsf": "y",
    "filedensity": "y",
    "outbasic": "y",
    "outtransenergy": "y",
    "outdensity": "y",
    "outgamma": "y",
    "outlevels": "y",
    "outomp": "y",
    "outinverse": "y",
    "outdiscrete": "y",
    "outdecay": "y",
    "outpreequilibrium": "y",
    "outdirect": "y",
}
# Fission output keywords are FATAL below A=151 ("TALYS-error: Fission not allowed for A <= 150",
# no output files written, exit code 0), so they are added for heavy targets only.
FISSION_OUTPUT_KEYWORDS: dict[str, str] = {"filefission": "y", "outfission": "y"}
# What the production sweeps write (physics/talys/runner.py DEFAULT_KEYWORDS); the invariance
# check compares against this.
MINIMAL_KEYWORDS: dict[str, str] = {
    "channels": "y",
    "filechannels": "y",
    "filetotal": "y",
    "fileelastic": "y",
    "outbasic": "n",
}

VARIANTS: dict[str, dict] = {
    # TALYS at its defaults, everything written.
    "default": {"keywords": {}, "output": OUTPUT_KEYWORDS, "targets": "all"},
    # Width fluctuation correction off: isolates `compound` from `widthfluc`/`moldauer`.
    # widthmode 0 = no WFC (input_compoundmodel.f90:148). A null, not a physics model.
    "wfc_off": {"keywords": {"widthmode": "0"}, "output": OUTPUT_KEYWORDS, "targets": "all"},
    # Flag invariance: production keywords only, on a subset spanning every shape class.
    "minimal": {
        "keywords": {},
        "output": MINIMAL_KEYWORDS,
        "targets": ("Fe056", "Zr090", "Au197", "Gd157", "Pb208", "U238"),
    },
    # On demand only (~100-500 MB of text per run): multi-chance populations per (Ex, J, pi).
    "population": {
        "keywords": {},
        "output": {**OUTPUT_KEYWORDS, "outpopulation": "y"},
        "keep_population": True,
        "targets": ("Fe056", "Sn120", "Au197"),
        "energies": (1.0, 5.0),
        "on_demand": True,
    },
}


def jobs(variants: list[str]) -> list[tuple[str, Target]]:
    out = []
    for v in variants:
        spec = VARIANTS[v]
        for t in REFERENCE_SET:
            if spec["targets"] == "all" or t.tag in spec["targets"]:
                out.append((v, t))
    return out


def input_text(variant: str, t: Target) -> tuple[str, str]:
    """(talys.inp, energies file) for one job. Physics keywords come only from the variant."""
    spec = VARIANTS[variant]
    energies = spec.get("energies", ENERGIES_MEV)
    lines = ["projectile n", f"element {t.symbol.lower()}", f"mass {t.A}", "energy energies"]
    lines += [f"{k} {v}" for k, v in spec["keywords"].items()]
    output = dict(spec["output"])
    if spec["output"] is not MINIMAL_KEYWORDS and t.A > 150:
        output.update(FISSION_OUTPUT_KEYWORDS)
    lines += [f"{k} {v}" for k, v in output.items()]
    return "\n".join(lines) + "\n", "".join(f"{e:.6E}\n" for e in energies)


# ---------------------------------------------------------------------------------------------
# run (stdlib only)
# ---------------------------------------------------------------------------------------------


def _talys_bin() -> Path:
    if os.environ.get("TALYS_BIN"):
        return Path(os.environ["TALYS_BIN"])
    return Path(os.environ.get("TALYS_DIR", Path.home() / "opt/talys-src")) / "bin" / "talys"


def run_one(variant: str, t: Target, out: Path, timeout: float) -> dict:
    tar = out / f"{variant}__{t.tag}.tar.gz"
    if tar.exists():
        return {"job": tar.name, "status": "exists"}
    wd = out / "_work" / f"{variant}__{t.tag}"
    shutil.rmtree(wd, ignore_errors=True)
    wd.mkdir(parents=True)
    inp, en = input_text(variant, t)
    (wd / "talys.inp").write_text(inp)
    (wd / "energies").write_text(en)
    env = dict(os.environ)
    env.setdefault("TALYS_DIR", str(_talys_bin().resolve().parent.parent))
    t0 = time.time()
    with open(wd / "talys.inp") as fin, open(wd / "talys.out", "w") as fout:
        try:
            rc = subprocess.run(
                [str(_talys_bin())],
                stdin=fin,
                stdout=fout,
                stderr=subprocess.STDOUT,
                cwd=wd,
                env=env,
                timeout=timeout,
            ).returncode
        except subprocess.TimeoutExpired:
            rc = "timeout"
    elapsed = time.time() - t0
    text = (wd / "talys.out").read_text(errors="replace")
    ok = rc == 0 and "The TALYS team congratulates" in text
    fatal = [
        ln
        for i, ln in enumerate(text.splitlines())
        if "TALYS-error" in ln and not any("Continuing" in w for w in text.splitlines()[i : i + 6])
    ]
    manifest = {
        "variant": variant,
        "target": t.tag,
        "Z": t.Z,
        "A": t.A,
        "shape": t.shape,
        "returncode": rc,
        "completed_banner": "The TALYS team congratulates" in text,
        "fatal_errors": fatal[:5],
        "elapsed_s": round(elapsed, 1),
        "host": os.uname().nodename,
        "talys_bin": str(_talys_bin()),
        "talys_bin_sha256": hashlib.sha256(_talys_bin().read_bytes()).hexdigest()[:16],
        "input": inp,
        "n_files": len(list(wd.iterdir())),
    }
    if not VARIANTS[variant].get("keep_population"):
        dropped = sorted(wd.glob("population*.out"))
        manifest["deleted_population_bytes"] = sum(p.stat().st_size for p in dropped)
        for p in dropped:
            p.unlink()
    (wd / "manifest.json").write_text(json.dumps(manifest, indent=1))
    status = "ok" if ok and not fatal else "failed"
    tmp = tar.with_suffix(".partial")
    with tarfile.open(tmp, "w:gz") as tf:
        tf.add(wd, arcname=f"{variant}__{t.tag}")
    tmp.rename(tar if status == "ok" else out / f"FAILED__{variant}__{t.tag}.tar.gz")
    shutil.rmtree(wd, ignore_errors=True)
    return {"job": tar.name, "status": status, "elapsed_s": manifest["elapsed_s"]}


def cmd_run(a) -> None:
    out = Path(a.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    names = a.variants.split(",")
    for v in names:
        if VARIANTS[v].get("on_demand") and not a.include_on_demand:
            sys.exit(f"variant {v!r} is on demand; pass --include-on-demand")
    todo = jobs(names)
    todo = sorted(todo, key=lambda j: (j[1].shape == "actinide", j[1].A))  # slow ones last
    todo = todo[a.shard :: a.nshards]
    if a.only:
        wanted = set(a.only.split(","))
        todo = [(v, t) for v, t in jobs(names) if f"{v}__{t.tag}" in wanted]
    print(f"{len(todo)} jobs on {os.uname().nodename}, {a.workers} workers -> {out}", flush=True)
    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(run_one, v, t, out, a.timeout) for v, t in todo]
        for f in as_completed(futs):
            print(json.dumps(f.result()), flush=True)
    print("done", flush=True)


# ---------------------------------------------------------------------------------------------
# parse (numpy, pandas, pyarrow)
# ---------------------------------------------------------------------------------------------

# file family -> glob inside a run directory. Each family becomes one long-format parquet.
FAMILIES: dict[str, str] = {
    "xs_channels": "xs*.tot",  # exclusive channels (xsNNNNNN.tot)
    "xs_totals": "*.tot",  # total/elastic/nonelastic/reaction/ng.tot/... (filtered below)
    "xs_levels": "*.L[0-9][0-9]",  # partial cross sections to discrete levels
    "xs_continuum": "*.con",
    "transmission": "transmission_*.out",
    "inverse_xs": "cross_*.tot",
    "omp_parameters": "omppar_*.out",
    "omp_potential": "omp.out",
    "level_density": "ld*.gs",
    "levels": "levels*.out",
    "discrete_gamma": "gamma[0-9]*.tot",
    "psf": "psf*",
    "binary_population": "binE*.out",
    "direct": "directE*.out",
    "preequilibrium": "preeq*.out",
    "exciton": "exciton*.out",
    "fission": "fission*",
    "residual_production": "rp*.tot",
}
_TOTALS_EXCLUDE = (
    "xs",
    "cross_",
    "rp",
    "gamma",
    "aprod",
    "dprod",
    "gprod",
    "hprod",
    "nprod",
    "pprod",
    "tprod",
)


def _family_files(d: Path, fam: str) -> list[Path]:
    files = sorted(p for p in d.glob(FAMILIES[fam]) if p.is_file())
    if fam == "xs_totals":
        files = [p for p in files if not p.name.startswith(_TOTALS_EXCLUDE)]
    return files


def _peak_rss_gb() -> float:
    """Peak resident set size of this process, in GB (Linux VmHWM; 0.0 elsewhere)."""
    try:
        for line in Path("/proc/self/status").read_text().splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1]) / 1024**2
    except OSError:
        pass
    return 0.0


class _ParquetSink:
    """One parquet file, appended archive by archive rather than written once at the end.

    The first parse of the full 54-archive reference set held every family's long-format rows
    until the last tarball and grew by ~0.5 GB per archive; extrapolated to ~30 GB, and it is
    what ran the laptop out of memory on 2026-09-12. Here each archive is one row group, so
    peak memory is one archive whatever the set size. The files are equivalent to what the
    buffered version wrote: the string columns stay dictionary-encoded, so pandas still reads
    them back as ``category`` -- with the index width pinned to int32, because per-chunk
    inference picks int8 or int16 by cardinality and ParquetWriter demands that every row group
    share one schema.

    Rows go to ``_staging/<name>.parquet`` and are moved onto the published name only once the
    whole parse has succeeded (``publish``). Several port workers poll these parquets while this
    runs, and a ParquetWriter opens -- and so truncates -- its target immediately, so writing
    in place would hand every reader a headless, unreadable file for the whole parse, and leave
    one behind for good if the parse died. ``os.replace`` within the one directory is atomic,
    so a reader sees either the previous parse or this one.
    """

    def __init__(self, path: Path, schema) -> None:
        import pyarrow.parquet as pq

        self.path, self.schema, self.rows = path, schema, 0
        self.staging = path.parent / "_staging" / path.name
        self.staging.parent.mkdir(parents=True, exist_ok=True)
        self._writer = pq.ParquetWriter(self.staging, schema, compression="zstd")

    def write(self, df) -> None:
        import pyarrow as pa

        if df is None or len(df) == 0:
            return
        self._writer.write_table(pa.Table.from_pandas(df, preserve_index=False, schema=self.schema))
        self.rows += len(df)

    def close(self) -> None:
        self._writer.close()

    def publish(self) -> None:
        os.replace(self.staging, self.path)


def _write_atomic(df, path: Path, **kw) -> None:
    """to_parquet via _staging + rename, so pollers never see a half-written file."""
    staging = path.parent / "_staging" / path.name
    staging.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(staging, index=False, **kw)
    os.replace(staging, path)


def _schemas() -> dict:
    """Column names, order and types of the streamed parquet files (contract §6)."""
    import pyarrow as pa

    d, s, i = pa.dictionary(pa.int32(), pa.string()), pa.large_string(), pa.int64()
    return {
        # every YANDF family, long format: one row per (block, row, column)
        "long": pa.schema(
            [
                ("row", i),
                ("column", d),
                ("value", pa.float64()),
                ("unit", d),
                ("variant", d),
                ("target", d),
                ("file", d),
                ("block", i),
                ("meta", d),
            ]
        ),
        # non-numeric lines kept verbatim (branching ratios, level tables, parse errors)
        "raw_rows": pa.schema(
            [("variant", s), ("target", s), ("file", s), ("block", i), ("row", i), ("line", s)]
        ),
        "block_index": pa.schema(
            [
                ("family", s),
                ("variant", s),
                ("target", s),
                ("file", s),
                ("block", i),
                ("n_numeric_rows", i),
                ("n_raw_rows", i),
                ("columns", s),
                ("meta", s),
            ]
        ),
    }


def cmd_parse(a) -> None:
    import pandas as pd

    from physics.hf.yandf import parse_blocks

    raw = Path(a.raw)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_extract"
    schemas = _schemas()
    sinks: dict[str, _ParquetSink] = {}
    scalars: list[dict] = []
    manifests = []
    n_raw_rows = 0

    def sink(name: str, kind: str) -> _ParquetSink:
        if name not in sinks:
            sinks[name] = _ParquetSink(out / f"{name}.parquet", schemas[kind])
        return sinks[name]

    # a parse killed mid-flight (SIGKILL catches no handler) leaves staging behind
    shutil.rmtree(out / "_staging", ignore_errors=True)
    tars = [t for t in sorted(raw.glob("*.tar.gz")) if not t.name.startswith("FAILED__")]
    for n_tar, tar in enumerate(tars, 1):
        frames: dict[str, list] = {f: [] for f in FAMILIES}
        raw_rows: list[dict] = []
        # every datablock, including empty ones: TALYS writes `entries: -1` blocks with no rows
        # for closed channels (alpha on Sr-87 below the barrier), and the energy in their meta is
        # still a point of the emission grid (A-grid)
        block_index: list[dict] = []
        shutil.rmtree(tmp, ignore_errors=True)
        with tarfile.open(tar) as tf:
            tf.extractall(tmp, filter="data")
        (d,) = list(tmp.iterdir())
        man = json.loads((d / "manifest.json").read_text())
        manifests.append(man)
        for row in parse_talys_out(d / "talys.out"):
            scalars.append({"variant": man["variant"], "target": man["target"], **row})
        for fam in FAMILIES:
            for p in _family_files(d, fam):
                try:
                    blocks = parse_blocks(p)
                except Exception as exc:  # keep going, but record it
                    raw_rows.append(
                        {
                            "variant": man["variant"],
                            "target": man["target"],
                            "file": p.name,
                            "block": -1,
                            "row": -1,
                            "line": f"PARSE ERROR {exc!r}",
                        }
                    )
                    continue
                for b, blk in enumerate(blocks):
                    block_index.append(
                        {
                            "family": fam,
                            "variant": man["variant"],
                            "target": man["target"],
                            "file": p.name,
                            "block": b,
                            "n_numeric_rows": int(blk.data.shape[0]),
                            "n_raw_rows": len(blk.raw_rows),
                            "columns": json.dumps(blk.columns),
                            "meta": json.dumps(blk.meta, sort_keys=True),
                        }
                    )
                    for r, line in blk.raw_rows:
                        raw_rows.append(
                            {
                                "variant": man["variant"],
                                "target": man["target"],
                                "file": p.name,
                                "block": b,
                                "row": r,
                                "line": line,
                            }
                        )
                    if blk.data.size == 0:
                        continue
                    df = pd.DataFrame(blk.data, columns=_dedupe(blk.columns))
                    df.insert(0, "row", blk.numeric_row_index)
                    long = df.melt(id_vars="row", var_name="column", value_name="value")
                    units = dict(zip(_dedupe(blk.columns), blk.units))  # noqa: B905
                    long["unit"] = long["column"].map(units)
                    long["variant"], long["target"], long["file"], long["block"] = (
                        man["variant"],
                        man["target"],
                        p.name,
                        b,
                    )
                    long["meta"] = json.dumps(blk.meta, sort_keys=True)
                    frames[fam].append(long)
        # flush this archive: one row group per family, then let the frames go
        for fam, parts in frames.items():
            if parts:
                sink(fam, "long").write(pd.concat(parts, ignore_index=True))
        if raw_rows:
            cols = [f.name for f in schemas["raw_rows"]]
            sink("raw_rows", "raw_rows").write(pd.DataFrame(raw_rows, columns=cols))
            n_raw_rows += len(raw_rows)
        if block_index:
            cols = [f.name for f in schemas["block_index"]]
            sink("block_index", "block_index").write(pd.DataFrame(block_index, columns=cols))
        print(
            f"[{n_tar}/{len(tars)}] {tar.name}: "
            f"{sum(len(x) for v in frames.values() for x in v)} rows, "
            f"{len(block_index)} blocks, peak RSS {_peak_rss_gb():.2f} GB",
            flush=True,
        )
    shutil.rmtree(tmp, ignore_errors=True)
    written = {}
    for name, sk in sinks.items():
        sk.close()
        if name in FAMILIES:
            written[name] = sk.rows
    _write_atomic(pd.DataFrame(scalars), out / "incident_scalars.parquet")
    _write_atomic(pd.DataFrame(manifests), out / "manifest.parquet")
    # every file is complete on disk before any of them is published, so the swap window is
    # a handful of renames rather than the length of the parse
    for sk in sinks.values():
        sk.publish()
    # a family that produced nothing this run must not keep an earlier parse's file around:
    # readers would silently mix this reference set with the previous one
    stale = [f for f in FAMILIES if f not in sinks and (out / f"{f}.parquet").exists()]
    for f in stale:
        (out / f"{f}.parquet").unlink()
    shutil.rmtree(out / "_staging", ignore_errors=True)
    print(
        json.dumps(
            {
                "runs": len(manifests),
                "rows": written,
                "raw_rows": n_raw_rows,
                "stale_removed": stale,
                "peak_rss_gb": round(_peak_rss_gb(), 2),
            },
            indent=1,
        )
    )


_TALYS_OUT_SCALARS = (
    # (column name, regex on one talys.out line; group 1 = value). First match per energy block.
    ("sigma_tot_omp_mb", r"^ Total cross section\s+:\s+(\S+) mb"),
    ("sigma_reac_omp_mb", r"^ Reaction cross section:\s+(\S+) mb"),
    ("sigma_el_omp_mb", r"^ Elastic cross section :\s+(\S+) mb"),
    ("s0", r"^ S0:\s+\d+\s+(\S+) \.e-4"),
    ("s1", r"^ S1:\s+\d+\s+(\S+) \.e-4"),
    ("r_prime_fm", r"^ R :\s+\d+\s+(\S+) fm"),
    ("norm_reaction_mb", r"^ Reaction cross section\s+:\s+(\S+) \(A\)"),
    ("norm_sum_tjl_mb", r"^ Sum over T\(j,l\)\s+:\s+(\S+) \(B\)"),
    ("norm_cn_formation_mb", r"^ Compound nucleus formation c\.s\. :\s+(\S+) \(C\)"),
)


def parse_talys_out(path: Path) -> list[dict]:
    """Per-incident-energy scalars from talys.out that no YANDF file carries.

    `transmission_inc.out` is overwritten at every energy, so the incident channel's
    S0/S1/R' (printed as ``S0:  90  0.4667 .e-4`` = 0.4667e-4, stored absolute here) and the
    OMP total/reaction/elastic cross sections, plus the normalisation block (A reaction, B sum
    over T(j,l), C compound formation), exist only in talys.out.
    """
    import re

    from physics.hf.core.units import S0_PRINT_SCALE

    rows: list[dict] = []
    cur: dict | None = None
    pats = [(k, re.compile(v)) for k, v in _TALYS_OUT_SCALARS]
    for ln in Path(path).read_text(errors="replace").splitlines():
        m = re.match(r"^ ########## RESULTS FOR E=\s*(\S+) ##########", ln)
        if m:
            cur = {"e_inc_mev": float(m.group(1))}
            rows.append(cur)
            continue
        if cur is None:
            continue
        if ln.startswith(" Width fluctuations (flagwidth)") and "flagwidth" not in cur:
            cur["flagwidth"] = ln.rsplit(":", 1)[1].strip() == "y"
        for k, pat in pats:
            if k in cur:
                continue
            m = pat.match(ln)
            if m:
                v = float(m.group(1))
                cur[k] = v * S0_PRINT_SCALE if k in ("s0", "s1") else v
    return rows


def _dedupe(cols: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    out = []
    for c in cols:
        if c in seen:
            seen[c] += 1
            out.append(f"{c}#{seen[c]}")
        else:
            seen[c] = 0
            out.append(c)
    return out


def cmd_check(a) -> None:
    """Flag invariance: full-output `default` must equal production-keyword `minimal`."""
    import numpy as np
    import pandas as pd

    out = Path(a.out)
    rows = []
    for fam in ("xs_channels", "xs_totals"):
        p = out / f"{fam}.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p)
        df = df[df["variant"].isin(["default", "minimal"])]
        key = ["target", "file", "block", "row", "column"]
        wide = df.pivot_table(
            index=key, columns="variant", values="value", observed=True, aggfunc="first"
        )
        if "minimal" not in wide:
            continue
        wide = wide.dropna()
        rel = (wide["default"] - wide["minimal"]).abs() / np.maximum(
            wide[["default", "minimal"]].abs().max(axis=1), 1e-30
        )
        worst = rel.groupby(level="target").max()
        for tgt, w in worst.items():
            rows.append(
                {
                    "family": fam,
                    "target": tgt,
                    "values_compared": int((rel.index.get_level_values(0) == tgt).sum()),
                    "max_rel_diff": float(w),
                }
            )
    res = pd.DataFrame(rows)
    print(res.to_string(index=False) if len(res) else "no minimal runs parsed yet")
    bad = res[res["max_rel_diff"] > 1e-5] if len(res) else res
    (out / "flag_invariance.json").write_text(
        json.dumps(
            {"tolerance": 1e-5, "passed": bool(len(res) and bad.empty), "rows": rows}, indent=1
        )
    )
    if len(bad):
        sys.exit(f"FLAG INVARIANCE FAILED on {sorted(set(bad['target']))}")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--out", required=True)
    r.add_argument("--variants", default="default,wfc_off,minimal")
    r.add_argument("--workers", type=int, default=3)
    r.add_argument("--shard", type=int, default=0)
    r.add_argument("--nshards", type=int, default=1)
    r.add_argument("--timeout", type=float, default=4 * 3600)
    r.add_argument("--include-on-demand", action="store_true")
    r.add_argument(
        "--only", default="", help="comma list of variant__TAG jobs (overrides --shard/--nshards)"
    )
    p = sub.add_parser("parse")
    p.add_argument("--raw", default="features/hf_reference/raw")
    p.add_argument("--out", default="features/hf_reference")
    c = sub.add_parser("check")
    c.add_argument("--out", default="features/hf_reference")
    s = sub.add_parser("list")
    s.add_argument("--variants", default="default,wfc_off,minimal")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        cmd_run(a)
    elif a.cmd == "parse":
        try:
            cmd_parse(a)
        except BaseException:
            shutil.rmtree(Path(a.out) / "_staging", ignore_errors=True)
            raise
    elif a.cmd == "check":
        cmd_check(a)
    else:
        for v, t in jobs(a.variants.split(",")):
            print(v, t.tag, t.shape)


if __name__ == "__main__":
    main()
