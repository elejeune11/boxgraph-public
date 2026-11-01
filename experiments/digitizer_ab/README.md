# Digitizer comparison: shared tool versus agents alone

**Question.** Should figures be read by one shared, tested digitizer that an
agent drives (the hybrid), or by agents alone: by eye, or with code each agent
writes for itself?

**Answer from this experiment.** The hybrid. After one round of fixes it was
the most accurate on every figure type, its intervals were honest, and two
runs agreed exactly on clean figures. Agents alone were also accurate on clean
figures and their intervals were honest, but 4 to 5 times wider, so they
would give far fewer verdicts. Their readings also cannot be rebuilt: each run
gives slightly different numbers.

## Method

Six one-page PDFs with exact ground truth (`make_figures.py`): a coloured
curve; a log axis with minor ticks; four black curves (read the k = 3 one);
two crossing black curves (read curve A through the crossing); a degraded
"scan" (rasterised, rotated 0.6°, blurred, noisy, grey); and points with error
bars. Each method ran twice per figure with the same model and request
(`run.py`): give y at stated x with a 95% interval. Scoring (`score.py`, with
tests in `tests/test_experiment_score.py`): error as a fraction of the axis,
coverage (share of true values inside the claimed interval), interval width,
run-to-run spread.

- **hybrid:** the agent uses `boxgraph figure page/axes`, writes a spec; the
  shared code reads it (`boxgraph figure read`).
- **eye:** the agent renders and zooms with pdftoppm and looks; no code.
- **code:** the agent writes its own Python; BoxGraph's digitizer is denied to it.

## Results

Round 1 ([`RESULTS_v1.md`](RESULTS_v1.md)): all three accurate on clean
figures, but the hybrid was **overconfident on the scan**: only 42% of its
95% intervals held the truth. The tool assumed straight axes, so the 0.6°
tilt became an offset growing across the figure, and its intervals ignored
calibration error.

Fixes, test-first, in the shared tool: measure and remove tilt; set the ink
threshold from the image; bridge gaps in noisy axis lines; scale the
even-spacing tolerance with tick spacing; add the calibration misfit (at
least half a pixel) to every interval.

Round 2 ([`RESULTS.md`](RESULTS.md); hybrid rerun, others unchanged):

| Method | Mean error | Coverage | Interval width | Run-to-run spread | Cost (12 runs) |
|---|---|---|---|---|---|
| hybrid | 0.05% | 100% | 0.79% | 0.07% | $3.31 |
| eye | 0.18% | 100% | 3.10% | 0.19% | $3.12 |
| code | 0.28% | 100% | 3.75% | 0.20% | $2.07 |

On the scan: hybrid 0.23% error and 100% coverage, eye 0.69%, code 1.32%.

## What it means for BoxGraph

- **Verdicts need narrow, honest intervals.** A reading's interval is the
  printed precision a verdict is judged at. Intervals four times wider let
  through differences four times larger, so agent-only readings would turn
  many "not reproduced" into "reproduced" or "close".
- **Rebuilding needs determinism.** The hybrid's reading is code applied to a
  recorded calibration: the same every build. Agent-only readings are numbers
  an agent asserted, which principle 5 forbids for results.
- **The failure was found and fixed once, for every paper.** The scan
  weakness of round 1 would have been invisible inside per-paper bespoke code.
- **The agents' strength is judgement**, which the hybrid keeps: which panel,
  which tick carries which label, which curve.

## Caveats

- Synthetic figures only, two runs per method, one model. Real figures are
  messier (dashed lines, overlapping data, insets, hand drawing).
- The eye agent sometimes fitted a smooth function to the curve to sharpen
  its reading. That suits textbook test curves and could bias real ones.
- Error bars were not read by any method; the markers figure asked for centres.
