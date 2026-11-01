# 5 · How it is built

Documents 1 to 4 say what the record is and leave the code open. A few
requirements on the build itself are fixed here, because the record can only
be trusted if the code that checks it can be.

## Test-driven development

Every behaviour of the code that checks records is specified by a test
before the code is written.

- **A test first.** A new rule, or a change to one, starts as a test that
  fails. The code is written until the test passes, and no further.
- **Tests state the design.** Each test names, in one sentence, the rule it
  holds the code to, and where the rule comes from in these documents.
  Together the sentences form a catalogue of everything the code is held
  to, generated from the tests so it cannot drift from them.
- **Small fixtures, known answers.** Tests run on small records written by
  hand whose correct results are known, including deliberate errors: a
  misprint, an unstated input, a result that depends on its numerics, a
  false relation.
- **The readers are tested too.** Whoever or whatever reads papers into
  records is tested the same way: on papers made for the purpose, with
  errors planted in them, scored against what a correct reading must find.
- **Nothing ships red.** The whole suite passes before any change is kept.

## Reading figures

Figures are part of what a paper states, so the build must be able to read
them (see [BoxGraph](02-boxgraph.md), Values read from figures). A reading
must:

- find the axes and their marks on the page, so that a calibration can be
  recorded exactly rather than estimated;
- read a curve at given positions, plotted points, bar charts and
  histograms, and the error bars on points and bars, from the page image;
- give each value the precision the reading supports;
- show what it read, drawn over the figure, so a person can check it at a
  glance.

The reading is rebuilt from the page every time the record is built, like
every other result.

Every figure that plots data is read: what the paper's models predict, and
every measurement, whether or not a model in the record predicts it yet.
Measurements are what models are validated against, and a model in another
paper may predict them. Only figures with no values to read are left out
(drawings, micrographs, single random trajectories), each with the reason.

## Reading code kept with the record

Whoever reads a paper writes the code that reads each of its figures. The
code is kept in the record beside the reading it serves, and every build
runs it on the page again, like a model, so a reading is rebuilt and
checked like any other result.

- **The code reads everything from the image.** It finds the axes, matches
  the printed labels, finds the curve, points or bars, and gives every value
  an interval that says how precisely it could be read. Nothing is typed in
  from the paper except the labels matched to the axes.
- **Every value says where on the page it was read,** so the build can draw
  it over the figure and a person can check it at a glance.
- **Shared parts are offered, not imposed.** A tested library of shared
  parts (axis fitting, curve following, markers, bars, error bars) is
  available to the code, and for a clean figure a reading may simply name
  them. A part used by many records is worth adding to the library, test
  first.
- **Values judged by eye are never results.** Without code that reads them
  from the page, a reading gets no verdict.

This was decided on evidence. On figures made with known values, readings
through the shared parts were the most accurate. On real figures from the
first papers, whose true values were known from the equations they plot,
readers writing their own code were more accurate (a mean error of 0.25% of
the axis against 0.46-0.60%) and their intervals more honest (98% against
92-97% containing the true value), at about one and a half times the cost.
Keeping the code with the record keeps what the shared approach was for:
readings that rebuild and can be checked.
