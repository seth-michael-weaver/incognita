"""Curation layer (blueprint §4.3): units, standards, discrepancy model, trust scores.

* :mod:`data.curate.units` / :mod:`data.curate.standards` — WP-09/WP-12 steps 1–2.
* :mod:`data.curate.discrepancy` — per-(nuclide, reaction, bin) scatter model (GMA-like).
* :mod:`data.curate.quality_model` — per-dataset trust in [0, 1] (rule v0).
* :mod:`data.curate.review_log` — the human-review table and its decisions.

Regenerate everything with ``uv run python -m data.curate.quality_model``.
"""
