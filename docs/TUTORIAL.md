# Getting started

From a fresh clone to your own papers in the Synthesis. Each step says what it
needs and what you should see. The design behind it is in
[`minimalist_design/`](minimalist_design/README.md); this page is only how to
use it.

## 1. Install

Needs Python 3.11 or later, [uv](https://docs.astral.sh/uv/), and poppler
(`pdftotext`, `pdftoppm`, `pdfinfo`: `brew install poppler` on macOS,
`apt install poppler-utils` on Debian or Ubuntu).

```bash
git clone https://github.com/elejeune11/boxgraph-public && cd boxgraph-public
make install        # .venv with the exact versions in uv.lock
make check          # lint, tests and the test catalogue: should end with every test passing
```

## 2. Look at what is already there

`records/` holds one folder per source: what each paper prints, its models in
runnable form, and the comparisons between them. They validate without the
papers themselves:

```bash
.venv/bin/boxgraph validate records/erdmann2004 --no-run
```

`--no-run` checks the record's structure only: every value has a unit, a
quantity and a citation, every model names its inputs. Without it the models are
run as well; that needs the papers for any value read from a figure.

## 3. Supply the papers, code and data

Papers, released code and data are never committed: they belong to their
publishers and authors. List what the corpus needs and where each comes from:

```bash
.venv/bin/python -m pipeline.run_papers --missing
```

Put each PDF at the path shown (under `corpus/`, which git ignores), and released
code or data the same way. A build checks each code folder and data file against
the digest its record pins, so a different version is reported, not used.

## 4. Build the Synthesis

```bash
.venv/bin/boxgraph build records --out build --overview overview/content.yaml
```

The first build runs every model, including stochastic simulations with several
seeds at each refined time step: from a fresh clone it takes more than an hour
for sixteen sources, most of it in a few simulation-heavy papers. Later builds
reuse the cache in `build/cache/` (keyed by each model's code and inputs) and
take about a minute; only what changed runs again. Without the papers, figure
readings are checked for structure but not read, so comparisons that rest on
them have no verdict until the PDFs are in `corpus/`. It writes:

| File | What it is |
|---|---|
| `build/overview/index.html` | The page to start with, and to show others: the sources as a graph, case studies, a view per source |
| `build/report.html` | The full written review, every sentence traced to the records |
| `build/figures.html` | Every figure reading drawn on its figure, to check by eye |
| `build/synthesis.json` | Everything above as data |

Open `build/overview/index.html` in a browser.

## 5. Add your own papers

This step runs coding agents (the pipeline currently uses Claude Code), so it
needs the `claude` command, signed in.
Agents read each paper into a record, and every record must pass the validator
before it counts.

```bash
.venv/bin/python -m pipeline.add ~/Downloads/Smith2015.pdf --id smith2015 --pages 1-14 \
    --note "pages 9-14 are the supplement"
.venv/bin/python -m pipeline.attach ~/Downloads/smith_code.zip --id smith_code --kind software --papers smith2015
.venv/bin/python -m pipeline.run_papers --plan                 # what will run, with budget caps
.venv/bin/python -m pipeline.run_papers --papers smith2015,smith_code
```

A paper takes one to two hours and roughly $5-40 of agent time, most of it
reading figures; a relation between two papers, and then the check of each one's models against
the other's measurements, a few minutes and $0.3-2 each. The run
ends with a summary of what it spent and what, if anything, needs a person.
`--status` shows every job; a call that was stopped before reporting its cost is
listed with its tokens.

**If the run is stopped** (Ctrl-C, a closed laptop, a time limit on a cloud
machine), run the same command again: finished jobs are kept, and interrupted
ones carry on in their own sessions. Where a machine stops long processes (a
cloud session's time limit), schedule the same command to run again every hour
or so; a second copy refuses to start while one is running, so this is safe.

**If a job is parked** (it failed its gate on every attempt), read its transcript
in `pipeline_state/logs/`, fix what it says, and let it run again:
`python -m pipeline.run_papers --reset read:smith2015`.

## 6. Read the results

Afterwards, look at each new record's `audit.md`, `figures.md` and
`questions.yaml`, check its figure readings in `build/figures.html`, and read
its view in the overview. Commit the new records and `pipeline/completed.yaml`
(the ledger of finished jobs) together; never the papers.

To change what the overview says, edit `overview/content.yaml`: its
introduction, links and case studies. A case study names what each step shows
(`comparison: src/id`, `relation: src/id`, `cited: src/datum`,
`refinement: src/id`, `family: src/model`, `question: src/id`, ...), and the
build fills in the numbers.
