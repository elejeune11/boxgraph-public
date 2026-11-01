# Implementation decisions

Choices the design documents leave open, made while building version 0.1.
Each can be revisited; the tests in `docs/TESTS.md` pin the current choice.

## Records

- **Storage.** Plain YAML and Python files in git, one directory per source.
  The build is a disposable function of the records (`build/`).
- **Ids** are local to a record; globally they are `<source-id>/<local-id>`.
- **Citations** use the PDF page number (1-based, as in `text/page-NNN.txt`),
  with the journal's printed page label recorded where visible.
- **Quotes** are checked against the page text, ignoring case, spacing and
  punctuation, mapping common OCR confusions, and accepting a fuzzy match of
  at least 0.8 for quotes of six or more characters. Paraphrase fails.
- **A table or curve** is one datum with an index condition. A run produces a
  curve by sweeping one input over the index of a printed table.
- **Readers** are named in `source.yaml` (principle 13). A second reading is a
  second record version; the audit job is a second reading of the same paper
  that may correct transcription errors and must log every change in
  `audit.md`.

## Printed values and verdicts

- Precision is half a unit in the last printed digit, including for integers
  with trailing zeros (`200` means 199.5–200.5).
- Powers of ten must be written with a caret (`1.3 x 10^-10`); superscripts
  are converted. A bare power of ten (`10^-5`) is an order of magnitude and
  gets no verdict.
- `≈`, `~`, "about", "of order", `<`, `>` mean no precision and no verdict.
- `v ± u` replaces the digit precision with the interval [v−u, v+u].
- A range `a to b` (or `a–b`) is the interval itself.
- Reproduced inside the interval; close when outside it by at most its own
  width; otherwise not reproduced (Figure 4).
- A value printed as a logarithm is compared in the printed scale.

## Models with randomness

- A model marked `stochastic` must take a `seed` setting. Each run repeats it
  with seeds seed, seed+1, ..., five times unless the run says `replicates`.
  The value is the mean; its sampling error is the standard error of the mean.
- The computed side of a verdict is the interval mean ± 2 standard errors,
  carried into the printed unit and scale by linearisation. Reproduced when it
  overlaps the printed interval; close when the gap is at most the printed
  width; otherwise not reproduced. Without sampling error this is exactly the
  Figure 4 rule.
- Refinements compare means.
- Cross-paper checks still run a model once; carrying replicates across
  papers is not done yet.

## Models and runs

- `model.py` defines `run(inputs, settings) -> dict`, computing in the
  model's declared port units; optional `symbolic()` returns sympy
  expressions in the same symbols and units.
- Model code runs in a separate `python -I` process with a timeout, and
  results are cached by the hash of (code, inputs, settings).
- Inputs are converted from a datum's unit and scale to the port's. A port
  accepts only the exact quantity it declares (principle 6).
- Conditions agree when every condition both values name has the same
  value (as printed, or equal after unit conversion). A condition named on
  one side only is noted. Disagreement blocks a comparison unless
  `conditions_ok` says why.
- **Refinement:** factors default to 1, 2, 4, 8. The series settles when the
  last two refinements differ by less than the tolerance (relative if
  written as a percentage). The paper's result belongs to the model only if
  the series settles *and* the value at the paper's setting is within the
  tolerance of the last refinement (principle 8). A first version checked
  only that the series settled; Chan 2008 showed why that is wrong: the
  soft-substrate flow settles near 47 nm/s, 38% below its value at the
  paper's 5 ms step.
- **Alternatives:** each alternative of each added input is run one at a time
  against the baseline, never in combination; only added inputs used by a
  run are varied.

## Figures

- **A figure reading is part of the record and is rebuilt.** `figures.yaml`
  records the page, crop (pixels at a stated dpi, 300 by default), plot box,
  axis calibrations as `[pixel, printed label]` marks, the curve's colour and
  a seed point on it, and the x positions to read (or markers). Every build
  renders the page region again and reads it, so a reading cannot drift from
  its calibration.
- **Calibration** fits value (or log10 value) against pixel by least squares.
  Two marks calibrate but cannot catch a mislabelled tick, so they warn; a
  misfit over 1.5 px is an error, because it means a label is on the wrong
  tick.
- **Ticks** are found as short perpendicular runs adjoining the axis line,
  measured outward, so detection works at any resolution. The labelled ticks
  are the largest evenly spaced set, first among the longest marks (log-axis
  minor ticks are shorter), else among all candidates (a curve touching the
  axis can look like the longest mark). The agent still says which candidate
  carries which printed label; the tool only proposes.
- **Curves** are read in one pixel column at the requested x. With a seed,
  the curve is followed column by column from the seed, choosing the run
  nearest the recent slope's prediction; where curves of one colour merge,
  the interval widens to the whole merged run and the reading is marked
  ambiguous.
- **Precision of a reading** is half the line's extent in that column, plus
  half a pixel, plus the slope times the offset between the requested x and
  the column centre, mapped through the axis. Markers: one pixel either side
  of the centroid.
- **Datums** point at a reading with `figure:` and are curves indexed by the
  x quantity, judged value by value like a table.
- **Error bars.** With `error_bars` set, thin lines are separated from the
  markers by a morphological opening whose size is the commonest thin-line
  width in the mask (measured, not fixed), and the vertical line through each
  marker's centre is followed out to its ends, bridging gaps of 2 px. Each end
  is read at the outer edge less half the line's width, ± (1 px + calibration
  misfit). The two ends are read separately, so unequal bars on a log axis are
  right. A bar not reaching outside its marker is reported as at most the
  marker. The datum's printed interval is the bar widened by the ends'
  precision, labelled with what the bar is (SEM, SD, 95% CI, range, unstated),
  which must be cited (or stated as not given).
- **Bar charts and histograms** (`mode: bars`) are read from the top edge of
  the run standing on the baseline in each column; touching bins split where
  the edge steps by more than 1.5 px; a line drawn over a bar (up to 8 px
  wide) does not split it. Error bars on bars: the upper end is read; the
  lower end is read where it is drawn over the bar, otherwise taken as the
  mirror of the upper, and the reading says so.
- **Every plot of data is read**, measurements included, whether or not a
  model in the record predicts them yet (05-building.md).
- **Overlays.** Every build draws each reading over its figure
  (`build/figures/<id>/<reading>.png`), and the report shows them beside the
  paper's verdicts. Candidate overlays keep crop coordinates, with margins
  only on the right and bottom, and never paint over the figure's own ink.

- **Reading code kept with the record (superseding the shared digitizer as
  the default).** First chosen: the shared digitizer driven by agents, on
  synthetic figures (`experiments/digitizer_ab/`). Then tested on 8 real
  panels whose true values are the equations they plot
  (`experiments/digitizer_real/`): agents writing their own code had a mean
  error of 0.25% of the axis and 98% coverage; the shared digitizer 0.60% and
  97% at 300 dpi, 0.46% and 92% at 1200 dpi. So a figure reading is now
  usually `mode: code`: `read(image, at)` in `records/<id>/figures/`, run by
  every build in the isolated runner on the rendered crop (cached by code and
  image), returning values, 95% intervals and pixel positions; the build
  draws crosses at those positions for checking. The declarative modes stay.
- **Agents' shell commands.** Agents run one simple command per Bash call;
  a chained command (`cd ...; ...`) is refused by the permission rules, and
  in the first real-figure run that made 14 of 16 free-code agents give up
  and read by eye. The guide and the experiment prompts say so.
- **Tilt.** Every reading measures the figure's tilt from its longest straight
  line and straightens it when the tilt is 0.1° or more; marks and seeds are
  positions in the straightened crop. Ink is whatever is darker than halfway
  between paper and the darkest ink; coloured lines match within a colour
  distance of 100.

## ModelAtlas

- A mapping gives each of b's inputs as an expression in a's inputs, with
  numbers in each model's own port units; outputs are converted
  automatically.
- **same as:** verified by symbolic identity when both models give
  `symbolic()`, otherwise by agreement at 40 deterministic samples of the
  regime (log-uniform where the range spans a decade or more), within the
  relation's tolerance (default 1e-6). All points agree: verified. Some:
  ambiguous. None, but by a constant factor or offset: not verified, with
  what holds instead. None otherwise: refuted.
- **reduces to:** the limit is approached in four decades; verified when the
  last difference is within tolerance.
- **derived from:** steps written as `subs: x = e`, `limit: x -> v`,
  `series: x -> v, n` or `simplify` are applied to a's symbolic form; other
  steps make the relation unverifiable, with the paper's words as evidence.
- **scales as:** log-slopes compared in the variables both models share
  through the mapping.
- **approximated by:** the maximum relative error over the regime is
  measured; verified if within the stated tolerance.
- **Too plain:** a symbolic form with at most two operations is flagged and
  never joins a family.

## Synthesis

- **Cross-paper checks** run each model of a verified, non-trivial same-as
  pair on the other paper's run inputs. Inputs the mapping leaves free are
  taken from the first paper's own run and labelled as added. Every quantity
  correspondence used is listed. Runs that sweep a curve are not yet carried
  across.
- **Family conflict** is reported only when a cross-paper check is not
  reproduced while the paper's own check of the same value is reproduced or
  close, so a single misprint is not counted twice.
- **Cited values** are checked whenever the citing datum names
  `from_source` and `from_datum` and both records are sound. `from_source`
  may be a record id or a reference id whose reference names the record.
  When the cited paper is read after the citing one, its relation job names
  the matching value in the citing record's `cited.yaml`
  (`{datum, from_datum, evidence}`). That adds a link and leaves `data.yaml`
  as it was printed; a link may not contradict a `from_datum` already there.
- **Findings** are: not reproduced, belongs to the numerics, depends on an
  added input, refuted stated relation, family conflict, cited value.
- **Implications** are everything downstream of a finding's subject in the
  graph of inputs, runs, outputs, comparisons and cited values.
- **References** are ranked by how many open questions mention them.
- **Recomputed, not re-run.** Every verdict, relation status and family is
  derived again at each build, and none is stored in a record. What would
  cost time is running models and reading figures, so those results are
  cached by content: the hash of the code and of its exact inputs (and, for
  a figure, of the page image). A cache can always be deleted, and the build
  then gives the same Synthesis, only more slowly. Each record is evaluated
  once per build, and its evaluation is reused for cross-paper checks.
  Relation tests and symbolic forms use the same cache. A rebuild of
  unchanged records starts no model, test or figure reading. With 3 papers,
  that brought a warm rebuild from 20 minutes to 1.
- **The written review** is generated sentence by sentence from the
  Synthesis. The tracer refuses a sentence with no trace, a trace to an
  unknown id, or a number not found in what it traces to.
- **The explorer** (`build/explorer.html`) shows the same Synthesis as a
  knowledge graph and a dashboard. It is one file with no external script:
  the graph is drawn in SVG by the page's own layout, figure overlays are
  embedded scaled to 720 px wide, and the data is the Synthesis's JSON form.
  The own comparisons of a paper appear as edges from the paper to the
  printed datum, since the Synthesis does not name the model behind a
  comparison; a cross-paper check is an edge from the model.

## Agents

- One reader per paper, run in parallel; one auditor per paper after its
  reader; one figure job per paper after its audit; one relation job per
  pair of papers that show a sign of a relation (below), after both papers'
  own jobs. (Until version 0.4, one relation job covered every paper.)
- A pair is related when one paper cites the other (a reference linked to
  the record, or naming its first author and year), a model says it is
  described from the other, two models have the same shape (an output of the
  same dimension and at least two dimensional inputs in common), or the
  corpus list asks for it. On the first corpus these signs find exactly the
  three pairs the single relation job linked. Pairs are found after reading,
  from the records, so a paper added later is related to those already read.
- Jobs that passed are listed in `pipeline/completed.yaml`, committed with
  the records; a run skips them. The SQLite state is per machine and per run,
  and is not what says a paper is done.
- Jobs that edit one record hold a lock on it: two relation jobs that share a
  record run one after the other.
- Gates validate with the build's model cache, so a retry or a gate after a
  small change does not rerun every simulation. Cache files are written
  whole (a temporary file, then a rename), since jobs share the cache.
- A relation job's gate validates its two records without running their
  models, then tests the pair's relations (`boxgraph relations`); the full
  build follows the run.
- Agents run non-interactively, with an explicit allow list:
  read anything; write only inside their record; run the validator, Python
  and read-only shell commands. `Agent`, `WebFetch` and `WebSearch` are
  denied.
- An agent's job passes only when its gate passes: `boxgraph validate` says
  sound, and for an audit, `audit.md` was written. A record left unchanged is
  still sound, so soundness alone cannot show that an audit did its work.
  Failures resume the same session with the gate's output, plus any writes
  the permission rules refused.
- Every write rule is given twice: project-relative (`Edit(records/x/**)`)
  and absolute (`Edit(//abs/path/records/x/**)`). Agents address files both
  ways, and a rule only matches the form it is written in.
- A relation job may edit relations, questions, quantities and models of its
  two records, never data: it can add a helper model when a paper states a
  relation through an equation the reader did not model.
- Child agents get their own `--session-id` and an environment without the
  parent session's variables; otherwise they share the parent's identity.

## Hardening after review (v0.6)

- **Curves are compared at the same x values.** A computed and a printed
  table are compared point by point only if they are indexed by the same
  quantity at the same x values, after unit conversion; otherwise the
  comparison is an error of the record, never a verdict by list position.
- **A power of ten printed once** after two numbers applies to both:
  `4.7 ± 0.3 × 10^-5`, `(4.7 ± 0.3) × 10^-5`, `2–3 × 10^-5`.
- **Scales-as must compare something.** Slopes are taken wherever the
  variable is not zero (a regime may start at zero); a relation where no
  slope can be compared is unverifiable, not verified.
- **A symbolic form is a second copy of a model** and is trusted only where
  it gives what `run()` gives at the regime's samples (or ordinary positive
  values when there is no regime). Symbols are positive, so a regime reaching
  zero or below is tested numerically.
- **Cache keys cover everything code can load:** the file, the shared
  helpers beside it (names starting with `_`), the rest of a model's folder,
  and the models it is `built_from`, recursively.
- **Order never matters:** inputs that disagree on a condition give a mixed
  condition (`300 K | 310 K`, sorted) with a warning; alternatives, verdict
  changes, cited values and a cross-paper check's own run are sorted.
- **Sign conventions:** a cited-value link may say `negated: true` when the
  two papers print the value with opposite signs by their own conventions.
  The check applies it and shows it.
- **Mistakes in a record never crash a build:** a refinement of an unknown
  output, a tolerance that is not `1%` or a number, a run with no value, a
  model that prints, a relation whose test cannot be carried out, and bar
  readings without their kind are reported on the record or relation.
- **Unattended runs (pipeline):**
  - A job waits for its dependencies to *pass*; a dependency outside the
    run counts only if the ledger or this machine's state says it passed.
    Otherwise the job is blocked and never started.
  - A parked job stays parked on later runs (its cost kept) until
    `--reset JOB`. `--rerun` resets the chosen jobs as well as ignoring the
    ledger.
  - A job's budget covers all its attempts: each retry is given what is left.
  - Agents run in their own process group; a timeout, an interrupt or a
    SIGTERM kills the agent and everything it started. The job stays
    `running`, so the next run resumes its session.
  - One run at a time per state folder (`run.lock`). The ledger is written
    as each job passes, and always whole (written then swapped in).
  - Each job lists the paths it may change. After every attempt the project
    is scanned (ignored and build folders excepted); a file changed outside
    the job's paths, or page content (an image, PDF or text dump) written
    into a record outside its ignored folders, fails the attempt and is
    named to the agent. This holds whatever tool wrote it, Python included.
    Agents keep Python (to test their models) and lose `sed` (its `w`
    command writes files). Not covered: network access and `git`, which
    agents are not given but could reach through Python; a commit by an
    agent is still stopped by CI's copyright test.
  - A log the gate requires (`audit.md`, `figures.md`) must be written by
    this job, not left by an earlier one. A record whose id does not match
    its folder, or that holds no data and no models, is not sound.
  - A relation job's gate validates both records with their models run
    (from the shared cache), since the job may touch models.
  - An agent that exits without a result is recorded with its error output,
    and retried after a pause (an API outage, an expired login).
  - When a paper's PDF or page range changes, its finished jobs and the
    relation jobs it is part of leave the ledger and run again. A PDF that
    cannot be ingested stops only its own paper.
  - The run ends with a summary of what was spent and what needs a person,
    and exits 0 only if every job passed and the build succeeded.

## Code and data as sources (v0.6)

- **A record of its own.** Released code is a source of kind `software`, and
  released data (e.g. a journal's source-data spreadsheet) one of kind
  `dataset`, each with its own record. The files live under the ignored
  `corpus/` (`corpus/code/<id>/`, `corpus/data/<id>.xlsx`) and are never
  committed, whatever their licence; the record pins them by a digest of
  their contents (`version: sha256:...`, see `boxgraph/sources.py`), names
  their `licence` ('none stated' if none) and `url`, and is unsound when the
  files no longer match it.
- **Citations of code and data.** A value written in code is cited by `file`
  and `lines`, with a short quote that must be on those lines; a value in a
  spreadsheet by `sheet` and `cells`, and must equal the cells at its printed
  precision. Without the files (CI, a fresh clone) these are checked for
  structure only, with a warning.
- **Running the code.** A model with `software: true` runs the source's own
  code, found through `$BOXGRAPH_SOURCE` (the code's folder); its outputs have
  the origin *run*, and the code's digest is part of every cache key. Code
  that cannot be run here (MATLAB without Octave) may be ported to Python by
  the reader: the port is our code, its outputs are *predicted*, and the
  record says what it was ported from.
- **The links to papers** use what exists: a value in the code or data that
  a paper prints is a cited value (`from_source` the paper, `from_datum` its
  datum), checked as any other; the code's model and the paper's are related
  by the relation job (`same_as` if the code implements the paper's model).
  A table cited from another source (a figure reading against the source
  data) is compared at each shared x value, the source's value judged against
  the citing datum's own precision, which measures how well a figure was read.
- **Sandbox.** Record code runs in a fresh interpreter (`python -I`) and, where
  the system allows it (Linux user and network namespaces), with no network.
  Copies of released code or data (`.m`, `.mat`, spreadsheets) written into a
  record fail the attempt and are refused by the copyright test.

## Verdicts (v0.6)

- **Close needs the same sign and order of magnitude.** Figure 4's band (outside
  the printed range by no more than its width again) let a one-digit print call
  a millionfold difference close: Andreu's code ksub, 1e-3, against a printed
  "1" whose band reaches −0.5 to 2.5. Now, when the printed range excludes zero,
  a close result must also have the printed value's sign and be within a factor
  of ten of it (02-boxgraph, amended). For precise values nothing changes.
- **Which pairs are related.** A relation job runs for a pair when one record
  cites the other, a model is described from the other, or the corpus list asks
  for it. Two models of the same shape alone (a rate from a force and a rate)
  is a weak sign that grows with the corpus; such pairs are printed for a
  person, not related (with five papers, three of Andreu's ten relation jobs
  were of this kind and found nothing).

## The overview (v0.7)

- **A page for showing the Synthesis to others** (`boxgraph/overview.py`, written by
  `boxgraph build` to `build/overview/index.html`). The report holds everything; the
  overview is for a first reading. It leads with a graph of the sources, then the case
  studies, then a view per source (`#source-<id>`, `#case-<id>`).
- **The graph is of sources, not of models.** One mark per source (circle: paper, square:
  released code, diamond: source data), placed by year from left to right (one column
  per year, not to scale), joined by what was tested between them: relations between
  their models (solid, counted by status), values one takes from the other and checked
  (dashed, counted as agree / differ), one model run on the other's inputs (dotted).
  A relation inside one source is not drawn. Selecting a source shows its models around
  it, with a line to each source a model is related to. Families are listed under the
  graph and highlight their sources.
- **The layout is computed by the build, deterministically**: x is fixed by year; y
  comes from 400 steps of a fixed force model (sources repel, linked sources attract,
  a weak pull to the middle) from a golden-ratio start, then no overlap within a column.
  The same Synthesis gives the same picture in any order.
- **Case studies: the words are a person's, the numbers the build's.** The text lives
  in `overview/content.yaml` (field content, outside `boxgraph/`); each step names what
  it shows (`comparison: src/id`, `relation: src/id`, `cited: src/datum`,
  `cross_check: src/relation`, `figure: src/id`), and the build fills in the values. A
  step naming something the build does not have stops the overview with its name.
- **Small:** one HTML file with its data embedded (about 0.7 MB for sixteen sources);
  only a case study's figures are copied beside it (`img/`).
