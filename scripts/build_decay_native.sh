#!/usr/bin/env bash
# SPEEDD: build the compiled decay kernels (physics/hf/compound/decay_native.c) into
# physics/hf/compound/libdecaynative.so.1 (a build output, not committed; the ".1" keeps
# pkgutil from listing it as a Python extension module of physics.hf.compound).
#
#   scripts/build_decay_native.sh      # uses $CC, else the incognita-phys micromamba gcc, else cc
#
# Same flags as scripts/build_native.sh: IEEE operations in the order written (no FMA contraction,
# no reassociation, no auto-vectorised reductions), so a build gives the same bits on every run.
# Without the .so (or with HF_NATIVE=0) compound.decay_fast runs its numpy path.
set -euo pipefail
cd "$(dirname "$0")/.."
CC="${CC:-}"
# macOS: Apple clang, never a micromamba gcc (its driver execs a clang that is not there)
if [ -z "$CC" ] && [ "$(uname -s)" = "Darwin" ]; then
  CC=cc
fi
if [ -z "$CC" ]; then
  # conda-forge gcc, under whichever micromamba env this box has (the env name varies by machine,  #   e.g. incognita-phys), for machines without a system cc.
  for candidate in "$HOME/micromamba/envs/incognita-phys/bin/gcc" "$HOME/micromamba/envs/phys/bin/gcc"; do
    if [ -x "$candidate" ]; then
      CC="$candidate"
      break
    fi
  done
  CC="${CC:-cc}"
fi
OUT=physics/hf/compound/libdecaynative.so.1
"$CC" -O2 -fno-fast-math -ffp-contract=off -fno-tree-vectorize -fno-strict-aliasing \
  -std=c11 -Wall -Wextra -Wno-unused-parameter -fPIC -shared \
  physics/hf/compound/decay_native.c -o "$OUT.tmp" -lm
mv "$OUT.tmp" "$OUT"
echo "built $OUT with $("$CC" --version | head -1)"
