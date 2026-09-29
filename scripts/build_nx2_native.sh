#!/usr/bin/env bash
# NATIVEX2: build every physics/hf/native/nx2_*.c (the second wave of whole-stage kernels) into one
# library, physics/hf/native/lib/libnx2.so (libnx2.dylib on macOS; gitignored build output).
#
#   scripts/build_nx2_native.sh     # uses $CC, else Apple clang on macOS, else a micromamba gcc, else cc
#
# Held to closeness, not to bits (docs/results/hf-nativex2.md): -O2, no intrinsics, so x86-64 and
# arm64 build the same source. Without a build (or with HF_NATIVE=0 / HF_NATIVEX=0 / HF_NX2=0) the
# callers run their torch/numpy paths. Check a new build with tests/hf/test_nx2.py.
#
# FP_CONTRACT: the compiler's default contraction (fusing a*b+c into one FMA) differs between
# Apple clang on arm64 (on by default) and gcc on x86-64 (off by default), so the same source
# produced different last-ulp results per box -- not "same source, same result" as intended. The
# reference these kernels are checked against (numpy/Python, no FMA) never contracts, so `off` is
# the setting that actually matches "same source" across compilers; see
# docs/results/hf-macfma.md.
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
OUT=physics/hf/native/lib/libnx2.so
LINK=-shared
if [ "$(uname -s)" = "Darwin" ]; then
  OUT=physics/hf/native/lib/libnx2.dylib
  LINK=-dynamiclib
fi
SRC=(physics/hf/native/nx2_*.c physics/hf/native/ld.c physics/hf/native/fission.c)  # ld.c: CENGLD's level-density kernels; fission.c: CENGFIS's
"$CC" -O2 -std=c11 -ffp-contract=off -Wall -Wextra -Wno-unused-parameter -fPIC $LINK "${SRC[@]}" -o "$OUT.tmp" -lm
mv "$OUT.tmp" "$OUT"
echo "built $OUT from ${#SRC[@]} files with $("$CC" --version | head -1)"
