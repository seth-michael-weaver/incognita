# Registry v1 format (proposal, not built)

Goal: an AlphaFold-DB-style record that is falsifiable later — a specific number with a specific
uncertainty, committed to before the measurement, for a specific model version.

## One registry entry

```
nuclide_id        Z%03dN%03dM0 (matches series_table.csv convention, e.g. Z069N102M0 = Tm-171)
quantity          sigma_ng | macs            (differential capture, or Maxwellian-averaged)
grid              energy_eV list (sigma_ng) OR kT_keV list (macs) — the exact points scored
prediction        value per grid point, in barns or mb
interval_68       [lo, hi] per grid point (or a single log10_halfwidth if the grid shares one, as v0 does)
interval_95       [lo, hi] per grid point
model_version     repo commit hash + checkpoint files' sha256 (provenance.json pattern from v0)
regime            measured | interpolated_within_validated_distance | engine_only
                  (the chain-end exam, PLAN-ALPHAFOLD A2, defines "validated distance")
target_status     one of v0's status_at_freeze values, at freeze time
source_refs       proposal/INTC/DOI URLs this entry is racing against (from targets.csv)
freeze_timestamp  ISO date the manifest was hashed (not the git commit date — see below)
entry_hash        sha256 of this entry's canonical (sorted-keys) JSON, independent of the others
```

Row-level `entry_hash` lets someone verify one nuclide's prediction against the published manifest
without re-hashing the whole release; the manifest hash (below) is what actually gets timestamped.

## Hashing the file set

Same pattern as v0's `MANIFEST.sha256`/`provenance.json`, extended:
1. One canonical manifest file listing every release file with its own sha256 (grid tables, per-quantity
   parquet/csv, README, PROTOCOL, model checkpoints or at least their hashes) — sorted by path, LF line
   endings, no timestamps embedded in the hashed bytes themselves.
2. `MANIFEST.sha256` = sha256 of that manifest file. This single hash is the one that gets a public
   timestamp — never the raw predictions, so nothing about content leaks before the intended release.
3. Anyone can later run `sha256sum -c MANIFEST.sha256` to prove the release they're holding is
   bit-identical to the one that was stamped.

## Public timestamp options (repo stays private)

| option | pros | cons |
|---|---|---|
| OpenTimestamps (already used in v0) | free, no account, Bitcoin-anchored, `.ots` file is tiny and re-verifiable forever, only the hash ever leaves the machine | needs the upgrade step hours later; proof is only as legible as the tool (niche, needs `ots` client to check) |
| Public GitHub gist / public repo commit containing only the hash file | trivial, git commit time + hosting company's own timestamp is a second independent witness, human-readable | GitHub's own clock is not independently auditable; gist could in principle be edited/deleted (mitigated by also OpenTimestamping the gist's own commit) |
| Zenodo DOI for a one-page "hash certificate" | citable, permanent, institutional weight, works well alongside an eventual data-release DOI | manual upload step, DOI minting takes minutes-hours, mildly heavier process for something this small |
| arXiv or OSF preprint of the hash + methodology note | citable, discoverable by the field, doubles as the "here is our protocol" announcement | slower (moderation/versioning), overkill if this is the only content |
| Do all three (OpenTimestamps + gist + eventual Zenodo/arXiv on public release) | belt-and-suspenders, cheap since it's a few KB total | none — this is the recommended combination |

Recommendation: OpenTimestamps immediately (as v0 already does) for the cheap cryptographic proof,
plus a public gist of just `MANIFEST.sha256` + the OTS file for a second, human-checkable witness, the
day registry v1 is frozen. Zenodo/arXiv can follow once the repo itself goes public and the registry
is presented as a package, not before — no need to mint a DOI for every incremental freeze.
