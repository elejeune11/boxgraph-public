# Status: version 0.7 (2026-11-01)

## What exists

- **BoxGraph core** (`boxgraph/`): schema, printed precision and verdicts, units,
  sandboxed model runs, comparisons, refinement, alternatives of added inputs,
  the soundness validator.
- **ModelAtlas**: relation tests for all five kinds, families.
- **The Synthesis**: per-paper verdicts by purpose, cross-paper checks, cited-value
  checks, six kinds of finding, implications, references, a traced written review,
  Markdown and HTML report.
- **The reading pipeline** (`pipeline/`): ingest, reader guide, read / audit / relate
  jobs run as parallel headless agent jobs, gated by the validator,
  resumable; a synthetic evaluation paper with ground truth.
- **Figure readings**: each reading is code kept with the record
  (`records/<id>/figures/*.py`), run by every build on the rendered page in an
  isolated interpreter; every value says where it was read and is drawn on an
  overlay (`build/figures.html`). The shared tested digitizer
  (`boxgraph/digitize.py`) remains as a library and as declarative modes, and
  reads curves, markers, bars, histograms and error bars. Measured data with
  error bars (SEM, SD, 95% CI, range, unstated) carry the outer bar as their
  interval. On eight real panels with known truth the agents' own code beat
  the shared digitizer (0.25% error, 98% coverage, against 0.46-0.60%).
- **Models with randomness**: run with several seeds (5 by default); the
  computed value is the mean ± 2 standard errors and verdicts compare intervals.
- **Adding papers** (`pipeline/`): `python -m pipeline.add` registers a PDF;
  `run_papers` runs read, audit and digitize per paper, picks the pairs worth
  relating from the records (citations, models described from another, same
  shape), relates each pair with locks on both records, and builds. A committed
  ledger (`pipeline/completed.yaml`) keeps finished jobs from running again.
  Diagrams: `docs/pipeline.html`.
- **Builds recompute, they do not re-run:** model runs, relation tests and
  figure readings are cached by the hash of their code and inputs; a warm
  rebuild of four papers takes under two minutes.
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
- **311 tests** (catalogue in `docs/TESTS.md`), lint and CI (green).

## The corpus

Fourteen papers, plus released code for two of them and source data for one:
sixteen sources, read, audited and related by agents, every job validated.
Everything after the first three papers was added through the pipeline end to
end, and the last nine sources as one unattended batch in two waves:

| Paper | Models | Data | Comparisons | Figure readings | Open questions |
|---|---|---|---|---|---|
| Bell 1978 | 37 | 116 | 68 | 8 (4 in use) | 21 |
| Erdmann & Schwarz 2004 | 18 | 76 | 35 | 48 (24 in use) | 18 |
| Chan & Odde 2008 | 5 | 141 | 42 | 109 | 24 |
| Bangasser et al. 2013 | 17 | 514 | 249 | 98 | 28 |
| Andreu et al. 2021 | 3 | 127 | 37 | 86 | 17 |
| Andreu 2021, released code (MATLAB) | 2 | 50 | 17 | 0 | 16 |
| Andreu 2021, source data | 0 | 634 | 0 | 0 | 3 |
| Bangasser & Odde 2013 | 13 | 105 | 68 | 50 | 23 |
| Odde lab motor-clutch code (MATLAB) | 2 | 41 | 11 | 0 | 14 |
| Craig et al. 2015 | 10 | 216 | 146 | 130 | 29 |
| Elosegui-Artola et al. 2016 | 5 | 168 | 60 | 130 | 23 |
| Gardel et al. 2008 | 2 | 55 | 4 | 39 | 15 |
| Kong et al. 2009 | 2 | 80 | 14 | 74 | 19 |
| Elosegui-Artola et al. 2014 | 5 | 54 | 21 | 42 | 15 |
| Chaudhuri et al. 2015 | 5 | 85 | 13 | 53 | 22 |
| Gong et al. 2018 | 11 | 96 | 27 | 48 | 24 |

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

**The batch** (nine sources, two waves, run unattended with hourly check-ins and
restarts at the environment's two-hour limit): all 62 jobs passed, 60 at the
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
two families, one cross-paper check. The batch papers' findings are in
`build/report.html` and have not yet been reviewed by a person.

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

8. **Bangasser et al. 2013:** 146 comparisons reproduce, 37 are close, 16 are
   not reproduced. Eq. 10 with the base parameter set gives a binding time
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
- The evaluation corpus is one synthetic paper; the figure-reading test is
  eight real panels.
- **Costs of stopped attempts are not recorded**: an attempt stopped at a time
  limit never reports its cost, so the ledger undercounts resumed jobs (by
  about a quarter in wave 2). The transcripts have the token counts to fix it.
- **Source data with samples only:** Andreu's spreadsheet gives per-sample
  values, not the means and SEMs the figures plot, so no figure reading could be
  measured against it. That needs a processing step (mean and SEM of a sample
  table) that the engine does not have yet.
- **MATLAB is not run here:** code in other languages is checked through a
  Python port and its parameters, and the port is the reader's own model.
- Chan Fig. S12E points against its fitted curve, and overflow bars ("More",
  "100+"), are read but not compared.
- The finding for Chan 2008 depends on the reader's stepping rules; a person
  should look at `records/chan2008/models/motor_clutch/model.py` and the SOM.

## Next

1. An overview site for showing the Synthesis: the knowledge graph first,
   three case studies, a page per source.
2. A person reviews the findings against the papers, the batch's first.
3. A processing step for sample tables, so source data measures figure readings.
4. Record the cost of stopped attempts from the transcripts.
5. More synthetic evaluation papers, one per finding kind.
6. Second independent readings, and a comparison of the two.
7. The next papers, chosen from `build/report.html` "What to read next".
