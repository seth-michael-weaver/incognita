#!/usr/bin/env bash
# Build a private, instrumented copy of TALYS for the EXCL3 multiple pre-equilibrium gate (A-mpe).
# usage: apply_hooks.sh SRC_TALYS_DIR DEST_DIR   (DEST gets source/ copy, structure symlink, bin/talys)
# The two hooks only CALL write routines (mpdump.f90); no TALYS variable is modified, so the
# instrumented binary reproduces the reference xs*.tot / binE*.out unchanged.
set -euo pipefail
src=$1; dst=$2
here=$(cd "$(dirname "$0")" && pwd)
export PATH="${TALYS_TOOLCHAIN_BIN:-$HOME/micromamba/envs/phys/bin}:$PATH"
mkdir -p "$dst/bin"
rm -rf "$dst/source"; cp -r "$src/source" "$dst/source"
ln -sfn "$src/structure" "$dst/structure"
cp "$here/mpdump.f90" "$dst/source/mpdump.f90"
f="$dst/source/multipreeq2.f90"
grep -q "^  if (Zcomp == 0 .and. Ncomp == 0) return$" "$f"
grep -q "^  Dmulti(nex) = summpe / xspopex(Zcomp, Ncomp, nex)$" "$f"
sed -i '0,/^  if (Zcomp == 0 .and. Ncomp == 0) return$/s//  if (Zcomp == 0 .and. Ncomp == 0) return\n  call mpdump_in(Zcomp, Ncomp, nex)/' "$f"
sed -i 's|^  Dmulti(nex) = summpe / xspopex(Zcomp, Ncomp, nex)$|  call mpdump_out(Zcomp, Ncomp, nex, summpe)\n  Dmulti(nex) = summpe / xspopex(Zcomp, Ncomp, nex)|' "$f"
test "$(grep -c 'call mpdump_' "$f")" = 2
cd "$dst/source" && make FC="${FC:-gfortran}" FFLAGS="-w -O3 -ffp-contract=off" > "$dst/build.log" 2>&1
ls -la "$dst/bin/talys"
sha256sum "$dst/bin/talys" | cut -c1-16
