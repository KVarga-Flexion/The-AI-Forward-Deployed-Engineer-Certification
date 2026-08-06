.PHONY: help setup mirrors check execute nb clean

help:
	@echo "setup     install the root env (uv sync)"
	@echo "mirrors   regenerate every .ipynb from its marimo .py"
	@echo "check     what CI runs: mirrors, pins, deps, links, tests"
	@echo "execute  actually RUN every notebook, both .py and .ipynb"
	@echo "nb F=path open a notebook in its own sandbox (no root env needed)"

setup:
	uv sync

mirrors:
	uv run python scripts/mirrors.py --write

check:
	uv run python scripts/mirrors.py --check
	uv run python scripts/check_links.py
	uv run --group dev python scripts/check_manifests.py
	uv run python scripts/check_helpers.py
	uv run --group dev python -m pytest tests/ -q

# Runs every notebook in both formats. Minutes, not seconds, so it is not
# part of `check` -- but it is the only thing that proves they work.
#   make execute F=04_Retrieval    to scope it to one week
execute:
	uv run --group dev python scripts/check_execute.py $(F)

# Open any notebook standalone, using only its PEP 723 inline dependencies.
#   make nb F=01_Product_Engineering/sessions/S1_Enterprise_Dev_Environment.py
nb:
	uv run marimo edit --sandbox $(F)

clean:
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
