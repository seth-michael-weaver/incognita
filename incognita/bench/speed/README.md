# Speed: the TALYS port vs stock TALYS

Result, stated first (SPEED50C.md, one idle-laptop session, 20 nuclides x 20 energies, one pinned core, results equal to
1e-11): batch cold with the opt-in fused GPU kernel **15.3x** CPU (13.1x wall), CPU only ~10x, batch warm **21.5x**, one
nucleus per fresh process **5.1x**. The 50x goal was **not** reached. This hardware drifted 15-50 % between sessions, so
only ratios measured in one ABAB session are claims.

## Regenerate the published report from the raw timings (no downloads)

```bash
uv run python incognita/bench/speed/bench.py report incognita/bench/speed/results \
    --raw incognita/bench/speed/results/speed50c_raw.jsonl --dest out/speed_REPORT.md
diff out/speed_REPORT.md incognita/bench/speed/results/speed50c_REPORT.md    # identical (tested 2026-09-23)
```

## Run the benchmark yourself

Needs: stock TALYS built per `docs/talys-install.md` (`--talys-bin`, `$TALYS_BIN`, or `$TALYS_DIR/bin/talys`), this repo
with `uv sync` and `make native`, `taskset` (util-linux), an idle machine. The fused GPU arms need a CUDA torch.

```bash
uv run python incognita/bench/speed/bench.py --cpu 15 --repeats 2 --out "$PWD/out/speed"
# before/after in one session: check out an older commit with `git worktree add ../old <commit>`, uv sync + make native
# there, and add --repo base=../old --arms talys,base_cold,new_cold,base_batch,new_batch
```

`meta.json` records each repo's commit and whether its native engine library loaded; a timing without the native
kernels is ~4x slower and is not a valid result. SPEED50C's `base` and `b50b` arms were commits c423b78d and 1260ac1c.
The profile driver and the desktop accuracy gate were lab scripts and are not shipped (their results are in SPEED50C.md).
