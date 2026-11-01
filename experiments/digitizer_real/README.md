# Reading real figures: the shared digitizer or the reader's own code

## Question

On figures from real papers, is it better for the reading agent to drive the
shared, tested digitizer, or to write its own code for each figure?

## Set-up

Eight panels from the first corpus whose true values are known, because the
paper says which equation each plots and the build computes that equation at
the read positions (`make_real.py`): Bell 1978 Fig. 8 (two curves, a 1978 scan),
Erdmann & Schwarz 2004 Figs. 2(b), 3(a) (two lines), 3(d), 4(a) and 4(b). Each
panel is cut out of its page, so no equation is visible, and saved as a one-page
PDF. Every method gets the same panel, the same request and the same answer
format, and runs twice (`experiments/digitizer_ab/run.py`).

- **hybrid**: the agent uses the BoxGraph figure tools and writes a reading spec;
  the shared code reads it.
- **code**: the agent writes its own Python, without the BoxGraph package.

Errors are a fraction of the axis span; coverage is the share of true values
inside the agent's stated 95% interval.

## Results

| Method | Mean error | Coverage | Interval width | Spread between runs | Cost |
|---|---|---|---|---|---|
| hybrid, 300 dpi (`RESULTS.md`) | 0.60% | 97% | 3.21% | 0.19% | $3.46 |
| hybrid, told to work at 900-1200 dpi (`RESULTS_hires.md`) | 0.46% | 92% | 1.99% | 0.31% | $6.04 |
| code (`RESULTS.md`) | 0.25% | 98% | 2.64% | 0.14% | $5.32 |

The shared digitizer's errors were mostly constant offsets per panel (a
calibration about a pixel off); at higher resolution they shrank but its
intervals became overconfident. The agents' own code was the more accurate on
six of the eight panels and as good on the scan.

## A first run that was not fair

In the first run 14 of 16 code agents chained shell commands (`cd ...; ...`),
which the permission rules refuse; they then gave up and read by eye. The
answers on axes printed as "log N" were also scored against linear values.
Both were fixed (one simple command per call; truth in the axis's printed
units) and both methods were run again from scratch. Only the corrected runs
are reported.

## Limits

Eight panels, two runs each, from two papers. The truth is the equation, so a
figure drawn slightly off its equation counts as reading error for every
method alike (the scan shows a common offset).

## Decision

Figure readings are now usually the reader's own code, kept in the record and
run by every build (`docs/minimalist_design/05-building.md`, Reading code kept
with the record). The shared parts stay as a library.
