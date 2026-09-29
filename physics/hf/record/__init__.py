"""CREC: the chart set-up record (ROUTE100's WP4).

A warm chart worker (WARM0, `physics.hf.warmrun`) keeps, per nuclide, every cache a fit step does
not reach: incident and inverse transmissions, coupled-channels and DWBA results, the direct and
giant-resonance blocks. This package writes those caches as one flat, mmap-able file per nuclide
plus a chart index, and seeds them back into a fresh worker, so a warm run no longer needs the
cold run in the same process.

* `codec`   -- a cached value (dataclasses, dicts, numpy / torch arrays) as a JSON skeleton plus
               flat array blobs; no pickles, only `physics.hf` classes are rebuilt.
* `store`   -- the file format (header + aligned, deduplicated, optionally sparse blobs), the
               chart index, and the mmap loader.
* `caches`  -- which caches a record holds, how they are captured after a run and seeded into
               a new one, and the record key (what invalidates a record).

The key. A record holds only caches outside WARM0's taint set (`warmrun.DROP_LRU`, `DROP_DICTS`,
`DROP_ATTRS`), so a PARAMWIRE parameter set (`ChainedFull(params=)`, `density.overrides.FIT_KEYS`)
does not invalidate it: those caches are value-keyed by the parameters they read and are
recomputed. What does invalidate a record: the nuclide and declared grid, the taint set itself,
the recorded cache list, the port's source (every `physics/hf` module and native kernel outside
this package) and a `Cascade` with DIFFPARAM density / optical overrides, which the recorded
transmissions do not carry.

TALYS: none (worker cache policy)
Test: scripts/hf_route100_record.py verify
"""
