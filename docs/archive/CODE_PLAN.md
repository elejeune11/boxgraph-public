# Code as a source: plan

Status: the plan as written before v0.6. Part of it was built, test first;
the choices that stand are in DECISIONS.md (Code and data as sources), which
wins where it differs from this plan. The first use was Andreu 2021's MATLAB
code and source data.

**Built (v0.6):**

- code and data as sources of their own (kinds `software` and `dataset`),
  each read into its own record by a `read:<id>` job after its papers;
- registering them with `python -m pipeline.attach` (a zip, tar.gz, folder or
  data file; archives unpacked safely), as entries in the same corpus list as
  the papers (`papers.yaml`, with `papers:` naming the papers they belong to);
- citations by file and lines (code) and by sheet and cells (data), checked
  against the files when they are present;
- pinning by a digest of the files' contents (`boxgraph digest`), and a record
  that is unsound when the files no longer match;
- `software: true` on a model that runs the source's own Python code, with
  outputs of origin *run*; other languages ported to Python by the reader;
- runs in a fresh interpreter, without network where the system allows it
  (`unshare -rn`), with a time limit;
- a paper related to its own code or data by a relation job; cited values
  checked between them, and figure readings measured against source data.

**Not built:** `pipeline.add_code` and `add --code`; a separate code list
(`corpora/<name>/code.yaml`); fetching a repository by commit; the search job
(`findcode`) and its candidates ledger; matching code to papers without
`--papers`; the "triangle" classification; a memory limit; running C, C++,
MATLAB, Octave, R or Julia code. The sections below keep the plan as it was
written.

## The idea in one paragraph

An author's code is a **Source** of kind *software*, read into a record of
its own, exactly as a paper is. Its model is a chart in ModelAtlas like any
other; the values written in it are data cited by file and line; what it
outputs has the origin *run* (by a source's own software). The design
already names both (02-boxgraph.md, Source and Origins), so nothing in it
changes. The link between a paper and its code is not believed: it is a
relation between the paper's model and the code's model, tested by running
both on the same inputs. A paper then has three things that should agree:
what it prints, the model its text states, and the code its authors ran.

## Why a record of its own

- One repository often serves several papers (a lab's simulator, used and
  extended over years), and one paper may use several repositories.
- Code has versions; a record pins one commit. Two versions are two
  records, joined by relations, never merged.
- The paper's record stays what the paper prints. Nothing is corrected
  from the code, and nothing in the code is corrected from the paper.

## What a code record holds

```
corpora/motor_clutch/records/oddelab_clutch/
  source.yaml       kind: software; url; commit (full SHA); licence (SPDX, or
                    "none stated"); language; date of the commit; authors;
                    found: stated | proposed, with the evidence (below)
  models/<m>/       model.yaml + model.py: our adapter that calls the code's
                    own entry point; outputs have origin run
  quantities.yaml   as for a paper
  data.yaml         values written in the code (defaults, parameter files),
                    origin reported, cited by file, lines and a short quote
  runs.yaml         the code run on its own defaults and on each linked
                    paper's inputs
  comparisons.yaml  see the triangle below
  relations.yaml    same_as (or approximated_by) to each linked paper's model
  questions.yaml    as for a paper
```

Small generic additions to `boxgraph/` (no field names):

- `Source`: `url`, `version`, `licence`, `language`, required for software.
- `Citation`: `file` and `lines`, for a source that is not paged. The
  validator checks the quote against the checked-out file at the pinned
  commit, as it checks a page quote against the page text.
- `Model`: `software: <source id>` marks a model that runs a source's own
  code; its outputs take the origin *run* instead of *predicted*.

No new relation kind: "this code implements that paper's model" is a
*same as* relation with its mapping, tested like every other.

## The triangle

For each linked paper the build compares three things:

| | text model reproduces the print | code reproduces the print | reading |
|---|---|---|---|
| 1 | yes | yes | agree |
| 2 | no | yes | the text leaves out or misstates something the code does: the difference is a finding (unstated model, or possible error) |
| 3 | yes | no | the code has moved on from the paper, or a different version was used: the commit date is reported |
| 4 | no | no | the printed result itself is in question |

Together with:

- **Values:** each parameter in the code against the paper's printed value
  (a *consistency* comparison). This needs no running, so it is done even
  when the code cannot be run.
- **Our reading:** the relation test between our model and the code's
  model checks the reader as much as the paper.

The Synthesis and the explorer show the triangle per paper, with code as
its own kind of node.

## Adding code

Code is added the way papers are: uploaded, and registered with one
command. It can come with a paper, on its own, or after its papers.

```bash
python -m pipeline.add_code path/to/code.zip --id oddelab_clutch --papers chan2008,bangasser2013
python -m pipeline.add_code path/to/folder --id smith_sim
python -m pipeline.add_code https://github.com/lab/repo@<commit> --id lab_repo
python -m pipeline.add paper.pdf --id smith2015 --code path/to/code.zip
```

- **The code list.** `corpora/<name>/code.yaml` lists code beside the papers in
  `corpora/<name>/papers.yaml`: an id; the upload under `corpus/<name>/code/<id>/` or a
  URL; the version; the papers it is linked to; and a note. It is checked
  like the paper list: bad or duplicate ids, a missing file, an unknown
  paper.
- **The version.** An upload is pinned by the SHA-256 of its contents, a
  repository by its commit. An archive is unpacked safely: no paths outside
  its folder, no links, and a size limit.
- **The licence** is read from the code's LICENSE file, or recorded as
  "none stated".
- **Run on its own.** `run_papers` picks up new code as it picks up new
  papers, and the ledger keeps finished code jobs from running again.
  Adding code to papers that are already read runs only the new code's
  jobs and its relations.

## Linking code to papers

| How | Provenance | Evidence |
|---|---|---|
| you name the papers (`--papers`) | stated (by you) | the code list |
| the paper links the code | stated | its code or data availability statement, with the quote and page |
| the code names the paper | stated | a README or header citing the title or DOI, by file and line |
| matched | proposed | shared authors, matching parameter names and values, a commit or file date before publication |

Code added without `--papers` is matched against every record in the
atlas, as `candidate_pairs` matches papers. Each link only says which
models to test against each other: a link of any provenance becomes a
verified relation only by the running test.

## Finding code that was not uploaded

A search job looks for code a paper does not link: GitHub, the lab's
website, Zenodo, figshare, ModelDB and BioModels, by title, authors and
DOI. A repository it finds is taken only with at least two independent
kinds of evidence from the table above, and enters as *proposed*. Every
candidate, taken or rejected, goes into `corpora/<name>/code_candidates.yaml`
(committed) with its evidence, so the search is not repeated. This is the
optional route: uploads and stated links do not need it.

For a repository, the commit is the one the paper names. Otherwise it is
the last commit before the publication date, labelled as added, with the
newest commit as its alternative.

## Keeping it safe and legal

- **Never committed.** The code is kept under `corpus/<name>/code/<id>/` (the upload, or a
  checkout at the pinned commit), which is ignored, whatever its licence. Only
  our adapter, the record and short quotes are committed. The copyright
  guard test is extended to it. A build checks the code's hash and stops
  if it has changed; a missing repository checkout is fetched by commit, and
  a missing upload must be uploaded again.
- **Run in a box.** The authors' code is untrusted: every run is a
  subprocess in a fresh copy of the checkout, with no network
  (`unshare -n`), an environment without tokens, a time
  limit and a memory limit. The agent that reads code cannot push or use
  `gh`.
- **Runtimes.** Python (packages from PyPI) and C/C++ were planned. MATLAB,
  Octave, R and Julia are not assumed. Code that cannot be run still gets
  its values compared; its relation is *unverifiable*, with an open
  question naming the runtime. (As built, code in another language is
  ported to Python by the reader instead.)

## In the pipeline

```
read:p ─┬─ audit:p ── digitize:p ─────────┐
        └─ findcode:p (optional) ─┐       │
add_code ─────────────────────── code:c ──┴─ relate pairs ── build
```

- `code:<id>` runs for every entry in the code list, whether uploaded,
  linked or found.
- `findcode:<paper>`: optional and cheap. It reads the paper's statements, searches,
  and writes candidates with evidence. It writes no record.
- `code:<id>`: fetches if needed, reads the code, and writes the record: values with
  file and line citations, the adapter, runs, comparisons and the
  same-as relations to the linked papers. The gate is validate plus the
  relation test.
- Code records join `candidate_pairs` through their links. Both jobs go in
  the ledger, and the locks cover the paper and the code record.

## Tests first

The tests run against a synthetic pair built inside the test from a few
files: a paper (as in `pipeline/evals/synth_cluster`) and a small Python
repository in a local git repo. Two things are planted in it:

- one parameter whose value in the code differs from the paper's table;
- one result that the text's model misses and the code reproduces,
  because the code does something the text leaves out.

The expected findings are the value mismatch and triangle row 2.

The unit tests cover:

- the software source's fields;
- file and line citations checked against the checkout;
- origin *run* for models with `software:`;
- the sandbox: no network, no tokens, the time limit;
- the copyright guard over `corpus/<name>/code`;
- `add_code` and `add --code`: uploads, folders, URLs, the code list's checks
  and safe unpacking;
- matching code added without `--papers`;
- the candidates ledger;
- the job graph;
- the triangle classification;
- code nodes in the explorer.

The end-to-end check is the agent eval on the synthetic pair, then one real
paper whose code is public.
