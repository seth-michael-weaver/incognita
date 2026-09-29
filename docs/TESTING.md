# Testing Incognita from the outside

This page is for people who want to check our claims, score their own evaluation on our benchmark, or register
predictions before the measurements exist. Everything below runs from a fresh clone.

Install first (see the README's Quick start): `uv sync --extra dev`, `make native`, and the TALYS structure database
(`TALYS_DIR`). Run every command with `uv run python ...` (stock systems have no bare `python`, and the system `python3` lacks
the dependencies).

- **Disk and time.** The environment (`uv sync`, CPU-only PyTorch on Linux) takes about 1.5 GB. The TALYS structure
  database, needed only to run the engine, is a separate multi-gigabyte sparse clone (`docs/talys-install.md`). For a GPU
  build of PyTorch, install it into the environment yourself; the GPU kernels are optional.
- **Native kernels.** `make native` needs `make` and a C compiler (gcc). Without them the engine still runs, in pure Python,
  about 4x slower, and prints a warning. Under clang (tested with zig cc) `libhfnative` fails to link (`__cpu_model`); the
  other kernels build. `make native` builds every kernel it can and lists the ones that failed.
- **Data directory.** Every tool reads and writes one data directory, `$INCOGNITA_MAIN`, which defaults to the repository
  root: `data/ingest/download.py` writes `raw/`, the EXFOR ingest writes `staging/`. Set `INCOGNITA_MAIN` to put them elsewhere.
- **A healthy test run.** `uv run pytest`: 0 failed. Tests that need external data (TALYS structure database, EXFOR,
  RIPL), the compiled kernels or a GPU are skipped with the reason (`uv run pytest -ra` lists them).

## 1. Check our published numbers

```bash
bash scripts/reproduce.sh                        # every step whose inputs are present; the rest SKIPPED with the reason
bash scripts/reproduce.sh capblind retro         # only these steps
bash scripts/reproduce.sh --download             # also fetch what can be fetched (EXFOR master, benchmark repo)
bash scripts/reproduce.sh --with-engine terra    # also run the TALYS port (~3 CPU-minutes)
```

Output goes to `$INCOGNITA_WORK` (default `out/reproduce`). `SUMMARY.md` lists every step as IDENTICAL, DIFFERS (with
the diff) or SKIPPED (what's missing and how to get it). For each README claim, its status (regenerated, reported but
not reproducible, or retracted) is in [`docs/release/REPRODUCE.md`](release/REPRODUCE.md). Inputs we don't
redistribute, and how to fetch them, are in [`docs/release/INPUTS.md`](release/INPUTS.md).

## 2. Score any evaluation on the open benchmark

```bash
uv run python -m incognita.bench.score tracks --track all                  # verify the frozen tracks (sha256 pins)
uv run python -m incognita.bench.score score --track capture-heldout \
       --csv my_predictions.csv --name MyModel                      # score a CSV of predictions
uv run python -m incognita.bench.score score --track all --endf DIR --njoy /path/to/njoy   # score ENDF-6/PENDF files
uv run python -m incognita.bench.score leaderboard --out my_leaderboard    # the frozen entries + your staged libraries, 95 % CIs
# (the leaderboard has no --csv yet: score your own CSV with `score`, which prints it against the track's reference entry)
uv run python -m incognita.bench.score export --track capture-heldout --out rows.csv       # the rows, to predict yourself
```

- The tracks, with manifests and data cards, are in `incognita/bench/tracks/`. The guide and current leaderboard are
  [`docs/release/BENCHMARK.md`](release/BENCHMARK.md).
- Metric: the rms of log10(prediction / measurement), in dex, with paired differences on the rows both entries cover.
- We ship no evaluated-library values. To put ENDF/B, JENDL, TENDL and the others on the dated tracks, fetch them from
  their official sites and bin-average them on the data's energy bins:
  `uv run python -m incognita.bench.place_dated …`, which uses the rule in `incognita/bench/binavg.py` (NJOY RECONR). Then pass
  `--dated-library` (or `$INCOGNITA_DATED_LIBRARY`). Comparing pointwise library resonances with bin-averaged data
  below 100 keV gives meaningless numbers, so always use this placement.

## 3. Test anyone's uncertainties

```bash
uv run python -m incognita.uq.calibration_report TABLE.parquet --by tier --out report.md   # any table with err + h68/h95
uv run python -m incognita.uq.calibration_report --preset tiers    [--exam DIR]            # our published tier coverage
uv run python -m incognita.uq.calibration_report --preset nostruct [--exam DIR]
```

It reports coverage at 68/95 % with nucleus-bootstrap CIs, the PIT histogram, ECE and sharpness, by stratum. The
evidence behind our uncertainty claims, including where they fail, is in
[`docs/release/UQ_EVIDENCE.md`](release/UQ_EVIDENCE.md).

## 4. Register a prediction before the measurement exists

We keep hash-chained, timestamped registries of predictions made before the data. You can submit yours the same way:
see [`docs/registry/SUBMIT.md`](registry/SUBMIT.md). Registry manifests carry OpenTimestamps proofs next to them
(`*.ots`; verify with `ots verify`).

## 5. Rebuild the data judgement yourself

```bash
bash scripts/reproduce.sh --download curation   # fetches the EXFOR master and RIPL-4, stages capture, rebuilds and compares
# or by hand:
uv run python data/ingest/download.py --only exfor_entry_current ripl4      # -> $INCOGNITA_MAIN/raw/ (~380 MB + RIPL-4)
uv run python -m data.ingest.exfor --subset capture --zmin 26 --zmax 92      # -> $INCOGNITA_MAIN/staging/ (~1.5 min)
uv run python -m incognita.curation.build --out DIR                          # the register; compare DIR with data/curation/
```

- The two curated EXFOR tables the register starts from ship in `data/curation/inputs/` (EXFOR-derived, CC BY 4.0, hashed).
- The curation rule and its reason codes are in [`docs/release/CURATION_RULE_v2.md`](release/CURATION_RULE_v2.md) and
  [`CURATION_REGISTER.md`](release/CURATION_REGISTER.md). No library value enters it.
- The automatic EXFOR-rebuild pipeline (predictions frozen before new data are ingested) is not in this release yet.

## What we'd most like tested

- Whether the capture uncertainties stay calibrated on data we have never seen. Our claim is narrow: pooled over two
  sealed tests, the 68 % interval covers at or above nominal (conservative, not sharp); the 95 % interval is not reliably
  calibrated (88 % on the shipped model's own sealed read).
- Any benchmark row where our placement of a library looks wrong.
- Curation decisions you disagree with: open an issue quoting the EXFOR entry and the rule code.

Where we already know we lose (libraries on data they fitted, BRUSLIB on MACS, JENDL-5 on (n,α) after 2021, the
resolved-resonance region, (n,p) for unmeasured nuclei) is listed in the README and BENCHMARK.md. Please don't
spend your time rediscovering those; tell us about the ones we haven't found.
