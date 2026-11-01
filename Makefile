# BoxGraph: common tasks. Run `make help`.
PY ?= .venv/bin/python
BG ?= .venv/bin/boxgraph

.PHONY: help install test lint docs check ingest plan read build report clean site

help:
	@echo "install   create .venv with the locked versions (uv.lock) and the dev and pipeline extras"
	@echo "test      run the test suite"
	@echo "lint      run ruff"
	@echo "docs      regenerate docs/TESTS.md and the design figures"
	@echo "check     lint + tests + docs freshness (what CI runs)"
	@echo "ingest    extract page text and images for the corpus in pipeline/papers.yaml"
	@echo "plan      what the pipeline would run for the corpus, with budget caps"
	@echo "read      run every job not yet done: read, audit, digitize, relate, build"
	@echo "build     validate and build every record into build/ (synthesis + report)"
	@echo "site      copy the built overview into site/, which GitHub Pages serves"
	@echo "clean     remove build outputs and caches"

install:  # the exact versions in uv.lock
	uv sync --locked --python 3.13 --extra dev --extra pipeline

test:
	.venv/bin/pytest -q  # as CI runs it: `python -m pytest` would add the project to the path and hide import errors

lint:
	$(PY) -m ruff check boxgraph pipeline tests tools

docs:
	$(PY) tools/test_catalog.py
	$(PY) docs/minimalist_design/figures/make_figures.py

check: lint test
	$(PY) tools/test_catalog.py --check

ingest:
	$(PY) -m pipeline.run_papers --stages ingest

plan:
	$(PY) -m pipeline.run_papers --plan

read:
	$(PY) -m pipeline.run_papers

build:
	$(BG) build records --out build --title "BoxGraph Synthesis"

clean:
	rm -rf build .pytest_cache

site:  # after a build: the overview, as GitHub Pages serves it
	mkdir -p site && rm -rf site/img && cp -r build/overview/. site/
