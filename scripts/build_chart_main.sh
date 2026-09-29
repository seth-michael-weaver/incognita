#!/usr/bin/env bash
# CHARTDRV (ROUTE100 WP10): build native/chart_main.c, the one-box chart driver binary.
#
#   scripts/build_chart_main.sh     # uses $CC, else the micromamba gcc, else cc
#
# Plain C11 + pthreads; no torch, no BLAS. The physics stays in the warm Python workers it drives
# (scripts/hf_route100_chart.py serve), so this binary is scheduling, the total-J loop of
# `solver._sum_blocks_tasks`, and output.
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
mkdir -p native
"$CC" -O2 -std=c11 -Wall -Wextra -pthread -o native/chart_main.tmp native/chart_main.c -lm
mv native/chart_main.tmp native/chart_main
echo "built native/chart_main with $CC"
