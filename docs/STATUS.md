# Status: version 0.10 (2026-11-11)

## What exists

- **BoxGraph core** (`boxgraph/`): schema, printed precision and verdicts, units,
  sandboxed model runs, comparisons, refinement, alternatives of added inputs,
  the soundness validator.
- **ModelAtlas**: relation tests for all five kinds, families.
- **The Synthesis**: per-paper verdicts by purpose, cross-paper checks, cited-value
  checks, models judged against other papers' measurements (v0.8), six kinds of finding, implications, references, a traced written review,
  Markdown and HTML report.
- **The reading pipeline** (`pipeline/`): ingest, reader guide, read / audit /
  digitize / relate / validate jobs run as parallel headless agent jobs, gated by the validator,
  resumable; a synthetic evaluation paper with ground truth.
- **Figure readings**: each reading is code kept with the record
  (`corpora/<name>/records/<id>/figures/*.py`), run by every build on the rendered page in an
  isolated interpreter; every value says where it was read and is drawn on an
  overlay (`build/<name>/figures.html`). The shared tested digitizer
  (`boxgraph/digitize.py`) remains as a library and as declarative modes, and
  reads curves, markers, bars, histograms and error bars. Measured data with
  error bars (SEM, SD, 95% CI, range, unstated) carry the outer bar as their
  interval. On eight real panels with known truth the agents' own code beat
  the shared digitizer (0.25% error, 98% coverage, against 0.46-0.60%).
- **Curve ports** (v0.10): a model input or output may take or give a whole
  curve, so a model can process a measured trace (average it, differentiate
  it, separate it into waves) rather than be run once per x value.
- **Models with randomness**: run with several seeds (5 by default); the
  computed value is the mean ± 2 standard errors and verdicts compare intervals.
- **Adding papers** (`pipeline/`): `python -m pipeline.add` registers a PDF;
  `run_papers` runs read, audit and digitize per paper, picks the pairs worth
  relating from the records (citations, models described from another, same
  shape), relates each pair with locks on both records, then runs a validate
  job for the pair (v0.8), and builds. A committed
  ledger (`corpora/<name>/completed.yaml`) keeps finished jobs from running again.
  Diagrams: `docs/pipeline.html`.
- **Builds recompute, they do not re-run:** model runs, relation tests and
  figure readings are cached by the hash of their code and inputs; a warm
  rebuild of unchanged records starts no model, test or figure reading.
- **Code and data as sources** (v0.6): a paper's released code and source data
  are attached with `python -m pipeline.attach` and read into records of their
  own. Values in code are cited by file and line and checked against the paper;
  a model runs the code itself (Python) or a faithful Python port (other
  languages); values in a spreadsheet are cited by sheet and cells and checked
  against them. Both are pinned by a digest of their contents and never
  committed. Record code runs without network where the system allows it.
- **Hardened after an independent review** (v0.6): curves are compared only at
  the same x values; a shared power of ten applies to both numbers; scales-as and
  symbolic checks cannot pass vacuously; cache keys cover code a model loads;
  results do not depend on the order of a record's entries; record mistakes are
  reported, never raised. The pipeline can be left running: dependencies must
  pass, parked jobs wait for a person (`--reset`), budgets are per job, a stop
  kills its agents, one run at a time, every attempt is checked for writes
  outside its record and for page content in a record, required logs must be
  fresh, and the run ends with a summary and an exit code. An end-to-end test
  runs the whole pipeline with a fake agent in CI.
- **Models against other papers' measurements** (v0.8): a record's
  `validations.yaml` says which of its models predicts which measurement of
  another record, on which inputs, and which quantities of the two are the same.
  The build runs the model on the other record's values (figure readings
  included) and judges it at the measurement's precision. A model fitted to that
  measurement is entered with `purpose: fit_quality` and reported as a fit.
- **The overview** (v0.7): `build/<name>/overview/index.html`, served from `site/<name>/`: the
  sources and models as a graph (in full, or the sources alone by year), three
  case studies and a view per source.
- **Several corpora** (v0.9): every corpus lives in `corpora/<name>/`, and
  every pipeline command names it (`--corpus <name>`, and `CORPUS=<name>` for
  make). Each has its own build, overview page (`site/<name>/`) and ledger;
  the model cache is shared. `site/index.html` is a landing page linking the
  reviews. The first corpus, `motor_clutch`, and the second, `cardio`, are below.
- **Rounded inputs in verdicts** (v0.9): a result that misses its printed
  value by no more than 10% is judged again with the range the printed
  inputs' rounding allows (each input at either end of its printed range, at
  most eight inputs). The comparison says which inputs were varied.
- **Corrected variants of misprinted equations** (v0.9): the printed model
  stays, with its verdicts as the paper's; a variant (`variant_of`,
  `corrections` with their evidence) is run on the same results and tallied
  apart as "reproduction, corrected". It makes no finding of its own.
- **Time limits** (v0.9): a model run may take two hours, a gate six and an
  agent job eight, so 1D network models and long simulations can be checked.
- **The overview** (v0.9): one page per corpus, linked to each other; a
  source with a corrected variant shows its corrections and their evidence;
  sources sharing an author-year label are told apart (2013a, 2013b).
- **About 400 tests** (catalogue in `docs/TESTS.md`), lint and CI.

## The motor-clutch corpus

`corpora/motor_clutch/`. Thirteen papers, two releases of code (the Odde lab's, for Chan 2008 and
Bangasser 2013, and Andreu 2021's) and one of source data (Andreu 2021):
sixteen sources, read, audited and related by agents, every job validated.
Everything after the first three papers was added through the pipeline end to
end, and the last nine sources as one unattended batch in two waves:

| Paper | Models | Data | Comparisons | Figure readings | Open questions |
|---|---|---|---|---|---|
| Bell 1978 | 37 | 116 | 68 | 8 (4 in use) | 29 |
| Erdmann & Schwarz 2004 | 18 | 76 | 35 | 48 (24 in use) | 20 |
| Chan & Odde 2008 | 5 | 141 | 42 | 109 | 37 |
| Bangasser et al. 2013 | 17 | 514 | 249 | 98 | 40 |
| Andreu et al. 2021 | 3 | 127 | 37 | 86 | 24 |
| Andreu 2021, released code (MATLAB) | 2 | 50 | 17 | 0 | 21 |
| Andreu 2021, source data | 0 | 634 | 0 | 0 | 3 |
| Bangasser & Odde 2013 | 13 | 105 | 68 | 50 | 34 |
| Odde lab motor-clutch code (MATLAB) | 2 | 41 | 11 | 0 | 19 |
| Craig et al. 2015 | 10 | 216 | 146 | 130 | 31 |
| Elosegui-Artola et al. 2016 | 5 | 168 | 60 | 130 | 30 |
| Gardel et al. 2008 | 2 | 55 | 4 | 39 | 17 |
| Kong et al. 2009 | 2 | 80 | 14 | 74 | 25 |
| Elosegui-Artola et al. 2014 | 5 | 54 | 21 | 42 | 23 |
| Chaudhuri et al. 2015 | 5 | 85 | 13 | 53 | 27 |
| Gong et al. 2018 | 11 | 96 | 27 | 48 | 31 |

Model counts include the helper models the relation job added. "Data" counts
printed, measured and read values; earlier figure readings are kept but no
longer used. Agent cost: about $24 for reading, auditing and relating the
corpus, $7.40 for re-reading Bell's and Erdmann's figures by code, and $20.70
for Chan's second figure pass (measured data), about $52 in all. Bangasser
2013 cost $34.73: read $6.76, audit $4.91, digitize $20.83, three relation jobs
$2.23. All passed their gates first time. Andreu 2021 with its code and data
cost $46.38 as recorded (read $17.33, audit $0.63, digitize $16.73, code
$2.36, data $3.32, ten relation jobs $6.00), plus a few dollars not recorded for
attempts stopped before they reported their cost; read and data needed a second
attempt, both because of false alarms of the new write check (since fixed).

**The batch** (nine sources, two waves, run unattended with hourly check-ins, on
a machine that stops commands after two hours, so the run was restarted when
stopped): all 62 jobs passed, 60 at the
first attempt (a figure job and a relation job needed a second), and nothing
was parked. Wave 1 (Bangasser & Odde 2013 with the Odde lab code, Craig 2015,
Elosegui-Artola 2016) took about five and a half hours; wave 2 (Gardel 2008, Kong 2009, Elosegui-Artola
2014, Chaudhuri 2015, Gong 2018) about four and a half. Recorded cost: $86 and
$104. The ledger undercounts jobs that were stopped at the time limit and
resumed, because a stopped attempt never reports its cost; counted from the
agents' transcripts, priced at rates fitted to the 67 jobs that ran without
interruption (median error 1.8%), the waves cost about $93 and $136. A paper
cost $5-40 to read, audit and digitize, depending on how many figures plot
data; a relation job $0.3-1.6. After the batch: 204 findings, 59 relations,
two families, one cross-paper check (before rounded inputs, v0.9). The
current build has 140 findings (112 not reproduced, 16 that depend on an added
input, 11 that belong to the numerics, one cited value), 59 relations, two
families and one cross-paper check. The batch papers' findings are in
`build/motor_clutch/report.html` and have not yet been reviewed by a person.

Validations (v0.8): a validate job ran for each of the 48 related pairs, all
passed their gates ($39.42 in all, $0.3-1.6 a pair, plus one stopped call not
priced). They entered 18 validations, every one checked by the build, and for the other
pairs a question saying why none applies (most pairs are two theory papers, or
a measurement no model there predicts). Only two are tests, and neither
reproduces: Elosegui 2016's talin clutch model against Elosegui 2014's traction
under myosin inhibition (Fig. 1b, which rises and then falls with stiffness;
the model keeps rising) and its α5β1 retrograde flow (Fig. 4e). The other 16 are
fits, the model tuned to that data:

| Model | Against | Verdict |
|---|---|---|
| Bangasser 2013 simulation | Chan 2008 flow, 260 Pa and 57 kPa | both reproduced |
| Bangasser 2013b software | the same | 260 Pa not reproduced (49 against 78 ± 4 nm/s), 57 kPa close |
| Odde lab code | the same | 260 Pa not reproduced (43 against 78 ± 4 nm/s), 57 kPa reproduced |
| Andreu 2021 code | Andreu 2021 Fig. 1e-h, YAP and paxillin, four stretches | 1 reproduced, 3 close, 4 not reproduced |
| Chan 2008 model | Bangasser 2013 Fig. S1B | not reproduced |
| Bangasser 2013 Eq. 9 (catch-slip bond) | Kong 2009 Fig. 3A lifetimes | not reproduced: Kong's lifetimes first fall with force, Eq. 9's only rise then fall |

The two implementations that miss at 260 Pa may be run with parameters other
than the set fitted to Chan; a person should check. Craig 2015 against Gardel
2008 is not a test (Craig's parameters were chosen to match Gardel's cells) and
cannot be checked as a fit (per-cell scales are not printed): an open question
in Craig's record.

Findings:

1. **Bell 1978, Table 2 (p. 6):** log t at 4 x 10^-6 dyne is printed -14.7; Eq. 17
   and both forms of Eq. 22 give -4.7. The other rows reproduce.
2. **Erdmann & Schwarz 2004 (p. 3):** both printed lists of decay rates for
   N0 = 2, 5, 10, 15 match Eq. 5 and the master equation only in reverse order.
3. **Chan & Odde 2008 (SOM):** the simulated retrograde flow on soft substrates
   depends on the time step. At the paper's 5 ms it is 75.7 nm/s, matching the
   measured 78 ± 4 nm/s on 260 Pa gels; refined, it settles near 46.6 nm/s,
   which does not match. On stiff gels it holds at any step. This rests on the
   stepping rules the paper leaves partly unstated (recorded as q_binding_rule).
   With five seeds per point: 77.0 ± 0.8 at 5 ms (reproduced) and 45.0 ± 1.2
   refined (not reproduced), so the step dependence is not sampling noise.
4. **Sensitivities:** Bell's critical-force row depends on an unstated K N2;
   Chan's soft-gel validation depends on how the fit length enters Eq. 13.

5. **Chan & Odde 2008, measured data (Fig. 3D):** the six measured flow
   means with their SEM bars, read from the figure, against the model at the
   paper's settings: reproduced at 0.26, 0.73, 24 and 57 kPa; close at
   1.07 kPa (77.3 against 85.2 ± 2.4 nm/s); not reproduced at 1.30 kPa (81.0
   against 102 [97.3, 106.3] nm/s), the point where the paper's measured flow rises
   sharply and the model's has not yet. Fig. S8C (control and GFP-actin flow,
   error bars of unstated kind) is close for GFP-actin; the control on
   260 Pa is not reproduced.
6. **Chan & Odde 2008, figures against text:** the Fig. 3C bars come in
   multiples of 1/95, which ties n = 95 to the 260 Pa gel and leaves only the
   caption's "stiff"/"soft" swapped (q_fig3c_counts); Fig. S8C's GFP-actin
   260 Pa data (n = 77, ~84 nm/s) are not the Fig. 3C data (n = 95,
   78 ± 4 nm/s) and the paper does not say how they relate
   (q_figS8C_vs_fig3); failure frequency is said to rise "as predicted by the
   model" but no simulated failure rate is shown (q_failure_frequency_model).
7. **Re-reading by code** settled three of Erdmann's four "close" figure
   points as reading error at 300 dpi (Fig. 3(d)'s log N = 1 was placed 19 px
   off); Bell's curves moved at most 0.04 log units with intervals about a
   third narrower.

8. **Bangasser et al. 2013:** 175 comparisons reproduce, 11 are close, 13 are
   not reproduced (before rounded inputs, v0.9: 146, 37 and 16). Eq. 10 with the base parameter set gives a binding time
   about twice the dashed line of Fig. 6D (q_tbinding), the line on which the
   paper's explanation of the optimal stiffness rests. Four sensitivity
   products of Fig. 5C differ in the last digit from S x R (-0.75 printed,
   -0.732 computed). At the softest substrate (0.01 pN/nm) the simulated flow
   is about 10 nm/s in Figs. 2C and 3A where the figures read near zero.
   Smaller slips: the right axis of Fig. 6B is labelled nm/s for a spring
   constant, and the text lists nc among the motor parameters.

9. **Andreu et al. 2021, Supplementary Table 4:** prints the substrate spring
   constant as 1 µN/nm; the released code uses 1e-3 N/m (1 pN/nm), a millionfold
   less. With the printed value the model's Fig. 2e lines are flat (not
   reproduced); with the code's value they reproduce (q_ksub_unit).
10. **Andreu et al. 2021, code against paper:** every other parameter the paper
   prints agrees with the code. The code has what the paper does not state:
   talin refolding, active although a comment says it was not considered; a
   scaling of the model to the experiments (bl = 1.2, sc = 1.4); the catch- and
   slip-bond coefficients; and the rate tables' grids and cut-off. One script does
   not run as released (its rate lines are commented out). A Python port of the
   rate-table script reproduces the shipped tables; the port of the clutch model
   reproduces the paper's four Fig. 2e model curves; the paper's Methods model
   approximates the code only to 4.1%.

Chan's simulated curves read from Figs. 1D, 3D and S1 are mostly "not
reproduced": across 135 points the median gap is 3.6%, against a median
sampling error (2 SE) of 0.7% and reading half-width of 0.5%. The shapes
match; the levels sit a few percent apart. The printed curves are themselves
single noisy runs of unknown length and seed, and that noise is not in the
printed side's interval (see Known limits), so these are not yet findings.

ModelAtlas: Bell's loaded off-rate, Erdmann's single-bond rate and Chan's
clutch off-rate verify as one family; Bell's and Erdmann's critical-force
formulas verify as another. Erdmann's statement that its model is "a
stochastic version of the Bell model" is tested as an approximation and is
not verified within the stated 10% (the error reaches 63%). Bangasser's
catch-slip law reduces to Bell's, Chan's and Erdmann's slip-bond rates as the
catch term vanishes, and Erdmann's lifetime without rebinding reduces to
Bangasser's binding time (all verified). Bangasser's statement that its exact
simulation is "qualitatively similar" to Chan's fixed-step one is tested as an
approximation within a 10% tolerance the relator chose, and is not verified
(the paper itself says the shapes differ).

## The cardio corpus (v0.9-0.10)

A second review, kept as a corpus of its own in `corpora/cardio/`: 0D
(lumped-parameter) and 1D models of the cardiovascular system, from the heart
and the large arteries to the viscosity of blood in microvessels. Its overview
is published in `site/cardio/`.

Twenty-nine sources: 21 articles, two thesis chapters (Shi 2013, chapters 2 and
5), and six releases of code or data (four CellML models, the code of Smith
2004 as CellML, and the Boileau 2015 benchmark waveforms). All were read,
audited, figure-read, related and validated by agents in five batches. The
ledger (`corpora/cardio/completed.yaml`) lists 231 passed jobs: 29 read,
23 audit, 23 digitize, 78 relate and 78 validate. Recorded cost: $433.94
(read $123.44, audit $32.94, digitize $163.25, relate $55.92, validate
$58.39), about $14 a paper for reading, auditing and figures.

A sixth batch (coronary) added ten sources: Spaan 1981 (the intramyocardial
pump), Chilian 1986 (microvascular pressures in the beating heart), Kassab 1993
(pig coronary morphometry), Kim 2010 (coronary outflow boundary conditions),
Mynard 2014 and 2015 (a validated left coronary model; the whole adult
circulation in 1D), Schwarz 2020 (a human left coronary tree), and the released
data of Mynard 2014, Mynard 2015 and Schwarz 2020 (without the network file of
Schwarz 2020, which was too large to upload).

Three more batches followed (v0.10):

- **Batch 7, SimVascular codes and grown trees:** Menon 2025 and Yong 2025
  (0D closed-loop and coronary models), Sexton 2025 and the released
  svVascularize code (vascular trees grown by optimization, set against the
  human tree of Schwarz 2020 and the pig trees of Kassab 1993), and the
  released svZeroDSolver.
- **Batch 8, the 1D solver:** Wan 2002 and the released svOneDSolver, built and
  run on the 1D benchmarks of Boileau 2015 against its released 3D reference
  solutions. The paper's own formulation cannot be run with a resistance
  outlet in the release (it divides by a value the code never sets).
- **Batch 9, human coronary measurements:** Davies 2006, pressure and Doppler
  velocity in the left coronary arteries of 20 people, analysed by wave
  intensity. No model in the corpus predicts what it measured (the models
  that compute coronary wave intensity cannot be run, and the others give
  flow, not velocity); each pair says why. With curve ports, the paper's
  wave intensity analysis is rebuilt from its own plotted pressure and
  velocity traces and compared with its plotted wave intensities.

- **Batch 10, human capillaries:** Kaneko 2011 (one human capillary bed
  rebuilt in 3D from serial sections), Rakusan 1992 (capillary density and
  domain radius from infancy to adulthood, with and without pressure
  overload), Campbell 2011 (capillary length density and diffusion radius
  in men and women with coronary artery disease), Mohammed 2015 (capillary
  density in heart failure with preserved ejection fraction, from autopsy)
  and Vink 2024 (myocardial blood volume, CFR and hyperemic microvascular
  resistance in people with angina and non-obstructed coronary arteries,
  with its supplement). Their values are related to each other and to
  Kassab 1993, Schwarz 2020 and the coronary models.
- **Batch 11, an engineered microvascular network:** Pandian 2025
  (self-assembled human vessel networks in fibrin on a chip, segmented from
  confocal stacks and simulated with porous-wall CFD, with its supplement)
  and its released code (the MATLAB segmentation and COMSOL export, with one
  control stack and the network it exported). The figure pass rebuilds the
  paper's R2 values and permeability bars from its plotted points; the code's
  sample network has a median diameter of 28 um, inside the printed 20-40 um,
  and two of the code's choices differ from the paper's text. The printed
  fibrin permeability does not follow from the paper's own formula.

The corpus now has 54 sources and its ledger 515 passed jobs: 54 read,
41 audit, 41 digitize, 190 relate and 189 validate. Recorded cost: $907.31
(read $268.46, audit $62.72, digitize $288.11, relate $138.62, validate
$149.40).

The build (`build/cardio/synthesis.json`):

- 177 relations (116 verified, 21 not verified, 4 refuted, 2 ambiguous,
  34 unverifiable) and 23 families;
- 264 cross-paper runs checked;
- 2410 cited values, 709 of them with a verdict (660 reproduced, 5 close,
  24 not reproduced, 20 without a verdict);
- 335 validations of one paper's models against another paper's
  measurements: 312 tests (38 reproduced, 20 close, 253 not reproduced,
  one without a verdict) and 23 fits (one reproduced). Most measured
  curves are judged point by point at the precision of a figure reading;
- 850 findings: 660 not reproduced, 100 that depend on an added input,
  52 family conflicts, 24 cited values, three refuted relations, 11 that
  belong to the numerics;
- 17 corrected variants of misprinted models.

Reproduction across the corpus: 2265 comparisons reproduced, 94 close,
798 not reproduced, 77 without a verdict, with the rounding of printed inputs
taken into account (DECISIONS, Rounded inputs in verdicts).

Corrected variants: Korakianitis and Shi 2006 as printed reproduces 2 of 117
results; its three evidently misprinted equations (an activation that gives
negative elastance, a reverse flow without its sign, a flow driven by the
wrong pressure) are corrected in a variant, which reproduces 21 and is close
on 10 of 246 comparisons, reported apart as "reproduction, corrected". Pries
1990's Eq. 7 has the wrong dimensions as printed; the variant with the factor
(D/(D - W))^4 reproduces all five Fig. 3 curves read.

The overview's seven case studies: Pries 1990's Eq. 7, a coronary tree solved
again, Boileau 2015's tables rebuilt from the released files (one entry of
Table VI: 12.95% printed, 2.95% computed), the human tree of Schwarz 2020
against the other papers, a grown tree against the human tree (Sexton 2025),
the 1D solver against its paper (Wan 2002 and svOneDSolver), and Olufsen's
asymmetry ratio across 1999, 2000 and 2012.
These findings have not yet been reviewed by a person.

## Known limits

- One reading per paper (plus an audit). Two independent readings compared
  with each other would measure reading reliability.
- A printed simulated curve is one run with sampling noise of its own; the
  verdict counts our sampling error but not the paper's. Design 02 does not
  yet say how to treat it.
- Erdmann Fig. 2(d): Eq. 6 as printed gives p0 = 1 against a reading of 0.58,
  while Eq. 1 reproduces all four points. The reading is sound; the open
  question is Eq. 6's printed form (q_eq6_exponent).
- Cross-paper checks run stochastic models once, not with repeated seeds.
- Cross-paper checks do not yet carry curves across papers.
- Relations between models with curve ports are not tested (the atlas
  samples single values); they are reported unverifiable.
- Traces read from a printed figure limit what can be rebuilt from them: a
  10 ms reading step smooths narrow peaks, and finer steps pick up the
  image's pixel staircase (Davies 2006, q_wia_grid).
- The evaluation corpus is one synthetic paper; the figure-reading test is
  eight real panels.
- **Costs of stopped attempts are not priced**: an attempt stopped at a time
  limit never reports its cost, so the ledger undercounts resumed jobs (by
  about a quarter in wave 2). `--status` lists their tokens from the transcripts.
- **Source data with samples only:** Andreu's spreadsheet gives per-sample
  values, not the means and SEMs the figures plot, so no figure reading could be
  measured against it. That needs a processing step (mean and SEM of a sample
  table) that the engine does not have yet.
- **MATLAB is not run here:** code in other languages is checked through a
  Python port and its parameters, and the port is the reader's own model.
- Chan Fig. S12E points against its fitted curve, and overflow bars ("More",
  "100+"), are read but not compared.
- The finding for Chan 2008 depends on the reader's stepping rules; a person
  should look at `corpora/motor_clutch/records/chan2008/models/motor_clutch/model.py` and the SOM.

## Next

1. A person reviews the findings and the validations against the papers, the
   batch's first.
2. A person reviews the cardio corpus's corrected variants and findings
   against the papers.
3. A processing step for sample tables, so source data measures figure readings.
4. More synthetic evaluation papers, one per finding kind.
5. Second independent readings, and a comparison of the two.
