#!/usr/bin/env bash
# CENGSETUP: build physics/hf/native/lib/libsetup.so (native/setup.c). Bits do not depend on the
# vector flags: ISO C with -ffp-contract=off fuses no product and reorders no sum.
set -euo pipefail
cd "$(dirname "$0")/.."
CC="${CC:-}"
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
OUT=physics/hf/native/lib/libsetup.so
LINK=-shared
VEC=()
if [ "$(uname -s)" = "Darwin" ]; then
  OUT=physics/hf/native/lib/libsetup.dylib
  LINK=-dynamiclib
elif grep -qw avx2 /proc/cpuinfo && grep -qw fma /proc/cpuinfo; then
  VEC=(-mavx2 -mfma)
fi
# bash 3.2 (macOS) treats "${VEC[@]}" as unbound under `set -u` when VEC is empty
"$CC" -O3 ${VEC[@]+"${VEC[@]}"} -std=c11 -ffp-contract=off -fno-fast-math -Wall -Wextra \
  -Wno-unused-parameter -fPIC $LINK physics/hf/native/setup.c physics/hf/native/nx2_omp.c \
  physics/hf/native/nx2_preeq.c -o "$OUT.tmp" -lm
mv "$OUT.tmp" "$OUT"
echo "built $OUT with $("$CC" --version | head -1) ${VEC[*]-}"
