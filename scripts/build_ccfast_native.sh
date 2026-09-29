#!/usr/bin/env bash
# CCFAST2: build physics/hf/native/ccfast.c (the coupled-channels radial loop without
# bit-identity) into physics/hf/native/lib/libccfast.so (libccfast.dylib on macOS; gitignored).
#
#   scripts/build_ccfast_native.sh     # uses $CC, else the micromamba gcc, else cc
#
# Unlike build_native.sh this one optimises freely (-O3, FMA contraction, vectorisation): the kernel
# is held to the closeness rule of docs/results/hf-speed-profile.md ("Coupled channels without
# bit-identity"), not to the bits of the Python loop. Its LAPACK/BLAS are torch's own, found by
# address at load time (physics/hf/ecis/ccnative.py). Without a build the port falls back to
# `hf_cc_block` / Python automatically; check a new build with tests/hf/test_ccfast.py.
set -euo pipefail
cd "$(dirname "$0")/.."
CC="${CC:-}"
if [ -z "$CC" ] && [ "$(uname -s)" = "Darwin" ]; then
  CC=cc  # Apple clang; the micromamba env there has no plain gcc
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
ARCH_FLAGS=""
if [ "$(uname -m)" = "x86_64" ]; then
  ARCH_FLAGS="-mavx2 -mfma"
fi
mkdir -p physics/hf/native/lib
OUT=physics/hf/native/lib/libccfast.so
LINK=-shared
if [ "$(uname -s)" = "Darwin" ]; then
  OUT=physics/hf/native/lib/libccfast.dylib
  LINK=-dynamiclib  # LAPACK still comes from torch's libtorch_cpu.dylib, by address
fi
# shellcheck disable=SC2086
"$CC" -O3 $ARCH_FLAGS -std=c11 -Wall -Wextra -Wno-unused-parameter -fPIC $LINK \
  physics/hf/native/ccfast.c -o "$OUT.tmp" -lm
mv "$OUT.tmp" "$OUT"
echo "built $OUT with $("$CC" --version | head -1)"
# SETB: the same kernel with the split-storage solve and stabilisation (physics/hf/native/ccsplit.h),
# selected by physics/hf/ecis/ccnative.py where it is the default (HF_CCSPLIT)
SPLIT="${OUT/libccfast/libccsplit}"
# shellcheck disable=SC2086
"$CC" -O3 $ARCH_FLAGS -DCCFAST_SPLIT -std=c11 -Wall -Wextra -Wno-unused-parameter -fPIC $LINK \
  physics/hf/native/ccfast.c -o "$SPLIT.tmp" -lm
mv "$SPLIT.tmp" "$SPLIT"
echo "built $SPLIT"
