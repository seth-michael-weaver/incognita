#!/usr/bin/env bash
# SPEEDT3: build the compiled transmission-coefficient kernels (physics/hf/native/hfnative.c)
# into physics/hf/native/libhfnative.so (gitignored build output).
#
#   scripts/build_native.sh            # uses $CC, else the incognita-phys micromamba gcc, else cc
#
# The flags keep IEEE operation order exactly as written: no FMA contraction, no reassociation,
# no auto-vectorised reductions. The kernels are bit-identical to the Python path on the machine
# they were validated on (tests/hf/test_native.py); every other machine (the desktop, the Mac)
# needs its own build and its own run of that test, or it falls back to Python automatically
# (no .so, or HF_NATIVE=0). The .so depends on libc/libm only; the LAPACK/BLAS it calls are
# torch's own, handed over by address at load time.
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
# `lib/` is not a package on purpose: a .so next to an __init__.py is walked as a module by
# pkgutil and tests/hf/test_contract.py::test_module_imports then fails to import it.
mkdir -p physics/hf/native/lib
OUT=physics/hf/native/lib/libhfnative.so
"$CC" -O2 -fno-fast-math -ffp-contract=off -fno-tree-vectorize -fno-strict-aliasing \
  -std=c11 -Wall -Wextra -Wno-unused-parameter -fPIC -shared \
  physics/hf/native/hfnative.c -o "$OUT.tmp" -lm
mv "$OUT.tmp" "$OUT"
echo "built $OUT with $("$CC" --version | head -1)"
