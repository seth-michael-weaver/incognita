# Convenience targets; each is a thin wrapper over uv.

.PHONY: help sync lint test native reproduce

help:
	@echo "make sync        install the environment (uv sync --extra dev)"
	@echo "make lint        ruff check"
	@echo "make test        run the test suite"
	@echo "make native      build the optional C kernels (needs gcc); the engine runs without them, more slowly"
	@echo "make reproduce   scripts/reproduce.sh: regenerate the benchmark tables and compare them with docs/release/expected"

sync:
	uv sync --extra dev

lint:
	uv run ruff check .

test:
	uv run pytest

native:
	@command -v cc >/dev/null 2>&1 || command -v gcc >/dev/null 2>&1 || { echo "no C compiler (cc/gcc) found: the engine still runs without the native kernels, in pure Python"; exit 0; }
	@failed=""; for s in scripts/build_*.sh; do echo "== $$s"; bash "$$s" || failed="$$failed $$s"; done; \
	if [ -n "$$failed" ]; then echo; echo "native kernels NOT built:$$failed"; echo "the engine runs without them (pure-Python fallback)"; else echo "all native kernels built"; fi

reproduce:
	bash scripts/reproduce.sh
