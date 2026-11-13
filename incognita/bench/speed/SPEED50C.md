# SPEED50C: port vs stock TALYS, fused GPU batch (2026-09-23)

**Result: the port is 15.3x faster than stock TALYS (CPU) on a cold batch with the opt-in fused GPU kernel, 21.5x warm,
5.1x for one nuclide per fresh process. 50x is not reached and is not close.** All numbers come from one benchmark
session (20 nuclides x 20 energies, one pinned core, ABAB order):

- **Batch, cold, fused GPU kernel:** 13.5x (previous code, 1260ac1c) → **15.3x CPU / 13.1x wall** (this release).
- **Batch, warm (CC cache, so CC ≈ 0):** 19.8x → **21.5x**.
- **Single nuclide, cold, fused:** **5.1x**.

50x would need **4.7 CPU-s** at this session's TALYS time (235.8 CPU-s). The best arm is at **11.0 CPU-s warm** and
**15.4 CPU-s cold fused**.

## Limits and caveats

- What remains is ~20 flat stages (table below) plus imports, each 0.3-2 CPU-s; most of them already are C kernels
  called through ctypes (`ce_cascade`, `nx_widths`, `grid_coefficients`, the DWBA and OMP kernels).
- **The benchmark machine's speed drifts by 15-50 % between runs, even at load < 2.** Only same-session ABAB ratios
  are claims. Within the bench they were stable: 15.59 / 15.21 CPU-s for this release's repeats, 17.45 / 17.44 for
  1260ac1c's.
- Changes that did not help (measured, not kept): `-O3 -march=native -ffp-contract=fast` builds of the native
  libraries (inside the noise, not portable); running the worker inline instead of a spawned child; keeping
  `solver._CHANNELS` across targets on the CPU-only cold path.
- Imports cost ~1.2-1.6 CPU-s per process, ~0.8-1.0 of it `import torch` itself; the physics imports cost ~0.1 s.
- The cold GPU arms were timed on one machine only; the accuracy of the fused path was checked on a second machine
  with an RTX 3050.

## 1. Benchmark (`incognita/bench/speed/bench.py`, core 15, 2 repeats ABAB, every arm in one session)

1-min load median 1.4, max 1.9 (< 4). TALYS took 235.8 CPU-s in this session; compare ratios only within this table.

- Raw data: `results/speed50c_raw.jsonl`; report: `results/speed50c_REPORT.md` (regenerate it with
  `python incognita/bench/speed/bench.py report results --raw results/speed50c_raw.jsonl --dest out/REPORT.md`).
- The **b50b** arms are commit 1260ac1c, run from a sparse `git worktree` of that commit (`--repo b50b=PATH`), for a
  same-session before/after.

| Arm | CPU-s | wall-s | TALYS / CPU | TALYS / wall |
|---|---|---|---|---|
| Stock TALYS, sum of 20 per-nuclide processes | **235.8** | | 1 | |
| (B) base cold (c423b78d), per nuclide (sum) | 55.7 | | 4.24x | |
| (B) new cold, CPU only, per nuclide (sum) | 51.0 | | 4.63x | |
| (B) new cold + fused GPU, per nuclide (sum) | 46.3 | | **5.10x** | |
| (B) new WARM, per nuclide (sum) | 38.4 | | 6.15x | |
| (A) base batch, cold (c423b78d) | 26.0 | 27.4 | 9.06x | 8.60x |
| (A) new batch, CPU only, cold | 24.7 | 26.4 | 9.55x | 8.93x |
| (A) new batch + torch CCGPU, cold | 21.2 | 23.6 | 11.13x | 9.99x |
| (A) **previous batch + fused, cold** (1260ac1c) | 17.4 | 19.2 | 13.52x | 12.25x |
| (A) **this release, batch + fused, cold** | **15.4** | **18.0** | **15.31x** | **13.07x** |
| (A) previous batch WARM (1260ac1c) | 11.9 | 13.2 | 19.82x | 17.86x |
| (A) **this release, batch WARM** | **11.0** | **11.1** | **21.50x** | **21.26x** |

The cold CPU-only and per-nuclide arms barely move: the changes target the fused GPU path, GC and the channel/OMP reuse.

## 2. Profile per stage, before → after

py-spy at 250 Hz, all threads, on the batch work (`engine_curves._worker` in one process), core 15, back to back in
one session. Each sample goes to the deepest matching stage marker; one run per column; py-spy adds ~10 % and counts
on-CPU samples only.

| Stage (CPU-s over 20 nuclides) | warm 1260ac1c | warm this release | cold fused 1260ac1c | cold fused this release |
|---|---|---|---|---|
| **launcher thread (ccgpu)** | 0 | 0 | **5.90** | **0.98** |
| cascade C (`ce_cascade`, incl. nx_widths) | 1.73 | 1.73 | 2.00 | 1.78 |
| imports | 1.22 | 1.55 | 1.24 | 1.61 |
| cascade callback spec/add (per-nucleus LD, levels) | 1.25 | 1.06 | 1.25 | 1.02 |
| CC solve on the CPU (C matching, prefill) | 0 | 0 | 1.14 | 0.82 |
| cascade callback fission (C `grid_coefficients`, ladder) | 0.92 | 1.04 | 0.93 | 0.78 |
| ccgpu other (lookup keys, host(), device()) | 0 | 0 | 0.83 | 1.02 |
| OMP parameters (RIPL tables) | 0.31 | 0.36 | 0.80 | 0.58 |
| DWBA | 0.54 | 0.54 | 0.73 | 0.57 |
| cascade callback psf (gamma parameters) | 0.60 | 0.67 | 0.66 | 0.50 |
| `front` (C `nx_target` + glue) | 0.52 | 0.47 | 0.66 | 0.56 |
| `ccgpu.plan` (the plan pass's own set-up) | 0 | 0 | 0.21 | 0.64 |
| inverse transmissions (C `_run_job`) | 0.56 | 0.44 | 0.64 | 0.59 |
| `cases` other, `shell` | 1.18 | 1.12 | 1.24 | 1.06 |
| `drop_target_caches` (gc) | 0.37 | **0.12** | 0.46 | **0.13** |
| pre-equilibrium (prepare + exciton) | 0.61 | 0.72 | 0.77 | 0.59 |
| CC disk store / load | 0.12 | 0.19 | 0.21 | 0.11 |
| all the rest (≤ 0.2 each) | ~1.0 | ~0.9 | ~1.4 | ~1.2 |
| **total sampled** | **11.1** | **11.2** | **21.6** | **14.9** |

- **Cold fused path.** The gain is almost entirely the launcher thread, 5.9 → 1.0 CPU-s. Part of the plan's set-up
  (channel sets, RIPL OMP) used to be repeated in the run; it now happens once, in `plan`, so the plan's row grows
  while the solve and OMP rows shrink.
- **Warm path.** GC went 0.37 → 0.12; the other rows are within single-run noise (±0.1-0.3 s).
- **Where the time goes (native py-spy, warm):** CPython interpreter 24 %, libc/libm 22 %, our C kernels 18 %, torch
  C++ 17 % (mostly `import torch`), numpy 12 %. A C port of the remaining Python glue would remove at most the
  interpreter share plus some of the numpy and torch share.

## 3. What changed (from 1260ac1c; in this repository's history)

| Commit | Change | Effect |
|---|---|---|
| 9493e19e | **CCFUSED host→device copies through pinned memory, non-blocking.** A pageable H2D copy syncs the stream first, so each side's input copies (and the `inv` permutation after the launch) waited behind the previous kernel on that stream. Under WSL that wait *spins*: measured 2.4 CPU-s and 4.8 s wall in the one `inv.to(dev)` alone. The fix also covers the worker GC (`gc.freeze()` after every `drop_target_caches`, gen0 threshold 50000) and drops the fsync from `ccdisk.store` (atomic `os.replace` kept; a torn file is rejected by `load`'s key check). | largest single gain |
| 686db265 | The pair order is restored on the host in `_Side.host()` (no device `index_select` after the launch). The deformed derivative weights `WW` are memoised per nmax. | Launcher ~1.2 → ~0.9 CPU-s |
| a712f1cf + dabe6969 | `ccgpu.plan` keeps **every** channel set the target touches for `restore`, not just the ones it built. An earlier target with the same band (U-238 before Sm-154) had built them, so the run rebuilt 264 of 558 sets after the drop; the run now builds 0. It is implemented by wrapping `solver._channels_cached` during the plan. `solver.py` stays unchanged because it is one of the sources that key the CC disk cache's version: touching it invalidated every existing cache. | ~0.3-0.5 CPU-s cold fused |
| b7938ab9 | `ripl._full_table` joins `chartrun.KEEP` (pure, from files). With CCGPU, both the plan pass and the run built it. | ~0.2 CPU-s cold fused on actinides |

- Every CCGPU/CCFUSED change stays behind `HF_CCGPU=1 HF_CCGPU_FUSED=1`.
- The default path changes only by the GC schedule, the missing fsync and one more KEEP entry, which are value-identical (see §4).

## 4. Accuracy (median ≤ 1e-6, worst ≤ 1e-4 on every array `engine_curves` writes, vs c423b78d)

The fused runs used an RTX 3050 and ≤ 4 cores.

| Run | Commit | Nuclides | Cells | Median | Worst | Missing | Verdict |
|---|---|---|---|---|---|---|---|
| fused | dabe6969 (final) | 20 bench | 32,913 | 0 | 6.7e-13 | 0 | PASS |
| fused | dabe6969 (final) | 100 sample | 162,343 | 0 | 6.4e-12 | 0 | PASS |
| default (CPU) | a712f1cf | 20 bench | 32,913 | 0 | 4.3e-16 | 0 | PASS |
| default (CPU) | a712f1cf | 100 sample | 162,343 | 0 | 1.4e-16 | 0 | PASS |
| warm, bench machine | dabe6969 | 20 bench | 32,913 | 0 | 4.3e-16 | 0 | PASS |

The default-path runs are at a712f1cf. After it, the only default-path code change is b7938ab9 (one more pure KEEP
cache); dabe6969 touches only the CCGPU plan, and its fused and warm runs pass.

## 5. What would be needed for more

- **The ceiling for anything that leaves the per-target physics in Python is the warm arm, ~21-22x.** The cold fused
  arm sits ~4.4 CPU-s above warm: CC plan and set-up ~1.5, CPU matching and prefill ~0.8, lookup/host()/keys ~1.0,
  the launcher thread ~1.0.
- **50x (≤ 4.7 CPU-s) would need all of:** the per-target set-up and per-energy Python layer in C (~20 stages at
  0.3-1.3 s each); the cascade callbacks folded into `ce_cascade`; no torch import (~0.8-1.0 s per process); the GPU
  device time (~5 s) hidden entirely, which caps wall near 45x. That is a rewrite of the engine's driver layer; an
  estimate from the stage table is that a thorough C port of the glue lands around 30x warm.
- **Remaining improvements, in order of yield:**
  1. Move the three cascade callbacks (`spec`/`add`, `fis_cb`, `psf_cb`, ~2.3 CPU-s) to C-side per-target tables built once.
  2. Share the plan pass's level-density, OMP and gamma set-up with the run, ~1 CPU-s cold.
  3. Replace the per-block blake2 value hashing in `ccgpu.lookup` with identity keys, ~0.3 CPU-s.

## Files

- Commits 9493e19e, 686db265, a712f1cf, b7938ab9, dabe6969 (in this repository's history).
- `incognita/bench/speed/bench.py`: the bench; `results/`: the session's raw data and report.
- The profiler and the accuracy-check scripts are not shipped; their results are the tables above.
