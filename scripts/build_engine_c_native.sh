#!/usr/bin/env bash
# CENGDECAY (ROUTE100 WP5): build physics/hf/native/engine_decay.c (the warm decay core of one
# (nuclide, energy) in one call) into physics/hf/native/lib/libengdecay.so (libengdecay.dylib on
# macOS; gitignored build output). It calls libnativex's and libnx2's kernels through pointers, so
# build those first (scripts/build_nativex_native.sh, scripts/build_nx2_native.sh).
#
#   scripts/build_engine_c_native.sh    # uses $CC, else Apple clang on macOS, else a micromamba gcc, else cc
#
# Without a build (or with HF_NATIVE=0 / HF_ENGINE_C=0) `physics.hf.engine_c` runs the engine's
# own Python path. Check a new build with tests/hf/test_engine_c.py.
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
OUT=physics/hf/native/lib/libengdecay.so
LINK=-shared
if [ "$(uname -s)" = "Darwin" ]; then
  OUT=physics/hf/native/lib/libengdecay.dylib
  LINK=-dynamiclib
fi
"$CC" -O2 -ffp-contract=off -std=c11 -Wall -Wextra -Wno-unused-parameter -fPIC $LINK \
  physics/hf/native/engine_decay.c -o "$OUT.tmp" -lm
mv "$OUT.tmp" "$OUT"
echo "built $OUT with $("$CC" --version | head -1)"
