# Contributing

- Licences: code contributions are accepted under Apache-2.0; data contributions under CC-BY-4.0.
- Open an issue before larger changes, and say which claim, table or file it affects.
- Before a pull request: `uv sync --extra dev`, then `uv run ruff check .` and `uv run pytest` must pass.
  If you change anything under `docs/release/exam/`, `docs/release/expected/` or the scorers, `bash scripts/reproduce.sh`
  must still report IDENTICAL (or the pull request must explain the change).
- Never commit downloaded inputs (`raw/`, `staging/`, the TALYS structure database) or evaluated-library values. Libraries
  may be used only as scoring baselines built from files each user downloads.
- Frozen registries in `docs/registry/` and exam files hashed in `SHA256SUMS` files are never edited in place.
- Good first contributions: reviewing a discrepant EXFOR dataset against the curation register
  (`docs/release/CURATION_REGISTER.md`), or reporting a new measurement that scores a registry prediction.
