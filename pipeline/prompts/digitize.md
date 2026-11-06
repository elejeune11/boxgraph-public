Read the figures of `{file}` into the BoxGraph record `{records}/{id}/` (PDF pages {first}-{last}).
{page_note}

The record already exists, read and audited. Many of the paper's results are shown only in figures,
so far read by eye (approximate values, no verdict) or left out. Your job is to read them properly,
with calibrated figure readings, as the guide's section "Reading figures" explains, so they can be checked.

1. Find every figure that plots data: results the record's models predict, and every measurement
   (points, bars, histograms, with their error bars), whether or not a model predicts it yet. Look first at data whose `printed` values start with "~" and whose
   citation is a figure, and at figures the record's notes say were left out.
2. For each, record a calibrated figure reading in `{records}/{id}/figures.yaml`, a datum that uses it
   (`figure: <reading id>`, origin `measured` for measurements), and, where a model can produce it, a
   run (a `sweep` over the datum's x positions) and a comparison (`validation` for measurements).
   A measurement no model predicts is still recorded: a later paper's model may. Keep the existing eye-read data; do not delete anything.
3. Check every reading with `.venv/bin/boxgraph figure check {records}/{id} <reading id> --out {records}/{id}/figwork/<reading id>.png`
   and look at the image: the magenta marks must sit on the curve or points you meant.
4. If a figure can settle one of the record's open questions, say so in a new question or in `figures.md`;
   never change existing questions' text.
5. Write `{records}/{id}/figures.md`: one bullet per figure panel: read (which reading ids, which curve, how
   calibrated, misfit), or left out (why: a drawing or micrograph with no values, curves indistinguishable,
   too blurred...). "No model predicts it" is not a reason to leave out a measurement.

If `figures.yaml` and `figures.md` already exist from an earlier pass, keep their readings and data
unchanged, add what that pass left out that this guide now asks for, and update `figures.md`.

Put scratch images under `{records}/{id}/figwork/`. Today is {date}.
Validate with `.venv/bin/boxgraph validate {records}/{id}` and stop only when it reports SOUND.
