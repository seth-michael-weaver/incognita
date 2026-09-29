# Benchmark harnesses

| folder | what | regenerates from shipped files | re-run needs |
|---|---|---|---|
| `speed/` | port vs stock TALYS timing | the SPEED50C report (from raw timings) | stock TALYS, idle machine |
| `criticality/` | ICSBEP k-eff, phases 1 and 2 | results / decomposition / TEST / TRAIN tables (from our k-eff) | mit-crpg/benchmarks, ENDF libraries, NJOY, OpenMC |
| `shielding/` | OKTAVIAN leakage, FNG foils, section-swap diagnosis | OKTAVIAN / FNG / diagnosis tables (from our tallies) | openmc_fusion_benchmarks @ c47fc57 (also for re-scoring), ENDF libraries, NJOY, OpenMC |

Each folder's README lists what to download and the exact commands. `SHA256SUMS` covers every shipped result file
(`sha256sum -c SHA256SUMS` from this folder).
