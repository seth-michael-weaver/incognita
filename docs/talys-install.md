# TALYS install (from source, no sudo)

TALYS is the Hauser-Feshbach / optical-model nuclear reaction code used by
Incognita as a physics prior and as a consistency check against evaluated data.
It is MIT-licensed and hosted at <https://github.com/arjankoning1/talys>.

## Engine only: you need the structure database, not the Fortran binary

The Python/C engine reads TALYS's `structure/` database (8.6 GB) and nothing else from TALYS. To fetch only that:

```bash
mkdir -p $HOME/opt && cd $HOME/opt
git clone --depth 1 --filter=blob:none --sparse https://github.com/arjankoning1/talys talys-src
cd talys-src && git sparse-checkout set structure
export TALYS_DIR=$HOME/opt/talys-src
```

Build the Fortran binary (below) only to compare against stock TALYS.

## Version

| item | value |
|---|---|
| upstream commit | `1f634cbcdc7003e38a6bb91d3d69e6b38dfbe234` (main, 2026-09-06) |
| banner in `talys.out` | `TALYS-2.25 (Version: September 3, 2026)` |
| `source:` line in YANDF `*.tot` files | `TALYS-2.24` (upstream inconsistency; the code is 2.25) |
| clone method | `git clone --depth 1` (no tags in a shallow clone; version taken from `source/talys.f90` header) |
| on-disk size | 11 GB (`structure/` database is the bulk) |

## Locations

| what | path |
|---|---|
| source + structure DB | `$HOME/opt/talys-src` |
| binary (installer output) | `$HOME/opt/talys-src/bin/talys` |
| convenience symlink | `$HOME/opt/talys -> $HOME/opt/talys-src`, so `$HOME/opt/talys/bin/talys` also works |
| build log | `$HOME/opt/talys-build.log` |

## Toolchain

Any gfortran works; ours comes from a micromamba env `incognita-phys` (gfortran 16.2.0,
conda-forge). Adjust the PATH lines below to wherever your gfortran lives. This env is *only* used for compiling; the Python side of Incognita
is managed by `uv` in your checkout and is independent.

```bash
export PATH=$HOME/micromamba/envs/incognita-phys/bin:$PATH
```

## Exact build commands

```bash
mkdir -p $HOME/opt && cd $HOME/opt
git clone --depth 1 https://github.com/arjankoning1/talys talys-src   # ~11 GB, took ~25 min on this link

# one-line patch so the binary finds structure/ without TALYS_DIR (see Patches)
cd talys-src
sed -i "s|code_dir = '/path/to/talys/'|code_dir = '$HOME/opt/talys-src/'|" source/machine.f90

export PATH=$HOME/micromamba/envs/incognita-phys/bin:$PATH
./install_talys.bash            # == make -C source clean && make -C source all
ln -sfn $HOME/opt/talys-src $HOME/opt/talys
```

The Makefile compiles all 387 `.f`/`.f90` files in a single `gfortran`
invocation with the stock flags `-w -O3 -ffp-contract=off` and installs to
`../bin/talys`. **Build time: 90 s** wall on this box (16 cores, but the build
is single-process). No `-fallow-argument-mismatch` / `-std=legacy` was needed:
gfortran 16.2 compiled the tree cleanly with zero warnings printed
(`-w` suppresses them anyway).

To rebuild after `git pull --ff-only`, re-run `./install_talys.bash` (the
`machine.f90` patch will need re-applying if upstream touches that line;
`git diff` shows whether it is still in place).

## Runtime configuration (structure database)

TALYS locates its structure database as `${TALYS_DIR}/structure/`, checked at
startup via `structure/abundance/H.abun`. Precedence in `source/machine.f90`:

1. env var `TALYS_DIR` if set and non-empty;
2. otherwise the compiled-in fallback `code_dir`, which we patched to
   `$HOME/opt/talys-src/` (upstream default is the placeholder
   `/path/to/talys/`, which fails).

So the binary works with no environment at all. Recommended shell config
(what the installer prints):

```bash
export TALYS_DIR=$HOME/opt/talys          # or talys-src; the symlink resolves either way
export PATH="$TALYS_DIR/bin:$PATH"
export TALYS_USER="Your Name"                   # only stamps the output headers
```

Peak RSS for a single-energy 56Fe run is ~720 MB (TALYS pre-allocates large
arrays; `memorypar` in `source/A0_talys_mod.f90` can lower this if needed).

## Smoke test

Input (classic 4-liner), run in a scratch dir with `talys < talys.inp > talys.out`
and **no** `TALYS_DIR` set, to prove the fallback patch:

```
projectile n
element fe
mass 56
energy 1.
```

Result: exit 0, "The TALYS team congratulates you with this successful
calculation." **Runtime 0.79 s** CPU (0.88 s wall, first run, cold cache).

From `talys.out` section "1. Total (binary) cross sections" (mb):

| quantity | mb |
|---|---|
| Total | 3785.75 (**3.79 b**, target ≈ 3 b: OK) |
| Shape elastic | 1548.50 |
| Compound elastic | 1650.24 |
| Total elastic | 3198.74 |
| Reaction | 2237.25 |
| Non-elastic | 587.01 |
| 57Fe production, i.e. (n,γ) | 3.045 |
| 56Fe (n,n') | 583.9 |

The plain 4-line input does **not** write per-channel tables. Adding the
output keywords the Python wrapper uses by default

```
channels y
filechannels y
filetotal y
fileelastic y
outbasic n
```

produces (0.49 s wall) `total.tot`, `elastic.tot`, `nonelastic.tot`,
`reaction.tot`, `all.tot`, `xs000000.tot` (n,g), `xs100000.tot` (n,n'),
`xs000001.tot` (n,a), plus `*prod.tot`. Channels below threshold at 1 MeV
((n,2n), (n,p), ...) are simply not written. A 1 + 14 MeV run through the
wrapper takes 1.3 s and gives at 14 MeV: total 2657.8, elastic 1219.7,
(n,2n) 480.8, (n,p) 124.8, (n,α) 35.7, (n,n') 742.7 mb, all in line with
ENDF/B-VIII.0 for 56Fe.

## Output file format

All `*.tot` files are YANDF-0.4: `#`-prefixed YAML-ish header (title, target,
reaction `type`, `ENDF_MT`, Q-value, threshold, residual), then `##` column
names and `##` units lines, then whitespace-separated numeric rows with `E`
in MeV and `xs` in **mb**. Exclusive-channel files are named
`xs<n><p><d><t><h><a>.tot` by ejectile multiplicity (`xs200000` = (n,2n),
`xs010000` = (n,p), `xs000001` = (n,α), `xs000000` = (n,γ), `xs100000` = (n,n')).

## Python wrapper

`physics/talys/runner.py` (stdlib + numpy):

```python
from physics.talys.runner import run_talys, get_channel
r = run_talys(26, 56, [1.0, 14.0])          # -> dict
r["channels"]["total"]["xs"]                 # ndarray, mb
get_channel(r, "(n,2n)")["E"]                # MeV
```

* Binary path: module constant `TALYS_BIN` (default
  `$HOME/opt/talys-src/bin/talys`), overridable with env `TALYS_BIN`.
  `TALYS_DIR` is derived from the binary location if not set, and is passed
  to the subprocess explicitly.
* Runs in a temp dir (deleted afterwards) unless `workdir=` is given.
* `timeout` (default 600 s) raises `TalysError`; so does a non-zero exit or a
  `TALYS error` line in `talys.out`.
* Channel keys: `total, elastic, nonelastic, reaction, capture, inelastic,
  n2n, n3n, np, nd, nt, nh, na, nnp, nna, n2np`, plus any other `xs*.tot`
  keyed by its reaction string. Each value has `E`, `xs`, `MT`, `reaction`,
  `file`, `columns`, `data` (full table), and `Q_value` / `E_threshold`
  when present.

Tests: `tests/test_talys_runner.py` (5 tests, skipped if the binary is
missing).

```bash
uv run pytest tests/test_talys_runner.py -q   # 5 passed in ~1.2 s
```

## Patches applied

Exactly one, outside the Incognita repository, in the TALYS clone:

```diff
--- a/source/machine.f90
+++ b/source/machine.f90
@@ -48,7 +48,7 @@ subroutine machine
-    code_dir = '/path/to/talys/'
+    code_dir = '$HOME/opt/talys-src/'
```

Purpose: make the structure database resolvable without `TALYS_DIR`.
No compiler-flag or Fortran-strictness patches were required with gfortran 16.2.
