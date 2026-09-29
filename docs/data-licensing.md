# Data sources and licensing

What each external source is used for, whether anything derived from it is distributed here, and under which terms.
The project's own data are CC BY 4.0 and its code Apache-2.0 (`LICENSE-DATA`, `LICENSE`).

| source | used for | distributed here | terms |
|---|---|---|---|
| EXFOR Master File (IAEA NDS and the NRDC network) | training targets, exam targets, curation evidence | EXFOR-derived exam cells and curation tables; not the library itself (downloaded by `data/ingest/download.py`) | CC BY 4.0 as stated by the IAEA; cite Otuka et al., Nucl. Data Sheets 120 (2014) 272 |
| RIPL-3 / RIPL-4 (IAEA) | resonance spacings D0, average radiative widths, level and level-density tables read by the engine | a few parsed parameter tables (e.g. `physics/hf/gamma/ggnorm_ripl3.csv`) | IAEA NDS terms of use: scientific reuse with acknowledgement |
| TALYS-2 code and structure database (A. Koning et al.) | the engine is a port of the code; the database is read at run time | ported code only (MIT notice kept, `physics/hf/NOTICE-TALYS.md`); the database is not redistributed | MIT |
| AME2020 / NUBASE2020 (AMDC) | masses, separation energies, half-lives | derived quantities in exam tables and the measure-next ranking | published in Chinese Physics C, cite the papers |
| ENSDF (NNDC) | discrete level information via the TALYS / RIPL tables | no | US government work |
| Compiled measured MACS values (KADoNiS) | anchoring 21 nuclides; flags of which entries are experimental | a yes/no flag table (`models/data/kadonis_keep.csv`); the 21 anchored predictions reproduce the compiled values by construction; the compiled values are not distributed as data | no licence stated by the publisher |
| Atlas of Neutron Resonances (S.F. Mughabghab) | resonance counts for the resolved-resonance bound | no values; only the derived bound energy (`resolved_upper_ev`) | book (Elsevier) |
| Evaluated libraries: ENDF/B-VIII.1, JENDL-5, JEFF-3.3/4.0, TENDL, CENDL-3.2, BROND-3.1, FENDL-3.2, IRDFF-II | scoring baselines only, from files the user downloads and stages with `data/ingest/build_evaluated.py` | no values | varies by library; several state no reuse licence |
| NON-SMOKER, BRUSLIB cross sections, ASTRAL | descriptive comparisons during development | no | varies |

Downloads are scripted in `data/ingest/download.py`; nothing under `raw/` or `staging/` is committed.

When in doubt about a third-party term, the rule applied here is: distribute only our own predictions and
EXFOR-derived tables, and give users a script to fetch anything else from its publisher.
