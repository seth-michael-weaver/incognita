#!/usr/bin/env bash
# NATIVEX: build physics/hf/native/nativex.c (whole-stage kernels: the compound target decay with
# and without Moldauer, and the multiple-emission cascade) into physics/hf/native/lib/libnativex.so
# (libnativex.dylib on macOS; gitignored build output).
#
#   scripts/build_nativex_native.sh     # uses $CC, else Apple clang on macOS, else a micromamba gcc, else cc
#
# Held to closeness, not to bits (docs/results/hf-nativex.md), so it optimises at -O2 with the
# compiler's default floating-point contraction; no intrinsics, so x86-64 and arm64 build the same
# source. Without a build (or with HF_NATIVE=0 / HF_NATIVEX=0) the callers run their torch/numpy
# paths. Check a new build with tests/hf/test_nativex.py.
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
OUT=physics/hf/native/lib/libnativex.so
LINK=-shared
if [ "$(uname -s)" = "Darwin" ]; then
  OUT=physics/hf/native/lib/libnativex.dylib
  LINK=-dynamiclib
fi
"$CC" -O2 -std=c11 -Wall -Wextra -Wno-unused-parameter -fPIC $LINK \
  physics/hf/native/nativex.c -o "$OUT.tmp" -lm
mv "$OUT.tmp" "$OUT"
echo "built $OUT with $("$CC" --version | head -1)"
