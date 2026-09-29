# Inputs Incognita does not redistribute, and how to get them

`scripts/reproduce.sh` regenerates tables from these inputs. It never downloads a library or EXFOR by itself unless you
pass `--download` (and even then only the EXFOR master file and RIPL-4). Every location is an
environment variable (`incognita/config.py`):

| variable | default | holds |
|---|---|---|
| `INCOGNITA_MAIN` | the repository root | the one data directory every tool uses: `data/ingest/download.py` writes `raw/`, the EXFOR ingest writes `staging/`; `curated/` and `features/` copies there win over the shipped `data/curation/inputs/` |
| `INCOGNITA_EVALUATED` | `$INCOGNITA_MAIN/staging/evaluated` | staged evaluated-library grids |
| `INCOGNITA_INPUTS` | `~/incognita-inputs` | the other inputs below |
| `INCOGNITA_WORK` | `out/reproduce` | everything the reproduce script writes |
| `TALYS_DIR` | `~/opt/talys-src` | the TALYS source tree (only `structure/` is read) |

## 1. EXFOR (IAEA Nuclear Data Section and the NRDC network)

Measurements. We score against them; we do not redistribute them.

```bash
uv run python data/ingest/download.py --only exfor_entry_current      # -> $INCOGNITA_MAIN/raw/exfor/entry.zip
                                                                       #    (https://nds.iaea.org/nrdc/exfor-master/entry/entry.zip)
uv run python -m data.ingest.exfor --subset all                        # -> staging/exfor_all.parquet
for s in capture n2n np na; do uv run python -m data.ingest.exfor --subset $s --zmin 26 --zmax 92; done
                                                                       # -> staging/exfor_<s>_Z26-92.parquet
```

The registry scorers (`scripts/registry/`) fetch `entry.zip` themselves. The EXFOR master changes daily, so staged
tables built later than ours hold more (and occasionally corrected) entries.

## 2. Evaluated libraries (from their official distributions)

| library | source | key |
|---|---|---|
| ENDF/B-VIII.1 | NNDC, https://www.nndc.bnl.gov/endf-releases/ | `endfb81` |
| JENDL-5 | JAEA, https://wwwndc.jaea.go.jp/jendl/j5/j5.html | `jendl5` |
| TENDL-2025 | PSI / IAEA-NDS mirror, https://tendl.web.psi.ch/ | `tendl2025` |
| JEFF-4.0, JEFF-3.3 | OECD-NEA, https://www.oecd-nea.org/dbdata/jeff/ (JEFF-4.0 via the IAEA-NDS mirror) | `jeff40`, `jeff33` |
| BROND-3.1, FENDL-3.2c, IRDFF-II | IAEA-NDS, https://www-nds.iaea.org/public/download-endf/ | `brond31`, `fendl32`, `irdff2` |
| CENDL-3.2 | CNDC via IAEA-NDS | `cendl32` |

```bash
uv run python data/ingest/download.py --only endfb81_endf6 jendl5_n tendl2025_n jeff40_n jeff33_n brond31_n fendl32_n cendl32_n irdff2_n
uv run python -m data.ingest.build_evaluated --library all --subset all --workers 3    # needs NJOY2016 (RECONR)
```

`build_evaluated` reconstructs each file's pointwise cross sections with NJOY2016 RECONR (`INCOGNITA_NJOY` points at the
executable; `conda install -c conda-forge njoy2016`) and writes `<key>.parquet` on a 3000-point grid, 1e-5 eV to 20 MeV.
Known issue: 12 curves are staged as zero by a bug in this builder; a fix is pending. Staged libraries are used only
as scoring baselines.

## 3. The channel-track exam rows (EXFOR-derived)

`$INCOGNITA_INPUTS/exam_rows/{na,n2n,np,capture,sacs}_rows.parquet` + `SHA256SUMS`: the measured points of the channel tracks (12,460 differential points and 417 spectrum-averaged records), i.e. EXFOR values selected,
renormalised and binned by our curation. Columns: Z, A, series (EXFOR entry/subentry), e_ev, the value (data_mb; capture
data_b), year, and for (n,a) the kind (total or He production). No library values.

These rows fed a development-stage evaluation that is not part of v0.1. The rows themselves ship in
`incognita/bench/data/exam_rows/` (with SHA256SUMS) because the benchmark's channel tracks use them.

## 4. TALYS structure database (for the engine)

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/arjankoning1/talys ~/opt/talys-src
(cd ~/opt/talys-src && git sparse-checkout set structure)       # 8.6 GB
export TALYS_DIR=~/opt/talys-src
```

## 5. Benchmarks and library files

- Speed (stock TALYS for the comparison): `incognita/bench/speed/README.md`, `docs/talys-install.md`.
- ENDF-6 library files: not part of v0.1.
