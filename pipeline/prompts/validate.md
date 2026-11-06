Judge the models of two BoxGraph records against each other's measurements: `{a}` and `{b}`.
The design asks for it (`docs/minimalist_design/05-building.md`): "Measurements are what models are
validated against, and a model in another paper may predict them." Other records may exist; their
validations are other jobs' work.

Why this pair was chosen:
{reasons}

1. Read both records: the models (`{records}/<id>/models/*/model.yaml`), and the measured data
   (`data.yaml` entries with `origin: measured`, and the figure readings in `figures.yaml` /
   `figures.md`). Read the parts of each paper (text in `{records}/<id>/text/`) that say one paper's model
   explains, fits or predicts the other paper's measurements ("explains the biphasic relationship
   measured by ...", "compared with the data of ref. N").
2. For each measurement of one record that a model of the other predicts, add an entry to the
   **modelling** record's `validations.yaml`. Only where the model, run on the measurement's own
   conditions, gives the measured quantity; never a model that predicts only a trend the measurement
   does not quantify. Where the model's parameters were fitted to that same measurement, it is not a
   test: enter it with `purpose: fit_quality` (the basis names what was fitted), so it is reported as a
   fit. Finding none is a result: then add nothing, and say why in a question.
3. Format (see `tests/fixtures/toy2/validations.yaml` and `boxgraph/schema.py`, CrossValidation):
   ```yaml
   - id: val_<short name>
     model: <a model of this record>
     inputs: {{<model input>: <datum or added id here, or '<other record>/<datum>'>}}
     sweep: {{<model input>: '<other record>/<table datum>'}}   # run at each x of the measured curve
     output: <the model output that predicts it>
     against: '<other record>/<measured datum>'
     purpose: validation        # or fit_quality, where the model was fitted to this measurement
     quantities: {{'<other record>/<their quantity>': <the same quantity here>}}  # every quantity crossed
     conditions_ok: <only if conditions differ: why they may still be compared>
     basis: <why this model should predict this measurement, with page and quote if a paper says so>
   ```
   - The model's inputs come from this record's values, or from the other record's where the
     measurement's conditions are printed there (a substrate stiffness, a force).
   - Quantities are named independently in each record: list every quantity of the other record you
     use, mapped to the one here it is the same as. Do not map two quantities that only share a
     dimension.
   - An input neither paper states for these conditions goes in the modelling record's `added.yaml`,
     labelled as added, with what it rests on and its alternatives.
   - A choice that is open (which of two curves, which condition a measurement belongs to) goes in
     `questions.yaml`.
4. You may write only `validations.yaml`, `added.yaml` and `questions.yaml` of these two records. Never
   change data, models, runs, comparisons or anything already in the files.
5. Check your work: `{venv}/boxgraph validations {records} --only {a},{b}` must list each validation as
   checked (a verdict, of any kind, is a result; "cannot be checked" is not), and
   `{venv}/boxgraph validate {records}/{a} {records}/{b}` must say both records are sound. Work in
   `{check}/` for anything scratch.
6. End with a short summary: each validation added, the verdict, and the measurements you considered
   and did not use, with why.
