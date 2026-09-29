# Prospective registry: how the chain works and how to submit

A registry entry is a prediction frozen before the measurement exists: a number, an interval, the model version and
the rule by which it will be scored. The registries here are chained in `CHAIN.jsonl`
(`python -m incognita.bench.registry verify` re-hashes every file, every row and every link).

| link | registry | frozen | entries | independent time witness | caveats (in the link) |
|---|---|---|---|---|---|
| 1 | `blind-2026-09-13-v0` | 2026-09-13 | 2,524 capture nuclei | OpenTimestamps (Bitcoin) | predates the shipped model; **not distributed in this preview** (the chain link is kept so the chain verifies) |
| 2 | `na-2026-09-22-v1` | 2026-09-22 | 1,881 rows: 171 (n,α) targets × 11 energies | OpenTimestamps, Bitcoin blocks 968199 / 968205 | README.md edited after hashing (original in git 7c46c4f7) |
| 3 | `capture-betaoslo-2026-09-23-v1` | 2026-09-23 | 48 rows (Sr-92..95) | none yet | a research registry; **not distributed in this preview** (link kept) |

Chain head after link 3: `285d208473e77a11cb3419a178276f8714e4ba5a738ac31632374533d2ff2a97`.
Anchored proofs: `ots/anchored/`. The proofs next to the registries are the earlier pending ones. The capture registry of the
shipped model, `capture-v01-2026-09-24`, carries its own OpenTimestamps proof and is not yet a chain link.

## What the chain proves, and what it does not
It proves integrity and order: no frozen byte, row or link can change without `verify` failing. It does not prove time.
Time comes only from witnesses outside our control: the OpenTimestamps Bitcoin attestations of links 1-2, and for
link 3 nothing yet. **Every append must be followed by a public witness of the new head.**

Proposed witness procedure (not yet done):
1. OpenTimestamps: `pip install opentimestamps-client`. `ots stamp` on a file holding
   the head hash, `ots upgrade` a few hours later. Only the hash leaves the machine.
2. A signed git tag on the commit that appends the link: `git -c gpg.format=ssh -c user.signingkey=~/.ssh/id_ed25519.pub
   tag -s registry-chain-3 -m "INCOGNITA registry chain head 285d2084..."` Pushing the
   tag to the public repository makes the host's timestamp a second witness.
3. A public post of the head hash (GitHub release note or issue, and a Zenodo record at v0.1), so that the hash is held by
   parties other than us.

## How an outside group submits
1. Make a directory `docs/registry/<group>-<YYYY-MM-DD>-<tag>/` with `predictions.csv` in the format the v1 registries use
   (`capture-betaoslo-2026-09-23-v1/predictions.csv`; background in `FORMAT.md`: one row per nuclide × quantity × energy / kT: prediction, 68 % and 95 % half-widths in log10 units,
   regime, model version, freeze date), a `README.md` stating the scoring rule, and `entry_hash` =
   sha256 of each row's JSON (`json.dumps(row_without_entry_hash, sort_keys=True)`).
2. Write `MANIFEST` (`sha256sum README.md predictions.csv > MANIFEST`) and `MANIFEST.sha256` (`sha256sum MANIFEST`).
3. Witness `MANIFEST.sha256` yourself BEFORE sending it (OpenTimestamps, a public post, a DOI). We cannot vouch for
   your time; your witness does.
4. Open a pull request. We check it and append the link without changing your files:
   `python -m incognita.bench.registry append <dir> --freeze-date ... --appended ... --witness "..."`, then witness the new head.
5. Scoring: when a measurement appears in EXFOR, `scripts/registry/score_capture_registry.py` /
   `score_na_registry.py` score every chained registry with the rule its README froze, next to the libraries.
   Predictions outside a registry can be scored any time on the frozen benchmark tracks (`docs/release/BENCHMARK.md`),
   but those are not prospective.
