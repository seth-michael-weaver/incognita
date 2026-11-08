#!/usr/bin/env bash
# KWCOV B12 (RECOIL): build physics/hf/native/recoil.c (the LAB scatter, output only) into physics/hf/native/lib/librecoil.so.
# Same flags as the other native kernels (IEEE order as written). Missing library -> recoil.py's Python scatter_py.
set -euo pipefail
cd "$(dirname "$0")/.."
CC="${CC:-}"
if [ -z "$CC" ]; then
  for candidate in "$HOME/micromamba/envs/incognita-phys/bin/gcc" "$HOME/micromamba/envs/phys/bin/gcc"; do
    if [ -x "$candidate" ]; then CC="$candidate"; break; fi
  done
  CC="${CC:-cc}"
fi
mkdir -p physics/hf/native/lib
OUT=physics/hf/native/lib/librecoil.so
"$CC" -O2 -fno-fast-math -ffp-contract=off -fno-tree-vectorize -fno-strict-aliasing \
  -std=c11 -Wall -Wextra -Wno-unused-parameter -fPIC -shared physics/hf/native/recoil.c -o "$OUT.tmp" -lm
mv "$OUT.tmp" "$OUT"
echo "built $OUT with $("$CC" --version | head -1)"
