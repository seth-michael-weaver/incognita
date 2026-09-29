#!/usr/bin/env bash
# Build a private, instrumented copy of TALYS for the T10 emission acceptance test (A-mult).
# usage: apply_hooks.sh SRC_TALYS_DIR DEST_DIR   (DEST gets source/ copy, structure symlink, bin/talys)
# The two hooks only CALL write routines (chdump.f90); no TALYS variable is modified, so the
# instrumented binary reproduces the reference xs*.tot / rp*.tot / binE*.out unchanged.
# gfortran and make live in the micromamba `phys` env on this box, not in /usr/bin.
set -euo pipefail
src=$1; dst=$2
here=$(cd "$(dirname "$0")" && pwd)
export PATH="${TALYS_TOOLCHAIN_BIN:-$HOME/micromamba/envs/phys/bin}:$PATH"
mkdir -p "$dst/bin"
rm -rf "$dst/source"; cp -r "$src/source" "$dst/source"
ln -sfn "$src/structure" "$dst/structure"
cp "$here/chdump.f90" "$dst/source/chdump.f90"
f="$dst/source/talysreaction.f90"
grep -q "^        if (flagchannels) call channels$" "$f"
grep -q "^        call binary$" "$f"
sed -i 's/^        if (flagchannels) call channels$/        call chdump_channels\n        if (flagchannels) call channels/' "$f"
sed -i 's/^        call binary$/        call chdump_binary\n        call binary/' "$f"
test "$(grep -c 'call chdump_' "$f")" = 2
cd "$dst/source" && make FC="${FC:-gfortran}" FFLAGS="-w -O3 -ffp-contract=off" > "$dst/build.log" 2>&1
ls -la "$dst/bin/talys"
