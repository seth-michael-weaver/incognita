#!/usr/bin/env bash
# CCPROP: build physics/hf/native/ccprop.c into physics/hf/native/lib/libccprop.so
# (libccprop.dylib on macOS; gitignored). Same flags as build_ccfast_native.sh: the propagator is a
# research prototype held to the closeness rule, not to anyone's bits.
set -euo pipefail
cd "$(dirname "$0")/.."
CC="${CC:-}"
if [ -z "$CC" ] && [ "$(uname -s)" = "Darwin" ]; then
  CC=cc
fi
if [ -z "$CC" ]; then
  for candidate in "$HOME/micromamba/envs/incognita-phys/bin/gcc" "$HOME/micromamba/envs/phys/bin/gcc"; do
    if [ -x "$candidate" ]; then CC="$candidate"; break; fi
  done
  CC="${CC:-cc}"
fi
ARCH_FLAGS=""
if [ "$(uname -m)" = "x86_64" ]; then ARCH_FLAGS="-mavx2 -mfma"; fi
mkdir -p physics/hf/native/lib
OUT=physics/hf/native/lib/libccprop.so
LINK=-shared
if [ "$(uname -s)" = "Darwin" ]; then
  OUT=physics/hf/native/lib/libccprop.dylib
  LINK=-dynamiclib
fi
# shellcheck disable=SC2086
"$CC" -O3 $ARCH_FLAGS -std=c11 -Wall -Wextra -Wno-unused-parameter -fPIC $LINK \
  physics/hf/native/ccprop.c -o "$OUT.tmp" -lm
mv "$OUT.tmp" "$OUT"
echo "built $OUT with $("$CC" --version | head -1)"
