# Performance: the engine against stock TALYS-2

This page gives the speed of the Incognita Hauser–Feshbach engine next to stock TALYS-2.25, measured on the
same machine with the same structure database, and the agreement between the two codes on the same runs.
Everything here is produced by one script, [`scripts/bench_vs_talys.py`](../scripts/bench_vs_talys.py); the raw
record of the run quoted below is [`performance/bench-2026-09-29.json`](performance/bench-2026-09-29.json).

## Headline (measured 2026-09-29)

Twelve targets, 64 incident neutron energies each (1 keV to 20 MeV), one pinned CPU core, one thread, median
CPU-seconds of three interleaved repeats:

| | stock TALYS-2.25 | engine, no cache | engine, warm cache |
|---|---|---|---|
| CPU-s, 12 targets, per-target compute | 487.6 | 41.6 (**11.7x**) | 15.1 (**32.2x**) |
| CPU-s, 12 targets, whole process | 487.6 | 56.8 (**8.6x**) | 30.1 (**16.2x**) |

The no-cache numbers are the conservative ones. The warm-cache numbers apply only when the same coupled-channels
solutions are needed again (see [Cold and warm cache](#cold-and-warm-cache)).

On the same runs the two codes agree to a median of 1e-6 to 7e-6 in |log10(engine/TALYS)| and at worst 1.2e-3
(0.28 %) on capture; see [Parity](#parity).

## What is compared

- **Stock TALYS**: TALYS-2.25 (upstream commit `1f634cbcd`), unmodified, compiled with gfortran 16.2 and TALYS's
  own default gfortran flags (`-w -O3 -ffp-contract=off`). Input is the minimal default deck: `projectile n`,
  `element`, `mass`, `energy <file>` and `strucpath`. No dump, debug or extra output keywords are set: such
  keywords make TALYS several times slower and would inflate the ratio. TALYS's default output files already
  include the total, elastic, nonelastic and residual-production cross sections used for parity.
- **Engine**: this repository's engine, C kernels built (`make native`), default (stock TALYS) parameters, no
  fitted recipe (`INCOGNITA_TALYS_FIT` unset) and TALYS's own E1-width table. It runs the full calculation that
  `scripts/bestfit/engine_curves.py` runs per target, which includes the exclusive channels; default TALYS does not
  compute exclusive channels, so in that respect the comparison favours TALYS.
- **Structure data**: both codes read the same TALYS `structure/` directory.

## Protocol

- Each timed run is a fresh process started as `taskset -c <cpu> ...`, with `OMP_NUM_THREADS=1` and one torch
  thread. Its CPU time (user + sys) comes from `os.wait4`, so it covers everything that process did.
- For the engine two numbers are recorded: the **whole process** (Python start-up and imports, about 1.2 CPU-s,
  included) and the **per-target compute** (CPU time from building the target to having its cross sections,
  measured inside the process). A long-running worker that processes many targets pays the import once, so the
  compute figure is what a sweep pays per target; the whole-process figure is what a single one-off run pays.
  TALYS is always the whole process.
- Four arms per target: `talys`, `nocache` (cache off), `cold` (empty cache directory) and `warm` (a cache directory
  filled by one earlier, untimed run of the same target and energies).
- Repeats are interleaved: every repeat visits every target, and the arm order alternates between
  talys → nocache → cold → warm and the reverse, so slow drifts in background load hit every arm alike.
  Tables report medians over repeats.
- All arms of a given target run on the same core. The run used two streams (two cores, the targets split between
  them), never more than two benchmark processes at a time.

## Machine and load

A 16-thread x86-64 laptop (Intel Core i5-13450HX), Linux under WSL2, CPU only, Python 3.12, 24 GB of RAM visible to
Linux. The machine was **not idle**: other long-running jobs occupied about four to six logical CPUs throughout (1-minute
load average 4.9–9.0, median 5.9, sampled at the start and end of every timed run). The two benchmark cores were
chosen as the ones those jobs were least likely to use, but a sibling hyper-thread or shared cache may still have been
busy. The spread between repeats of the same (target, arm) was 13 % at the median and 45 % at worst (a 2.4–3.7 s
warm Dy-163 run); medians are used for that reason. Peak memory of any single run was 0.73 GB (TALYS).

## Results

Per target, median CPU-s. Engine columns give per-target compute / whole process.

| nuclide | class | TALYS | engine no-cache | cold cache | warm cache | speed-up no-cache | speed-up warm |
|---|---|---|---|---|---|---|---|
| Ni-58 | spherical | 6.22 | 0.79 / 2.02 | 0.79 / 2.10 | 0.79 / 2.11 | 7.9x / 3.1x | 7.9x / 2.9x |
| Zr-90 | spherical | 6.63 | 0.78 / 2.04 | 0.84 / 2.03 | 0.74 / 1.95 | 8.5x / 3.2x | 9.0x / 3.4x |
| Sn-118 | spherical | 7.08 | 0.73 / 1.86 | 0.76 / 1.96 | 0.77 / 1.97 | 9.6x / 3.8x | 9.2x / 3.6x |
| Ge-74 | vibrational | 13.97 | 1.21 / 2.40 | 1.24 / 2.40 | 0.79 / 1.94 | 11.6x / 5.8x | 17.7x / 7.2x |
| Cd-112 | vibrational | 14.38 | 1.33 / 2.57 | 1.32 / 2.48 | 0.85 / 2.00 | 10.8x / 5.6x | 16.9x / 7.2x |
| Sm-152 | rotational | 17.50 | 2.09 / 3.28 | 2.07 / 3.21 | 0.95 / 2.14 | 8.4x / 5.3x | 18.4x / 8.2x |
| Gd-157 | rotational | 45.54 | 4.38 / 5.67 | 4.33 / 5.60 | 1.10 / 2.38 | 10.4x / 8.0x | 41.6x / 19.2x |
| Dy-163 | rotational | 76.21 | 6.75 / 8.13 | 7.18 / 8.44 | 1.43 / 2.88 | 11.3x / 9.4x | 53.2x / 26.5x |
| W-184 | rotational | 46.97 | 4.10 / 5.50 | 3.92 / 5.34 | 1.02 / 2.20 | 11.5x / 8.5x | 46.3x / 21.4x |
| Th-232 | actinide | 57.37 | 4.50 / 5.76 | 4.50 / 5.68 | 1.96 / 3.20 | 12.8x / 10.0x | 29.2x / 17.9x |
| U-235 | actinide | 128.17 | 9.55 / 10.74 | 9.81 / 11.10 | 2.37 / 3.60 | 13.4x / 11.9x | 54.2x / 35.6x |
| U-238 | actinide | 67.51 | 5.43 / 6.81 | 4.89 / 6.30 | 2.37 / 3.74 | 12.4x / 9.9x | 28.5x / 18.0x |

By class (sums of the per-target medians; class from TALYS's collective type in `structure/deformation`, actinide
for Z ≥ 89):

| class | targets | TALYS | no-cache compute | no-cache process | warm compute | warm process | speed-up no-cache (compute / process) | speed-up warm (compute / process) |
|---|---|---|---|---|---|---|---|---|
| spherical | 3 | 19.9 | 2.3 | 5.9 | 2.3 | 6.0 | 8.6x / 3.4x | 8.7x / 3.3x |
| vibrational | 2 | 28.4 | 2.5 | 5.0 | 1.6 | 3.9 | 11.2x / 5.7x | 17.3x / 7.2x |
| rotational | 4 | 186.2 | 17.3 | 22.6 | 4.5 | 9.6 | 10.8x / 8.3x | 41.4x / 19.4x |
| actinide | 3 | 253.1 | 19.5 | 23.3 | 6.7 | 10.5 | 13.0x / 10.9x | 37.8x / 24.0x |
| all | 12 | 487.6 | 41.6 | 56.8 | 15.1 | 30.1 | 11.7x / 8.6x | 32.2x / 16.2x |

Reading the table:

- For light spherical targets both codes finish in seconds, and the engine's fixed Python start-up (about 1.2 CPU-s)
  is a large share of a one-off run, so the whole-process ratio there is only 3–4x.
- The cache has no effect on spherical targets, which have no incident coupled-channels solve.
- The deformed and actinide targets dominate the total cost of both codes, so the 12-target totals are driven by them.

## Cold and warm cache

For deformed targets most of the engine's time goes into the incident-channel coupled-channels solve. That solve
depends only on the target, the energy and the optical-model parameters at that energy, not on level densities,
photon strength functions or pre-equilibrium settings. `--cc-cache <dir>` (or `INCOGNITA_CC_CACHE=<dir>`) stores each
solution on disk under a hash of all its inputs and reuses it when the same inputs recur.

- **Cold** (empty cache): the first run pays the full cost plus writing the files. Measured cold and no-cache totals
  are the same within noise (41.6 vs 41.6 CPU-s compute).
- **Warm**: applies when the same coupled-channels solutions are needed again: parameter sweeps over level-density,
  gamma-strength or other non-optical-model parameters, reruns of the same targets, or several model variants on the
  same grid. A change to the neutron optical model, the energy grid or the code itself produces different keys, so
  those runs are cold again.
- **No cache** is the number for a single fresh calculation and is the conservative headline.

In this run, the cross sections from the cold and warm arms were identical to the no-cache arm at every energy for
all four observables.

## Parity

The speed comparison is only meaningful if both codes compute the same thing. For every no-cache run the engine's
cross sections were compared with the TALYS run of the same repeat at the 64 benchmark energies (12 targets × 64
energies × 3 repeats = 2,304 points per observable; points below 1e-6 mb are excluded, none were):

| observable | points | max abs(log10(engine/TALYS)) | median |
|---|---|---|---|
| total | 2304 | 0.000102 | 0.000001 |
| elastic | 2304 | 0.000220 | 0.000002 |
| nonelastic | 2304 | 0.000539 | 0.000005 |
| capture | 2304 | 0.001211 | 0.000007 |

Capture is the residual production of (Z, A+1). The largest difference, 1.2e-3 in log10 (0.28 %), is on Gd-157; the
largest for total and elastic is on the actinides. TALYS writes its output files to seven significant digits, which
sets a floor near 1e-6 to 1e-7 on this comparison.

## Reproduce

Requirements: TALYS-2 built from the upstream sources (see [talys-install.md](talys-install.md)), its `structure/`
directory, `taskset` (util-linux), and the native kernels (`make native`).

```bash
uv run python scripts/bench_vs_talys.py \
    --talys "$HOME/opt/talys-src/bin/talys" \
    --talys-structure "$HOME/opt/talys-src/structure" \
    --nuclides mix12 --energies grid64 --repeats 3 --cpus 8,10 --out out/bench
```

`--cpus 8` runs one stream on one core; `--nuclides` also takes a list such as `Fe-56,U-238`; `--energies` takes
`grid64` (the engine's standard grid), `grid16` or `short` (5 energies). The run above took 17 minutes of wall time
on two cores. Output: `out/bench/bench.json` (every run, the machine description, the load samples and the summary)
and `out/bench/bench.md` (the tables above). Results depend on the machine, the compiler and the background load;
the ratios, not the absolute times, are what should carry over.

The run quoted here used the repository at commit `ea27736` plus this benchmark script; the engine code was
unchanged.
