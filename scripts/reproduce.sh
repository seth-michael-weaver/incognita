#!/usr/bin/env bash
# Regenerate INCOGNITA's result tables from staged inputs and compare them with the published ones.
#
#   bash scripts/reproduce.sh                 # every step whose inputs are present; the rest are SKIPPED with the reason
#   bash scripts/reproduce.sh eval unc        # only these steps
#   bash scripts/reproduce.sh --download ...  # also fetch what can be fetched automatically (EXFOR master, benchmark repo)
#   bash scripts/reproduce.sh --with-engine terra   # also run the TALYS port for the terra check (~3 CPU-minutes)
#
# Steps: verify terra npfix speed capblind retro tiers na stock measure nostruct cleanretrain interp np vault final674 retromeasured curation registry  (default: all of them)
# Output: $INCOGNITA_WORK (default out/reproduce), with SUMMARY.md listing every step as IDENTICAL, DIFFERS (with the
# diff), or SKIPPED (the missing input and how to get it). What each README table needs, and which ones this script
# does NOT regenerate yet, is in docs/release/REPRODUCE.md.
#
# Inputs we do not redistribute (docs/release/INPUTS.md has the download steps):
#   - evaluated libraries (JENDL-5, TENDL-2025, ENDF/B-VIII.1, JEFF-4.0, JEFF-3.3, BROND-3.1, FENDL-3.2, CENDL-3.2,
#     IRDFF-II) from their official sites, staged with data/ingest/build_evaluated.py  -> $INCOGNITA_EVALUATED
#   - the EXFOR master from the IAEA (https://nds.iaea.org/exfor/), staged with data/ingest/exfor.py -> $INCOGNITA_MAIN/staging
#   - the evaluation exam rows (EXFOR points selected and binned by our curation)       -> $INCOGNITA_INPUTS/exam_rows
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
DOWNLOAD=0; ENGINE=0; STEPS=()
for a in "$@"; do
  case "$a" in
    --download) DOWNLOAD=1 ;;
    --with-engine) ENGINE=1 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) STEPS+=("$a") ;;
  esac
done
[ ${#STEPS[@]} -eq 0 ] && STEPS=(verify terra npfix speed capblind retro tiers na stock measure nostruct cleanretrain interp np vault final674 retromeasured curation registry)

export INCOGNITA_MAIN="${INCOGNITA_MAIN:-$ROOT}"   # one data directory for every tool: raw/, staging/ (default: this repository)
export INCOGNITA_EVALUATED="${INCOGNITA_EVALUATED:-$INCOGNITA_MAIN/staging/evaluated}"
export INCOGNITA_INPUTS="${INCOGNITA_INPUTS:-$HOME/incognita-inputs}"
export INCOGNITA_WORK="${INCOGNITA_WORK:-$ROOT/out/reproduce}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
W="$INCOGNITA_WORK"; mkdir -p "$W"
PY=(${INCOGNITA_PY:-uv run --no-sync python})
EXP=docs/release/expected
SUMMARY="$W/SUMMARY.md"
printf '# reproduce.sh summary (%s)\n\n| step | table | result |\n|---|---|---|\n' "$(date -u +%Y-%m-%dT%H:%MZ)" > "$SUMMARY"
FAILS=""   # steps that FAILED (plain string: macOS ships bash 3.2, which has no associative arrays)
setst() { [ "$2" = FAILED ] && FAILS="$FAILS $1"; return 0; }
command -v sha256sum >/dev/null 2>&1 || sha256sum() { shasum -a 256 "$@"; }   # macOS

row() { printf '| %s | %s | %s |\n' "$1" "$2" "$3" >> "$SUMMARY"; printf '  %-9s %-44s %s\n' "$1" "$2" "$3"; }
skip() { row "$1" "$2" "SKIPPED: $3"; setst $1 SKIPPED; }
cmpf() {  # step, label, regenerated, expected
  if [ ! -f "$3" ]; then row "$1" "$2" "FAILED: not produced"; setst $1 FAILED; return 1; fi
  if cmp -s "$3" "$4"; then row "$1" "$2" "IDENTICAL"; else
    diff "$4" "$3" > "$3.diff" 2>&1; row "$1" "$2" "DIFFERS ($(grep -c '^[<>]' "$3.diff") lines; $3.diff)"; setst $1 DIFFERS; fi
}

step_verify() {
  echo "== verify: frozen files match their timestamped / registered manifests"
  local ok=1
  local na; na=$(cd docs/registry/na-2026-09-22-v1 && sha256sum -c MANIFEST 2>/dev/null)
  if (cd docs/registry/na-2026-09-22-v1 && sha256sum --quiet -c MANIFEST.sha256) && grep -q 'predictions.csv: OK' <<< "$na"; then
    row verify "(n,a) registry na-2026-09-22-v1 predictions" "IDENTICAL (sha256 in the stamped MANIFEST; README.md was amended after the stamp, known)"
  else row verify "(n,a) registry na-2026-09-22-v1 predictions" "FAILED"; ok=0; fi
  if (cd docs/registry/capture-v01-2026-09-24 && sha256sum --quiet -c MANIFEST.sha256); then
    row verify "capture registry capture-v01-2026-09-24" "IDENTICAL (MANIFEST.sha256.ots is its OpenTimestamps proof)"
  else row verify "capture registry capture-v01-2026-09-24" "FAILED"; ok=0; fi
  if (cd incognita/terra/data && sha256sum --quiet -c <(grep -E ' (frozen_np\.(pkl|json))$' MANIFEST_TERRA_CHANNELS.sha256)) \
     && [ "$(sha256sum incognita/terra/terra_model.py | cut -d' ' -f1)" = "$(grep ' terra_model.py$' incognita/terra/data/MANIFEST_TERRA_CHANNELS.sha256 | cut -d' ' -f1)" ]; then
    row verify "terra (n,p) frozen model + terra_model.py" "IDENTICAL (MANIFEST_TERRA_CHANNELS.sha256)"
  else row verify "terra (n,p) frozen model" "FAILED"; ok=0; fi
  # SHA256SUMS also lists files that are not distributed here: check the ones present
  local nb; nb=$(cd incognita/bench && while read -r h f; do [ -e "$f" ] && echo "$h  $f"; done < SHA256SUMS | tee "$W/bench_sums.txt" | wc -l | tr -d ' ')
  (cd incognita/bench && sha256sum --quiet -c "$W/bench_sums.txt") && row verify "benchmark result files ($nb present)" "IDENTICAL (incognita/bench/SHA256SUMS)" \
    || { row verify "benchmark result files" "FAILED"; ok=0; }
  [ $ok = 1 ] || setst verify FAILED
}

step_terra() {
  echo "== terra: (n,p) blind correction grid (frozen model) on 3 check targets"
  # the (n,p) correction was frozen on no-data engine curves with TALYS's stock E1 table (before INDEP_FIX), so the check uses it too
  local T=26-61,30-71,40-100 R="$W/terra/grid"
  if [ $ENGINE = 1 ]; then
    [ -d "${TALYS_DIR:-$HOME/opt/talys-src}/structure" ] || { skip terra "(n,p) grid" "no TALYS structure database (README quick start, TALYS_DIR)"; return; }
    "${PY[@]}" scripts/bestfit/engine_curves.py --arm nodata --e1 stock --out "$R/nodata" --only "$T" \
      --grid incognita/terra/data/grid_terra.json --cpus 0-2 --cc-cache "${INCOGNITA_CC_CACHE:-$HOME/.cache/incognita-cc}" \
      --no-ingredients > "$W/terra_engine.log" 2>&1 || { row terra "(n,p) grid" "FAILED engine (see $W/terra_engine.log)"; setst terra FAILED; return; }
  fi
  ls "$R/nodata"/*.npz >/dev/null 2>&1 || { skip terra "(n,p) grid" "no engine curves in $R/nodata; rerun with --with-engine (~3 CPU-minutes)"; return; }
  "${PY[@]}" -m incognita.terra.grid --root "$R" --only "$T" --out "$W/terra/grid_np_check.parquet" > "$W/terra.log" 2>&1 \
    || { row terra "(n,p) grid" "FAILED (see $W/terra.log)"; setst terra FAILED; return; }
  "${PY[@]}" - "$W/terra/grid_np_check.parquet" "$EXP/terra/grid_np_check.csv" <<'EOF' | while IFS='|' read -r lab res; do row terra "$lab" "$res"; done
import sys, numpy as np, pandas as pd
a = pd.read_parquet(sys.argv[1]); b = pd.read_csv(sys.argv[2])
for d in (a, b):
    d['E_key'] = d.E_MeV.round(9)                  # E_MeV = e_ev / 1e6 can differ in the last bit
m = a.merge(b.drop(columns='E_MeV'), on=['Z', 'A', 'E_key'], suffixes=('', '_pub'))
cols = ['recipe_mb', 'pred_mb', 'lo68_mb', 'hi68_mb', 'lo95_mb', 'hi95_mb']
rel = max(float(np.nanmax(np.abs(m[c] / m[c + '_pub'] - 1))) for c in cols) if len(m) else np.nan
ok = len(m) == len(b) and rel < 1e-6
print(f'(n,p) predictions, {m.groupby(["Z", "A"]).ngroups} targets / {len(m)} of {len(b)} points|' + ('MATCH' if ok else 'DIFFERS') + f' (max rel diff {rel:.1e}; the engine agrees to ~1e-11 across machines, so not byte-identical)')
EOF
}

step_npfix() {
  echo "== npfix: (n,p) correction re-derived on OUR E1 constant (C3-e1, a candidate not in the v0.1 library) on 3 check targets"
  local T=26-61,30-71,40-100 R="$W/npfix/grid"
  if (cd incognita/terra/data && sha256sum --quiet -c MANIFEST_NPFIX.sha256); then row npfix "C3-e1 frozen model + terra_model.py" "IDENTICAL (MANIFEST_NPFIX.sha256)"
  else row npfix "C3-e1 frozen model" "FAILED"; setst npfix FAILED; fi
  if [ $ENGINE = 1 ]; then
    [ -d "${TALYS_DIR:-$HOME/opt/talys-src}/structure" ] || { skip npfix "(n,p) C3-e1 grid" "no TALYS structure database (README quick start, TALYS_DIR)"; return; }
    # no --e1 flag: --arm nodata applies INCOGNITA's E1 constant 1.0425 by default
    "${PY[@]}" scripts/bestfit/engine_curves.py --arm nodata --out "$R/nodata" --only "$T" \
      --grid incognita/terra/data/grid_terra.json --cpus 0-2 --cc-cache "${INCOGNITA_CC_CACHE:-$HOME/.cache/incognita-cc}" \
      --no-ingredients > "$W/npfix_engine.log" 2>&1 || { row npfix "(n,p) C3-e1 grid" "FAILED engine (see $W/npfix_engine.log)"; setst npfix FAILED; return; }
  fi
  ls "$R/nodata"/*.npz >/dev/null 2>&1 || { skip npfix "(n,p) C3-e1 grid" "no engine curves in $R/nodata; rerun with --with-engine (~3 CPU-minutes)"; return; }
  "${PY[@]}" -m incognita.terra.grid --model e1 --root "$R" --only "$T" --out "$W/npfix/grid_np_check.parquet" > "$W/npfix.log" 2>&1 \
    || { row npfix "(n,p) C3-e1 grid" "FAILED (see $W/npfix.log)"; setst npfix FAILED; return; }
  "${PY[@]}" - "$W/npfix/grid_np_check.parquet" "$EXP/npfix/grid_np_check.csv" <<'EOF' | while IFS='|' read -r lab res; do row npfix "$lab" "$res"; done
import sys, numpy as np, pandas as pd
a = pd.read_parquet(sys.argv[1]); b = pd.read_csv(sys.argv[2])
for d in (a, b):
    d['E_key'] = d.E_MeV.round(9)
m = a.merge(b.drop(columns='E_MeV'), on=['Z', 'A', 'E_key'], suffixes=('', '_pub'))
cols = ['recipe_mb', 'pred_mb', 'lo68_mb', 'hi68_mb', 'lo95_mb', 'hi95_mb']
rel = max(float(np.nanmax(np.abs(m[c] / m[c + '_pub'] - 1))) for c in cols) if len(m) else np.nan
ok = len(m) == len(b) and rel < 1e-6
print(f'(n,p) C3-e1 predictions, {m.groupby(["Z", "A"]).ngroups} targets / {len(m)} of {len(b)} points|' + ('MATCH' if ok else 'DIFFERS') + f' (max rel diff {rel:.1e})')
EOF
}

step_speed() {
  echo "== speed: SPEED50C report from the shipped raw timings (re-timing needs stock TALYS and an idle machine)"
  local S=incognita/bench/speed
  "${PY[@]}" $S/bench.py report $S/results --raw $S/results/speed50c_raw.jsonl --dest "$W/speed_REPORT.md" > "$W/speed.log" 2>&1 \
    || { row speed "SPEED50C report" "FAILED (see $W/speed.log)"; setst speed FAILED; return; }
  cmpf speed "SPEED50C report (from shipped timings)" "$W/speed_REPORT.md" $S/results/speed50c_REPORT.md
}

step_capblind() {
  echo "== capblind: the blind capture table from the frozen per-cell exam file (docs/release/exam)"
  (cd docs/release/exam && sha256sum --quiet -c SHA256SUMS) || { row capblind "exam cells sha256" "FAILED: docs/release/exam/capture_blind_cells.parquet changed"; setst capblind FAILED; return; }
  "${PY[@]}" scripts/release/score_capture_blind.py docs/release/exam/capture_blind_cells.parquet "$W/CAPTURE_BLIND.md" > "$W/capblind.log" 2>&1
  cmpf capblind "blind capture table (5 rows)" "$W/CAPTURE_BLIND.md" "$EXP/capblind/CAPTURE_BLIND.md"
}

step_retro() {
  echo "== retro: retrodiction, ours vs our engine's no-data recipe, from the frozen rows (docs/release/exam)"
  (cd docs/release/exam && sha256sum --quiet -c SHA256SUMS) || { row retro "exam files sha256" "FAILED: docs/release/exam changed"; setst retro FAILED; return; }
  "${PY[@]}" scripts/release/score_retro.py docs/release/exam/retro_rows.parquet "$W/RETRO.md" > "$W/retro.log" 2>&1
  cmpf retro "retrodiction vs the recipe (286 rows)" "$W/RETRO.md" "$EXP/retro/RETRO.md"
  row retro "retrodiction vs TENDL of year Y (0.193)" "NOT REGENERATED: needs the TENDL-2015..2023 archives, which we do not redistribute ; uv run python -m incognita.bench.score leaderboard scores it from staged archives (REPRODUCE.md)"
}

step_tiers() {
  echo "== tiers: blind-tier interval coverage from the frozen held-out rows (docs/release/exam)"
  (cd docs/release/exam && sha256sum --quiet -c SHA256SUMS) || { row tiers "exam files sha256" "FAILED: docs/release/exam changed"; setst tiers FAILED; return; }
  "${PY[@]}" scripts/release/score_tiers.py docs/release/exam/tier_rows.parquet "$W/TIERS.md" > "$W/tiers.log" 2>&1
  cmpf tiers "blind-tier coverage 68 / 95 %" "$W/TIERS.md" "$EXP/tiers/TIERS.md"
}

exam_step() {  # step, label, scorer, input, expected-name
  (cd docs/release/exam && sha256sum --quiet -c SHA256SUMS) || { row "$1" "exam files sha256" "FAILED: docs/release/exam changed"; setst $1 FAILED; return 1; }
  "${PY[@]}" "scripts/release/$3" "docs/release/exam/$4" "$W/$5" > "$W/$1.log" 2>&1
  cmpf "$1" "$2" "$W/$5" "$EXP/$1/$5"
}
step_na() {
  echo "== na: (n,a) v1 recipe vs default TALYS on the three fresh sets (docs/release/exam)"
  exam_step na "(n,a) v1 vs default TALYS, fresh sets" score_na_v1.py na_v1_rows.parquet NA_V1.md
}

step_stock() {
  echo "== stock: the TALYS port vs stock TALYS on the channel-scoreboard rows (docs/release/exam)"
  exam_step stock "engine vs stock TALYS, 6 channels" score_stock.py stock_rows.parquet STOCK.md
}

step_measure() {
  echo "== measure: the measure-next ranking from the frozen inputs (docs/release/exam)"
  (cd docs/release/exam && sha256sum --quiet -c SHA256SUMS) || { row measure "exam files sha256" "FAILED: docs/release/exam changed"; setst measure FAILED; return; }
  "${PY[@]}" scripts/release/measure_next.py docs/release/exam "$W/MEASURE_NEXT.csv" > "$W/measure.log" 2>&1
  cmpf measure "MEASURE_NEXT.csv (188 targets)" "$W/MEASURE_NEXT.csv" docs/release/MEASURE_NEXT.csv
}

step_nostruct() {
  echo "== nostruct: nuclei with no structure data, count and out-of-fold interval coverage (docs/release/exam)"
  (cd docs/release/exam && sha256sum --quiet -c SHA256SUMS) || { row nostruct "exam files sha256" "FAILED: docs/release/exam changed"; setst nostruct FAILED; return; }
  "${PY[@]}" scripts/release/score_nostruct.py docs/release/exam "$W/NOSTRUCT.md" > "$W/nostruct.log" 2>&1
  cmpf nostruct "no-structure count + interval 66 / 95 %" "$W/NOSTRUCT.md" "$EXP/nostruct/NOSTRUCT.md"
}

step_cleanretrain() {
  echo "== cleanretrain: OLD vs CLEAN (69 datasets dropped) on the DEV exam (docs/release/exam)"
  exam_step cleanretrain "clean retrain, DEV deltas" score_clean_retrain.py clean_retrain_rows.parquet CLEAN_RETRAIN.md
}

step_interp() {
  echo "== interp: shipped INTERPOLATED interval coverage by chart distance (docs/release/exam)"
  exam_step interp "INTERPOLATED interval by distance" score_interp_interval.py interp_interval_rows.parquet INTERP_INTERVAL.md
}

step_np() {
  echo "== np: (n,p) learned correction on the fresh set, and its intervals (docs/release/exam)"
  (cd docs/release/exam && sha256sum --quiet -c SHA256SUMS) || { row np "exam files sha256" "FAILED: docs/release/exam changed"; setst np FAILED; return; }
  "${PY[@]}" scripts/release/score_np.py docs/release/exam "$W/NP.md" > "$W/np.log" 2>&1
  cmpf np "(n,p) fresh set + intervals" "$W/NP.md" "$EXP/np/NP.md"
}

need_entry() {  # the EXFOR master in $INCOGNITA_MAIN/raw/exfor/entry.zip, fetched ONCE with --download (used by curation and registry)
  [ -f "$INCOGNITA_MAIN/raw/exfor/entry.zip" ] && return 0
  [ $DOWNLOAD = 1 ] || return 1
  echo "  fetching the EXFOR master (IAEA, ~380 MB) into $INCOGNITA_MAIN/raw/exfor/"
  "${PY[@]}" data/ingest/download.py --only exfor_entry_current > "$W/download_exfor.log" 2>&1 && [ -f "$INCOGNITA_MAIN/raw/exfor/entry.zip" ]
}

step_curation() {
  echo "== curation: regenerate the library-free curation register v2 from EXFOR and compare with data/curation"
  # the two curated EXFOR tables ship in data/curation/inputs (a copy under $INCOGNITA_MAIN wins); EXFOR, its capture staging and RIPL-4 are fetched
  need_entry || { skip curation "curation register v2" "needs the EXFOR master: rerun with --download, or: uv run python data/ingest/download.py --only exfor_entry_current"; return; }
  if [ ! -f "$INCOGNITA_MAIN/staging/exfor_capture_Z26-92.parquet" ]; then
    [ $DOWNLOAD = 1 ] || { skip curation "curation register v2" "needs the staged capture table: uv run python -m data.ingest.exfor --subset capture --zmin 26 --zmax 92 (or --download)"; return; }
    "${PY[@]}" -m data.ingest.exfor --subset capture --zmin 26 --zmax 92 > "$W/stage_capture.log" 2>&1 || { row curation "EXFOR capture staging" "FAILED (see $W/stage_capture.log)"; setst curation FAILED; return; }
  fi
  if [ ! -f "$INCOGNITA_MAIN/raw/ripl4/RIPL-4/resonances/resonances_L0.dat" ]; then
    [ $DOWNLOAD = 1 ] || { skip curation "curation register v2" "needs RIPL-4: uv run python data/ingest/download.py --only ripl4 (or --download)"; return; }
    "${PY[@]}" data/ingest/download.py --only ripl4 > "$W/download_ripl4.log" 2>&1 || { row curation "RIPL-4 download" "FAILED (see $W/download_ripl4.log)"; setst curation FAILED; return; }
  fi
  (cd data/curation/inputs && sha256sum --quiet -c SHA256SUMS) || { row curation "shipped curation inputs" "FAILED: data/curation/inputs changed"; setst curation FAILED; return; }
  local O="$W/curation"; rm -rf "$O"; mkdir -p "$O"
  CURATION_OUT="$O" "${PY[@]}" -m incognita.curation.build --out "$O" > "$W/curation.log" 2>&1 || { row curation "register build" "FAILED (see $W/curation.log)"; setst curation FAILED; return; }
  local n=0 bad=""; for f in "$O"/*; do b=$(basename "$f"); n=$((n+1)); cmp -s "$f" "data/curation/$b" || bad="$bad $b"; done
  if [ -z "$bad" ]; then row curation "curation register v2 ($n files, 590 decisions)" "IDENTICAL"; else row curation "curation register v2" "DIFFERS:$bad"; setst curation DIFFERS; fi
}

step_vault() {
  echo "== vault: the registered read of folds 6-7, shipped library-value-free model vs the release candidate (docs/release/exam)"
  exam_step vault "vault read, folds 6-7" score_vault.py vault_rows.parquet VAULT.md
}

step_final674() {
  echo "== final674: the sealed coverage test of the shipped interval (674 post-2012 bins, 51 nuclei, blind protocol)"
  local R=docs/release/uq/final674_rows.parquet
  [ -f "$R" ] || { skip final674 "FINAL-674 coverage table" "$R is not in this checkout"; return; }
  "${PY[@]}" -m incognita.uq.calibration_report "$R" --by region fold --out "$W/FINAL674.md" > "$W/final674.log" 2>&1
  cmpf final674 "FINAL-674 coverage (sealed test)" "$W/FINAL674.md" "$EXP/final674/FINAL674.md"
}

step_retromeasured() {
  echo "== retromeasured: the MEASURED-tier interval on post-cutoff measurements (sealed time split, 286 rows)"
  local R=docs/release/uq/retro_measured_rows.parquet
  [ -f "$R" ] || { skip retromeasured "RETRO-MEASURED coverage" "$R is not in this checkout"; return; }
  "${PY[@]}" scripts/release/score_retro_measured.py "$R" "$W/RETRO_MEASURED.md" > "$W/retromeasured.log" 2>&1
  cmpf retromeasured "RETRO-MEASURED coverage (sealed)" "$W/RETRO_MEASURED.md" "$EXP/retromeasured/RETRO_MEASURED.md"
}

step_registry() {
  echo "== registry: score the prospective registries against today's EXFOR (new measurements only)"
  local Z="$W/registry/entry.zip"; mkdir -p "$W/registry"
  if [ ! -f "$Z" ]; then
    need_entry || { skip registry "registry scores" "no EXFOR entry.zip; rerun with --download (IAEA, ~380 MB, fetched once into \$INCOGNITA_MAIN/raw/exfor)"; return; }
    cp "$INCOGNITA_MAIN/raw/exfor/entry.zip" "$Z"
  fi
  local nd=(); [ -f "$Z" ] && nd=(--no-download)
  mkdir -p "$W/registry/na" "$W/registry/capture"; [ -f "$Z" ] && cp -n "$Z" "$W/registry/na/entry.zip" && cp -n "$Z" "$W/registry/capture/entry.zip"
  "${PY[@]}" scripts/registry/score_na_registry.py --registry docs/registry/na-2026-09-22-v1 --watch "$W/registry/na" "${nd[@]}" > "$W/registry_na.log" 2>&1 \
    && row registry "(n,a) registry scores" "RAN: $W/registry/na/REPORT.md (new data, not a fixed table)" \
    || { row registry "(n,a) registry" "FAILED (see $W/registry_na.log)"; setst registry FAILED; }
  local RIV=(); if [ -f "$INCOGNITA_EVALUATED/jendl5.parquet" ] || [ -f "$INCOGNITA_EVALUATED/tendl2025.parquet" ]; then
    "${PY[@]}" scripts/registry/build_capture_rivals.py --registry docs/registry/capture-v01-2026-09-24 --out "$W/registry/rivals" --evaluated "$INCOGNITA_EVALUATED" > "$W/registry_rivals.log" 2>&1 && RIV=(--rivals "$W/registry/rivals")
  else row registry "capture registry rivals" "SKIPPED: no staged libraries in \$INCOGNITA_EVALUATED; the registry is scored alone (we do not ship library values)"; fi
  "${PY[@]}" scripts/registry/score_capture_registry.py --registry docs/registry/capture-v01-2026-09-24 "${RIV[@]}" \
    --watch "$W/registry/capture" "${nd[@]}" > "$W/registry_capture.log" 2>&1 \
    && row registry "capture registry scores" "RAN: $W/registry/capture/REPORT.md (new data, not a fixed table)" \
    || { row registry "capture registry" "FAILED (see $W/registry_capture.log)"; setst registry FAILED; }
}

for s in "${STEPS[@]}"; do
  if declare -F "step_$s" >/dev/null; then "step_$s"; else echo "unknown step: $s" >&2; exit 2; fi
done
cat >> "$SUMMARY" <<'EOF'

Tables in README.md that this script does NOT regenerate yet (their inputs or code are not in the repository): see
docs/release/REPRODUCE.md, section "Not reproducible from this repository yet".
EOF
echo; echo "summary: $SUMMARY"
[ -z "$FAILS" ] || { echo "FAILED:$FAILS" >&2; exit 1; }
exit 0
