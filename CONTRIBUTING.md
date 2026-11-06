# Contributing to BoxGraph

Read `docs/minimalist_design/` before changing anything; the design wins over
the code. `docs/DECISIONS.md` records the choices the design leaves open; add
to it when you make one.

## Rules for the code

- `boxgraph/` is generic: never name a field, a model, a quantity or a paper
  in it (principle 12). Field content lives only in `corpora/<name>/`.
- Results are produced, never asserted: nothing computed is written into a
  record; the build derives it. Verdicts are computed when asked.
- Nothing is corrected or overwritten. A printed value stays as printed.
- Builds are deterministic and order-independent: sort everything.
- Papers are copyrighted: never commit a PDF, page text, page image or figure
  crop (`corpus/` and `corpora/*/records/*/{text,pages,figwork}/` are
  ignored). Records
  hold only short quotes that locate a value, and our own code and numbers.

## Working method

- Test first. Add or change a test in `tests/`, see it fail, then change the
  code. Every test has a one-line docstring saying what it checks; it feeds
  `docs/TESTS.md`.
- `make check` must pass before a commit: ruff, pytest, and
  `python tools/test_catalog.py --check` (run `make docs` to regenerate).
- Fixtures in `tests/fixtures/` are small hand-written records; extend them
  rather than writing records inside tests.

## The reading layer

`pipeline/` runs headless agent jobs through `pipeline/orchestrator.py`; each
job is gated by the validator. Prompts are in `pipeline/prompts/`; change the
guide, not the records, when agents get something systematically wrong.

## Commands

```bash
.venv/bin/python -m pytest -q
.venv/bin/boxgraph validate corpora/motor_clutch/records/bell1978
.venv/bin/boxgraph build corpora/motor_clutch/records --out build/motor_clutch --cache build/cache
make build site CORPUS=motor_clutch     # the same build with its overview text, copied to site/motor_clutch/
.venv/bin/python -m pipeline.add path/to/paper.pdf --id smith2015 --corpus motor_clutch
.venv/bin/python -m pipeline.run_papers --corpus motor_clutch --plan
.venv/bin/python -m pipeline.run_papers --corpus motor_clutch --papers smith2015
.venv/bin/python -m pipeline.run_papers --corpus cardio --plan   # every corpus lives in corpora/<name>/
```
