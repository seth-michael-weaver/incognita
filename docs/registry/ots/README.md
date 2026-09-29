# OpenTimestamps proofs

`anchored/na-2026-09-22-v1.MANIFEST.sha256.ots` is the Bitcoin-anchored proof for the `MANIFEST.sha256` of the (n,α)
registry `../na-2026-09-22-v1/`. The proof next to that registry is the earlier pending one. Verify with
`ots verify` (opentimestamps-client) against a Bitcoin node or a block explorer. A proof shows that the manifest, and
therefore every file it hashes, existed by the time of the attesting block; it does not show when it was made.
