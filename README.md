# Incognita

**Open, calibrated predictions of neutron reaction cross sections across the chart of nuclides, with a public blind
benchmark and a registry of predictions made before the data.**

[![Code: Apache-2.0](https://img.shields.io/badge/code-Apache--2.0-blue)](LICENSE)
[![Data: CC-BY-4.0](https://img.shields.io/badge/data-CC--BY--4.0-lightgrey)](LICENSE-DATA)
[![Status: v0.1 preview](https://img.shields.io/badge/status-v0.1%20preview-orange)](#status-and-limitations)
[![Engine: 2026-10-22](https://img.shields.io/badge/engine-2026--10--22-informational)](docs/GUIDE.md#engine-versions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](pyproject.toml)

<a href="https://www.incognitanuclear.org/?lang=en"><img src="docs/walkthrough/og.png" alt="Inside a Nuclear Reaction: an explorable explanation of the Incognita reaction engine" width="100%"></a>

## At a glance

- **Website: [www.incognitanuclear.org](https://www.incognitanuclear.org/?lang=en).**
  [Inside a Nuclear Reaction](https://www.incognitanuclear.org/?lang=en) is a teaching walkthrough of what the engine
  computes; [Every nuclide](https://www.incognitanuclear.org/data?lang=en) shows the predicted curves for 6,168 nuclides
  beside every curated measurement; the [Scoreboard](https://www.incognitanuclear.org/scoreboard?lang=en) compares the
  engine with other reaction codes, losses first.
- **Scoreboard result** (development comparisons against existing measurements, not a blind test): against the
  TALYS-2.24 program, 10 wins, 9 ties, 0 losses; against all rivals together, 47 wins, 19 ties, 0 losses in 66 decided
  comparisons (14 more are not applicable).
- **Data package:** [`docs/walkthrough/data/board/`](docs/walkthrough/data/board/) holds the per-nucleus rows behind
  every scoreboard cell, and [`recompute.py`](docs/walkthrough/data/board/recompute.py) recomputes the verdicts from them.
- **Prediction registry:** [`predictions/2026-10-23/`](predictions/2026-10-23/) holds predictions registered on
  2026-10-23 for measurements not yet published, with a fixed scoring rule; 16 of the targets are blind and decide the
  headline verdict.
- **Engine:** release tag [`engine-2026-10-22`](https://github.com/seth-michael-weaver/incognita/tree/engine-2026-10-22).
- **Library:** [`library/v0.1/`](library/v0.1/) is the current release; v0.2 is in preparation.
- **Citing:** [`CITATION.cff`](CITATION.cff) (see [Citing](#citing)).

## What is this

Most nuclei have never had a neutron cross section measured, yet reactors, nucleosynthesis networks, fusion shielding
and isotope production all need values for them. Incognita gives each nuclide **a value**, **an uncertainty interval**
whose coverage has been tested on nuclei held out of the fit, and **a regime label** (measured, anchored, interpolated
or extrapolated). The code, the predictions, the exam they were graded on and timestamped predictions for nuclei not
yet measured are all public, so every claim can be checked.

## Highlights

| | |
|---|---|
| **Coverage** | 6,168 nuclides (Z = 8–110), 1 keV – 20 MeV: capture, MACS, stellar rates, (n,p), (n,2n), (n,α) |
| **Held-out capture** | with measured D0, beats the default TALYS recipe on the sealed vault: 0.1519 vs 0.1712 dex |
| **Tested intervals** | 95 % interval covers 95.3 % of 674 sealed capture bins published after 2012 |
| **Engine** | a Python/C port of TALYS-2 physics; matches stock TALYS to four decimals on total, elastic, (n,p), (n,α) scores; 11.7x faster per target (no cache) |

Ties and losses are reported too: see the [full benchmark](docs/GUIDE.md#benchmark).

## Quick start

Needs Linux or macOS, Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/seth-michael-weaver/incognita.git incognita && cd incognita
uv sync --extra dev
uv run python -m incognita.library show Au-197    # capture curve with 68 / 95 % bands, MACS at 30 keV
bash scripts/reproduce.sh                         # regenerate the benchmark tables and compare with the shipped ones
```

Running the engine itself needs the TALYS structure database: see [Running the engine](docs/GUIDE.md#running-the-engine).

## What is in the repo

| path | content |
|---|---|
| [`library/v0.1/`](library/v0.1/) | the predictions (CC-BY-4.0) |
| [`incognita/`](incognita/) | library reader, benchmark scorer and tracks, calibration and curation tools |
| [`physics/`](physics/) | the Hauser–Feshbach engine |
| [`scripts/`](scripts/) | `reproduce.sh`, scorers, engine driver, native-kernel builds |
| [`docs/release/`](docs/release/), [`docs/registry/`](docs/registry/) | frozen exam inputs and expected tables; pre-registered predictions |
| [`predictions/`](predictions/) | dated prediction registries (blind targets, fixed scoring rule) |
| [`emu/`](emu/) | fast emulators of the engine |
| [`docs/walkthrough/`](docs/walkthrough/) | the explainer website |

The full layout is in the [guide](docs/GUIDE.md#repository-layout).

## Status and limitations

This is a **v0.1 preview**: research output, not an evaluation. Held-out tests are retrospective; the pre-registered
predictions have not yet been scored against new measurements. There is no claim of better accuracy than evaluated
libraries for measured nuclei; where good data exist, use the data or an evaluation. The library and its benchmark
numbers come from the v0.1 engine; the scoreboard uses the current engine (22 October 2026). Details: [Status and limitations](docs/GUIDE.md#status-and-limitations).

## Learn more

- [Using the library](docs/GUIDE.md#using-the-library): format, regime tiers
- [Running the engine](docs/GUIDE.md#running-the-engine) and [engine versions](docs/GUIDE.md#engine-versions)
- [Method](docs/GUIDE.md#method): physics, global rules, independence from evaluated libraries, curation
- [Benchmark](docs/GUIDE.md#benchmark), [performance](docs/GUIDE.md#performance) and
  [reproducing the numbers](docs/GUIDE.md#reproducing-the-numbers)
- [Prospective registry](docs/GUIDE.md#prospective-registry)
- [Acknowledgements](docs/GUIDE.md#acknowledgements)

## Emulator

Millisecond emulators of the engine, with Jacobians and sampling: [`emu/README.md`](emu/README.md).

## Citing

Use [`CITATION.cff`](CITATION.cff), and also cite EXFOR (N. Otuka et al., Nucl. Data Sheets 120 (2014) 272) and
TALYS (A. Koning, S. Hilaire, S. Goriely, Eur. Phys. J. A 59 (2023) 131) when you use the engine or the EXFOR-derived
tables.

## Licence

Code: Apache-2.0 ([`LICENSE`](LICENSE), [`NOTICE`](NOTICE)); predictions and data: CC-BY-4.0
([`LICENSE-DATA`](LICENSE-DATA), including third-party terms); ported TALYS routines keep their MIT notice
([`physics/hf/NOTICE-TALYS.md`](physics/hf/NOTICE-TALYS.md)).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md). If a number here is wrong,
please open an issue with the measurement.
