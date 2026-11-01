# How to read a paper into a BoxGraph record

You are building one record of an executable literature review. The design
is in `docs/minimalist_design/` (read `01-goal.md` and `02-boxgraph.md`
first). A complete small example record is `tests/fixtures/toy/`; copy its
file formats exactly. The schema is `boxgraph/schema.py`.

The record checks **consistency, not truth**: whether a paper's printed
results follow from its own printed equations and inputs. You do not judge
whether the paper is right, and you never summarize it.

## The rules that matter most

1. **Record what was stated, not what was meant.** Enter every value exactly
   as printed: same digits, same sign, same power of ten. Never correct a
   value, even an obvious misprint. A suspected misprint becomes an open
   question of kind `possible_error`. A not-reproduced result honestly
   reached is a finding, not a failure.
2. **Every value has an origin and a citation**: the PDF page (the NNN in
   `text/page-NNN.txt`) and a short verbatim quote copied from that text file.
3. **Never blur who supplied what.** Anything the paper does not state but a
   model needs goes in `added.yaml`, with its basis and plausible
   alternatives. Never put an assumed value in `data.yaml`.
4. **Results are produced, never asserted.** You do not write computed
   numbers anywhere. You write models and runs; the build computes.
5. **Units and meaning are both checked.** Declare each quantity once with
   its dimension; a run input must measure exactly the quantity its model
   port expects.
6. **Doubt is recorded, not settled**: open questions, each with a kind.

## Files (all YAML lists unless noted), in `records/<id>/`

`source.yaml` (a mapping):
```yaml
id: <id>
kind: article
title: ...
authors: [...]
year: 1978
venue: Science 200, 618-627
doi: 10.1126/science.347575
file: corpus/<file>.pdf
page_range: [1, 10]          # PDF pages that belong to this source
pages: {1: "618", 2: "619"}  # PDF page -> journal page label, where visible
reader: {kind: agent, name: boxgraph-reader, model: <your model id>, prompt_version: "reader-1", date: "<today>"}
notes: >
  How the reading went: what is in scope, what was left out and why.
```

`quantities.yaml`: `- {id, name, dimension, description}`. `dimension` is a
pint dimensionality: `"[force]"`, `"1/[time]"`, `"[length]**2/[time]"`,
`"[length]**3/[substance]/[time]"`, `"[energy]"`, `"dimensionless"`. A
quantity is what is measured (bond lifetime, force per bond), not a symbol.
Two different physical things get two quantities even if same dimension.

`data.yaml`: values exactly as printed.
```yaml
- id: k_minus_s_low          # short, readable, unique in the record
  quantity: k_off_solution
  unit: 1/s                  # pint syntax: s, ms, nm, um, cm^2/s, M^-1*s^-1, dyne, pN, eV, kcal/mol, degC, K
  origin: reported           # measured | fitted | estimated | assumed | reported | predicted | derived | run
  printed: "3 x 10^-5"       # see "Printed values" below
  scale: linear              # or log10 / ln when the paper prints a logarithm (e.g. log10 t)
  citation: {page: 3, printed_page: "620", quote: "from 3 x 10-5 to 6 x 103 sec", where: text}
  conditions: {temperature: "37 degC"}   # keys are quantity ids; values printed with units
  from_source: ref-39        # if the paper says the value comes from a cited work
```
Origins: `reported` = a value the paper gives as an input or parameter;
`measured` = the paper's own measurement; `estimated` = the author's
estimate; `predicted` = a result the paper says its model gives (these are
what you compare against); `derived` = arithmetic the paper did on other
values; `fitted` = a fit parameter; `run` = output of the paper's own software.

A **table or a curve is one datum**:
```yaml
- id: lifetime_vs_force
  quantity: bond_lifetime
  unit: s
  origin: predicted
  citation: {page: 6, quote: "Table 2", where: Table 2}
  table: {index_quantity: force_per_bond, index_unit: dyne, index: ["1 x 10^-6", "2 x 10^-6"], values: ["0.5", "0.02"]}
```

### Printed values
Write the printed string with plain ASCII:
- digits as printed: `"4.7"`, `"-14.7"`, `"0.010"` (keep trailing zeros);
- powers of ten with a caret: `"1.3 x 10^-10"`, never `"1.3 x 10-10"`;
- a bare order of magnitude: `"10^-5"` (gets no verdict, correctly);
- uncertainty `"4.7 ± 0.3"`; range `"4 to 5"`;
- approximate: keep the paper's sign: `"≈ 0.01"`, `"~7"` (no verdict, correctly).
Never put units inside `printed`.

OCR of old scans garbles exponents ("10-5" for 10⁻⁵, "105" for 10⁵) and
Greek letters. **Always check numbers, signs and exponents against the page
image** in `records/<id>/pages/page-NNN.png` (open it with the Read tool).
Record the value the page shows; quote the OCR text as it is in the .txt.

### Citations and quotes
`quote` must be findable on that page's text file: copy 4–12 consecutive
words from `text/page-NNN.txt`, including OCR errors. The checker ignores
case, spacing and punctuation and tolerates small OCR differences, but not
paraphrase. For an equation the OCR mangles, quote words next to it and set
`where: "Eq. 16"`. If no citation is possible, use `{none: "<why>"}`.

`added.yaml`: inputs the paper does not state.
```yaml
- id: temperature_added
  quantity: temperature
  unit: K
  printed: "310"
  basis: The paper works at 37 degC elsewhere (p. 5) but does not state T for this calculation
  alternatives: ["298"]
  stands_for: T in Eq. 21
```
Give real alternatives for any added input that could change a verdict.

### Models: `models/<model-id>/model.yaml` + `model.py`
```yaml
id: lifetime_eq16            # must equal the directory name
name: bond lifetime under force (Eq. 16)
role: model                  # model | fit | processing
stated: {page: 5, quote: "the lifetime of a bond is written", where: Eq. 16}
equation: "tau = tau0 exp[(E0 - gamma f)/kT]"   # as printed, in the paper's symbols
inputs:
  tau0: {quantity: reciprocal_natural_frequency, unit: s}
  E0:   {quantity: bond_energy, unit: eV}
  gamma: {quantity: bond_range, unit: nm}
  f:    {quantity: force_per_bond, unit: dyne}
  kT:   {quantity: thermal_energy, unit: eV}
outputs:
  tau:  {quantity: bond_lifetime, unit: s}      # add scale: log10 if the paper prints log10 of it
settings: {}                 # numerical settings with the paper's values: dt, n_samples, seed, mesh...
stochastic: false
```
```python
# model.py: compute in exactly the declared port units. No I/O, no globals that change.
import math

def run(inputs, settings):
    # unit bookkeeping is yours: dyne*nm -> erg is 1e-7; eV -> erg is 1.602176634e-12
    gamma_f_eV = inputs["gamma"] * 1e-7 * inputs["f"] / 1.602176634e-12
    return {"tau": inputs["tau0"] * math.exp((inputs["E0"] - gamma_f_eV) / inputs["kT"])}

def symbolic():   # optional but wanted for closed-form models: same names, same units
    import sympy as sp
    tau0, E0, gamma, f, kT = sp.symbols("tau0 E0 gamma f kT", positive=True)
    return {"tau": tau0 * sp.exp((E0 - gamma * 1e-7 * f / 1.602176634e-12) / kT)}
```
- A model is **as the paper states it**, in its own symbols, even if it fails
  to reproduce the paper's numbers. Do not "fix" an equation to make numbers
  work. If you suspect the equation is misprinted, record that as a question.
- A model given only in words is made runnable if the words allow it
  (`from_words: true`). If it cannot be made runnable, set `runnable: false`
  with `not_runnable_reason`, add an open question about it, and do not
  write model.py.
- Simulations: make every numerical choice a setting (dt, n_samples, seed,
  t_max) set to the paper's values, mark `stochastic: true` if random, use
  the seed so a run is deterministic, and keep one call under about a
  minute at the paper's settings. If the paper's own settings would take
  far longer, use the largest affordable setting and record it as an added
  choice in the run's `note` and as a `choice` question.
- One model per distinct equation or algorithm that produces a printed
  result. Use `built_from` when one model calls another's logic.

### `runs.yaml`, `comparisons.yaml`, `refinements.yaml`
```yaml
# runs.yaml
- id: run_eq16_bell_values
  model: lifetime_eq16
  inputs: {tau0: tau0_printed, E0: E0_antibody, gamma: r0_estimate, f: f_zero, kT: kT_37C}   # datum or added ids
  settings: {}
  outputs: {tau: tau_eq16_pred}   # names the produced value; never write its number
- id: run_curve
  model: lifetime_eq16
  inputs: {tau0: tau0_printed, E0: E0_antibody, gamma: r0_estimate, kT: kT_37C}
  sweep: {f: lifetime_vs_force}   # f takes each index value of that table; output is a curve
  outputs: {tau: lifetime_curve_pred}
# comparisons.yaml
- {id: cmp_tau0, purpose: reproduction, computed: tau_eq16_pred, printed: tau_zero_force_printed}
# refinements.yaml (for every result that rests on a simulation or a numerical scheme)
- {id: ref_dt, run: run_sim, setting: dt, factors: [1, 2, 4, 8], mode: divide, output: t,
   tolerance: "1%", tolerance_basis: "added: below the printed precision of the result", tolerance_added: true}
```
Purposes: `reproduction` (the paper's own result from its own model and
inputs: the core of the record), `validation` (against independent data),
`fit_quality`, `consistency` (two printed values that should agree),
`approximation`. A comparison needs the same quantity on both sides and
agreeing conditions; if conditions differ but comparing is still sensible,
say why in `conditions_ok`.

**Aim to compare every printed result the paper says its models produce**,
including intermediate ones (e.g. a constant computed from other printed
constants), using the paper's own inputs. This is the main deliverable.

## Reading figures

A value read off a figure by eye gets no verdict. To check a result that is
only plotted, record a **figure reading** whose values every build reads
from the page itself. The usual way is **your own reading code** for each
figure (`mode: code`): it was the most accurate way on real figures with
known answers. Run one simple command per Bash call (no `cd`, `;`, `&&`,
pipes or variable assignments: they are refused).

1. **Find the panel.** `.venv/bin/boxgraph figure page corpus/<file>.pdf <page> --out records/<id>/figwork/p<page>.png`
   renders the page at 300 dpi with a pixel ruler every 100 px. Choose a crop
   `[x0, y0, x1, y1]` around **one panel**, with its tick labels.
2. **Choose a resolution** where one pixel is small against the axis: the
   plot box at least 1500 px on its shorter side, usually 900-1200 dpi for a
   journal panel. Scale the crop to that dpi. Render it with
   `pdftoppm -r <dpi> -f <page> -l <page> -x X -y Y -W W -H H -png -singlefile corpus/<file>.pdf records/<id>/figwork/<name>`
   and look at it.
3. **Write the code** in `records/<id>/figures/<reading id>.py`, defining
   ```python
   def read(image, at):      # image: the rendered crop, a numpy array (rows, columns, RGB)
       ...                   # at: the x positions to read, as numbers (empty for points or bars)
       return [{"x": x, "y": y, "lo": lo, "hi": hi, "px": [column, row],
                "px_lo": row_of_hi, "px_hi": row_of_lo,   # optional: the interval in pixels, drawn on the overlay
                "note": "..."}, ...]
   ```
   Calibrate the axes from the image itself (find the tick marks and match
   them to the printed labels you see; fit and check the misfit), find the
   curve, points or bars, and give each value an honest 95% interval:
   line thickness, calibration misfit and anything ambiguous. A position you
   cannot read is `{"x": x, "y": None, "note": "why"}`. Use numpy, scipy and
   Pillow; `boxgraph.digitize` has helpers you may use (axis fitting,
   colour masks, curve tracing, markers, bars, error bars). Everything in the
   code must come from the image: no values typed in from the paper except
   the axis labels you matched.
4. **Write the reading** in `figures.yaml`:
```yaml
- id: fig3a_N10                      # unique in the record
  page: 3
  where: "Fig. 3(a)"
  what: "the line for N0 = 10 (third from the top), as labelled in the caption"
  dpi: 1200
  crop: [600, 7720, 2640, 9000]      # on the page, pixels at dpi
  x: {quantity: time_dimensionless, unit: dimensionless}
  y: {quantity: log10_bond_number, unit: dimensionless}
  mode: code
  code: figures/fig3a_N10.py
  at: ["10", "20", "30", "40"]       # x positions to read, as printed values in the x axis unit
```
5. **Make it a datum** in `data.yaml`, with `figure:` instead of `printed`:
```yaml
- id: N10_fig3a
  quantity: log10_bond_number        # must equal the reading's y quantity
  unit: dimensionless
  origin: predicted                  # or measured, as the figure shows
  figure: fig3a_N10
  citation: {page: 3, where: "Fig. 3(a)", quote: "<words from the caption on that page>"}
```
   The datum is a curve indexed by the x axis quantity, like a table; run a
   model on it with `sweep: {<x input>: N10_fig3a}` and compare.
6. **Check it.**
   `.venv/bin/boxgraph figure check records/<id> fig3a_N10 --out records/<id>/figwork/fig3a_N10.png`
   runs your code as the build will, prints each value with its interval, and
   draws magenta crosses where it read. Open the image: every cross must sit
   on the curve or point you meant.

The shared digitizer's declarative modes (`curve`, `markers`, `bars`, with
axis `marks`, `color`, `seed`, `box`) remain available when they fit a clean
figure exactly; `.venv/bin/boxgraph figure axes ...` proposes tick positions.

**Measured data and error bars.** Read every plot of data: what models
predict, and every measurement (origin `measured`), whether or not a model
in the record predicts it yet. Measurements are what models are validated
against, and a model in another paper may predict them. Plotted points are
points with their error bars, and bar charts and histograms bar by bar. If
the points or bars carry error bars, read both ends (in code, return
`bar_lo`, `bar_hi`, and `bar_lo_outer`, `bar_hi_outer` widened by how
precisely the ends were read), and say what they are and where the paper
says so; the bar then becomes the value's printed interval:
```yaml
  mode: code                         # or markers, bars
  error_bars: sem                    # sem | sd | ci95 | range | unstated
  error_bars_citation: {page: 4, quote: "Error bars, SEM"}   # or {none: "the caption does not say"} with unstated
  bar_color: "#000000"               # markers/bars modes only: error bars in another colour
```
   An error bar hidden inside its marker is reported as at most the marker;
   a lower end hidden behind a bar is taken as the mirror of the upper, and
   the reading says so. Check the green ticks on the overlay: they mark the
   bar ends that were read.

Leave out only what has no values to read: drawings, micrographs,
kymographs, single random trajectories, and curves you cannot tell apart.
Say why in `figures.md`.

`questions.yaml`: `- {id, kind, about: [ids], text, citation?}` with kind one
of `possible_error, unstated_input, unstated_model, unexplained_difference,
overstated_claim, reading, choice, numerics`.

`references.yaml`: `- {id: ref-44, label: "44", text: "<as printed>", source: <record id if in the record>}`.
List every work the paper cites that your record mentions (and preferably all).

`relations.yaml`: only relations **this paper states** about models (e.g.
"we present a stochastic version of the Bell model"), with
`provenance: stated` and a `citation` with quote and page. Model ids are
global: `<record-id>/<model-id>`. Leave this empty if the other model is not
in the record; a later job relates models across papers.

## Working method

1. Read `records/<id>/text/` page by page; open page images for every page
   with equations, tables or numbers you will record.
2. Write `source.yaml`, `quantities.yaml`, `references.yaml`.
3. Identify the models and the printed results they produce. Record inputs
   and results in `data.yaml`, unstated inputs in `added.yaml`.
4. Write each model, then runs and comparisons. Test a model directly:
   `.venv/bin/python -c "import sys; sys.path.insert(0,'records/<id>/models/<m>'); import model; print(model.run({...}, {}))"`.
5. Run the validator and fix every ERROR:
   `.venv/bin/boxgraph validate records/<id>`
   Model runs are cached in a cache shared with the check that follows your
   job, so do not pass `--cache`: a run you make is then not repeated.
   Look at warnings too: a printed result never compared, an added input
   without alternatives, a stochastic model never refined.
6. If a comparison comes out not reproduced, first re-check your reading
   (digits, exponent, units, which equation, page image). If your reading is
   right, leave it: that is a finding. Add a `possible_error` or
   `unexplained_difference` question saying what differs.
7. Finish by writing `notes` in source.yaml. Stop only when the validator says SOUND.

Do not edit anything outside `records/<id>/`. Do not delete the `text/` or
`pages/` directories.
