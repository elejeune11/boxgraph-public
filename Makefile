# BoxGraph: common tasks. Run `make help`.
PY ?= .venv/bin/python
BG ?= .venv/bin/boxgraph
# Every corpus lives in corpora/<name>/; the corpus targets take CORPUS=<name> (motor_clutch, cardio, ...)
CORPUS ?=
RUN = $(PY) -m pipeline.run_papers --corpus $(CORPUS)
RECORDS = corpora/$(CORPUS)/records
OUT = build/$(CORPUS)
CONTENT = corpora/$(CORPUS)/overview.yaml
SITE = site/$(CORPUS)
NEED = @test -n "$(CORPUS)" || { echo "name a corpus: make $@ CORPUS=<name>, one of: $$(ls corpora)"; exit 2; }

.PHONY: help install test lint docs check ingest plan read build report clean site

help:
	@echo "install   create .venv with the locked versions (uv.lock) and the dev and pipeline extras"
	@echo "test      run the test suite"
	@echo "lint      run ruff"
	@echo "docs      regenerate docs/TESTS.md and the design figures"
	@echo "check     lint + tests + docs freshness (what CI runs)"
	@echo "ingest    extract page text and images for a corpus (corpora/<name>/papers.yaml)"
	@echo "plan      what the pipeline would run for a corpus, with budget caps"
	@echo "read      run every job not yet done: read, audit, digitize, relate, validate, build"
	@echo "build     validate and build a corpus's records into build/<name>/: Synthesis, report, overview"
	@echo "site      copy the built overview into site/<name>/, which GitHub Pages serves (run build first)"
	@echo "clean     remove build outputs and caches"
	@echo "(ingest, plan, read, build and site take CORPUS=<name>: make build site CORPUS=motor_clutch)"

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
	$(NEED)
	$(RUN) --stages ingest

plan:
	$(NEED)
	$(RUN) --plan

read:
	$(NEED)
	$(RUN)

build:
	$(NEED)
	$(BG) build $(RECORDS) --out $(OUT) --cache build/cache --save-readings --title "BoxGraph Synthesis" $(if $(wildcard $(CONTENT)),--overview $(CONTENT))

clean:
	rm -rf build .pytest_cache

site:  # after a build: the overview, as GitHub Pages serves it (site/index.html is the landing page, kept by hand)
	$(NEED)
	mkdir -p $(SITE) && rm -rf $(SITE)/img && cp -r $(OUT)/overview/. $(SITE)/
