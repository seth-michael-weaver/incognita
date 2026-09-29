#!/usr/bin/env bash
# SPEEDW: build the compiled kernels of the whole-run speed work (physics/hf/native/speedw.c: the
# DWBA Numerov loop and the multiple pre-equilibrium bin) into physics/hf/native/lib/libspeedw.so
# (gitignored build output; `lib/` is not a package, so pkgutil does not walk the .so as a module).
#
#   scripts/build_speedw_native.sh     # uses $CC, else a micromamba gcc, else cc
#
# Same flags as scripts/build_native.sh: IEEE operations in the order written (no FMA contraction,
# no reassociation, no auto-vectorised reductions). Without the .so (or with HF_NATIVE=0, or
# HF_SPEEDW_NATIVE=0) both callers run their Python loops. Every machine needs its own build and a
# run of tests/hf/test_speedw_native.py (the DWBA kernel's identity rests on torch's kernels).
set -euo pipefail
cd "$(dirname "$0")/.."
CC="${CC:-}"
# macOS: Apple clang, never a micromamba gcc (its driver execs a clang that is not there)
if [ -z "$CC" ] && [ "$(uname -s)" = "Darwin" ]; then
  CC=cc
fi
if [ -z "$CC" ]; then
  for candidate in "$HOME/micromamba/envs/incognita-phys/bin/gcc" "$HOME/micromamba/envs/phys/bin/gcc"; do
    if [ -x "$candidate" ]; then
      CC="$candidate"
      break
    fi
  done
  CC="${CC:-cc}"
fi
mkdir -p physics/hf/native/lib
OUT=physics/hf/native/lib/libspeedw.so
"$CC" -O2 -fno-fast-math -ffp-contract=off -fno-tree-vectorize -fno-strict-aliasing \
  -std=c11 -Wall -Wextra -Wno-unused-parameter -fPIC -shared \
  physics/hf/native/speedw.c -o "$OUT.tmp" -lm
mv "$OUT.tmp" "$OUT"
echo "built $OUT with $("$CC" --version | head -1)"
