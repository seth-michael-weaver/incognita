#!/usr/bin/env bash
# Build a private, instrumented copy of TALYS for the T9 compound acceptance tests.
# usage: apply_hooks.sh SRC_TALYS_DIR DEST_DIR     (DEST gets source/ copy, structure symlink, bin/talys)
# The three hooks only CALL write routines (cndump.f90); no TALYS variable is modified.
set -euo pipefail
src=$1; dst=$2
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$dst/bin"
rm -rf "$dst/source"; cp -r "$src/source" "$dst/source"
ln -sfn "$src/structure" "$dst/structure"
cp "$here/cndump.f90" "$dst/source/cndump.f90"
f="$dst/source/comptarget.f90"
grep -q "^  nex = maxex(Zcomp, Ncomp)$" "$f"
grep -q "^      call compprepare(Zcomp, Ncomp, J2, parity)$" "$f"
grep -q "^  if (flagfisout) call tfissionout(Zcomp, Ncomp, nex)$" "$f"
sed -i 's/^  nex = maxex(Zcomp, Ncomp)$/  nex = maxex(Zcomp, Ncomp)\n  call cndump_inputs/' "$f"
sed -i 's/^      call compprepare(Zcomp, Ncomp, J2, parity)$/      call compprepare(Zcomp, Ncomp, J2, parity)\n      call cndump_jp(J2, parity)/' "$f"
sed -i 's/^  if (flagfisout) call tfissionout(Zcomp, Ncomp, nex)$/  call cndump_pop\n  if (flagfisout) call tfissionout(Zcomp, Ncomp, nex)/' "$f"
test "$(grep -c 'call cndump_' "$f")" = 3
# continuum-decay hooks (compound.f90 inputs), active only when CNDUMP_ZN is set at run time
m="$dst/source/multiple.f90"
grep -q "^        if (flagcomp) then$" "$m"
grep -q "^              call compound(Zcomp, Ncomp, nex, J2, parity)$" "$m"
grep -q "^          if (flagfisout) call tfissionout(Zcomp, Ncomp, nex)$" "$m"
sed -i 's/^        if (flagcomp) then$/        call cnmulti_inputs(Zcomp, Ncomp, nex, popepsA, odd)\n        if (flagcomp) then/' "$m"
sed -i 's/^              call compound(Zcomp, Ncomp, nex, J2, parity)$/              call compound(Zcomp, Ncomp, nex, J2, parity)\n              call cnmulti_jp(Zcomp, Ncomp, J2, parity)/' "$m"
sed -i 's/^          if (flagfisout) call tfissionout(Zcomp, Ncomp, nex)$/          call cnmulti_pop(Zcomp, Ncomp, nex)\n          if (flagfisout) call tfissionout(Zcomp, Ncomp, nex)/' "$m"
test "$(grep -c 'call cnmulti_' "$m")" = 3
cd "$dst/source" && make FC="${FC:-gfortran}" FFLAGS="-w -O3 -ffp-contract=off" > "$dst/build.log" 2>&1
ls -la "$dst/bin/talys"
