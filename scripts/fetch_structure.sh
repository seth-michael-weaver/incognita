#!/usr/bin/env bash
# Fetch ONLY the part of the TALYS structure database the engine reads (~0.9 GB of 8.7 GB).
#
#   scripts/fetch_structure.sh [DEST]                 # sparse, blob-filtered clone from GitHub (MIT, A.J. Koning)
#   scripts/fetch_structure.sh DEST --from TALYS_SRC  # copy the same subset out of an existing TALYS checkout
#
# then: export TALYS_DIR=DEST
#
# The list comes from tracing every file the engine opened (sys.addaudithook) on Fe-56,
# Au-197 and U-238 (spherical, deformed/coupled-channels, fissile) on 2026-10-11 -- both the production
# deck and the v0.1 default arm (which also reads density/ground/ctm and gamma/gdr) -- widened to whole
# directories. It is NOT yet traced over the whole chart: a nucleus that needs a file outside it
# may NOT stop: several readers fall back silently when a file is missing (0.6 dex was seen# on U-238 before ctm/gdr were added), so check a new region bitwise against a full checkout. The BSkG3 level-density
# tables are only read for fissile systems, so only Z >= 82 elements are fetched.
# resfiles/ (TENDL-derived resonance files) is deliberately excluded: the engine never reads library values.
set -euo pipefail
DEST="${1:-$HOME/opt/talys-structure}"
FROM=""
if [ "${2:-}" = "--from" ]; then FROM="${3:?--from needs a TALYS checkout}"; fi

DIRS="abundance masses levels/final gamma/gogny gamma/gognyM1 gamma/gdr density/ground/ctm deformation optical/global optical/proton optical/neutron
optical/ripl fission/states fission/hfbpath_bskg3"
HEAVY="Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn"
FILES=""
for e in $HEAVY; do
  FILES="$FILES density/ground/bskg3/$e.tab density/ground/bskg3/$e.ld_*"
  for m in Max1 Max2 Max3; do FILES="$FILES density/fission/bskg3/$m/$e.ld"; done
done

if [ -n "$FROM" ]; then
  mkdir -p "$DEST/structure"
  (cd "$FROM/structure" && for d in $DIRS; do echo "$d"; done; for f in $FILES; do [ -e "$f" ] && echo "$f"; done; true) \
    | (cd "$FROM/structure" && xargs tar -chf -) | (cd "$DEST/structure" && tar -xf -)
else
  git clone --depth 1 --filter=blob:none --no-checkout https://github.com/arjankoning1/talys "$DEST"
  cd "$DEST"
  git sparse-checkout init --no-cone
  { for d in $DIRS; do echo "/structure/$d/"; done; for f in $FILES; do echo "/structure/$f"; done; } \
    | git sparse-checkout set --no-cone --stdin
  git checkout
fi
du -sh "$DEST/structure"
echo "export TALYS_DIR=$DEST"
