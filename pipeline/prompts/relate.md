Relate two BoxGraph records: `{a}` and `{b}`. Each has models in `{records}/<id>/models/`.
Your job is ModelAtlas (`docs/minimalist_design/03-modelatlas.md`): enter the relations between the models
of these two papers. Other records may exist; relations to them are other jobs' work.

Why this pair was chosen:
{reasons}

1. Read both records' model.yaml and model.py, and the parts of each paper (text in `{records}/<id>/text/`,
   page images in `{records}/<id>/pages/`) that say how its models relate to the other paper's (e.g. "a
   stochastic version of the Bell model", "Bell's law for the off-rate").
2. For each relation a paper states, add it to that paper's `relations.yaml` with `provenance: stated`,
   a `citation` (page + verbatim quote from the text file), and the mapping. For relations no paper
   states but that you have reason to propose, add them with `provenance: proposed` and a `reason`,
   in the later paper's `relations.yaml`. Finding no relation is a result: then add nothing.
3. Format (see `tests/fixtures/toy2/relations.yaml` for working examples, and `boxgraph/atlas.py`):
   - `a` and `b` are global ids `<record-id>/<model-id>`;
   - `mapping` gives **each of b's inputs** as an expression in **a's input symbols**, in each model's own
     port units (include unit conversion factors);
   - `output_map: {{<b output>: <a output>}}` if either model has several outputs;
   - `regime` gives `[lo, hi]` for **every** input of a (numeric tests sample it);
   - kinds: same_as, reduces_to (with `limit`), derived_from (with `steps` such as "subs: f = 0" or
     "limit: N -> oo"), scales_as, approximated_by (with `tolerance` = acceptable relative error).
   A deterministic mean-field model and a stochastic one are usually `approximated_by`, not same_as.
4. You may add small helper models only if a paper states the relation in a form that needs one; never
   change existing models, data, or relations already in the files.
5. Values one paper says it takes from the other: in each record's `data.yaml`, a datum with
   `from_source` naming the other paper (a record id, or a reference whose `source` is the other record)
   and no `from_datum` does not yet say which value it is. Where the other record has that value, add
   a line to the citing record's `cited.yaml`:
   `- {{datum: <id in this record>, from_datum: <id in the other record>, evidence: "<why they are the same value>"}}`.
   If the two papers print the value with opposite signs by their own conventions (e.g. one counts a
   velocity negative), add `negated: true` and say so in the evidence.
   Never edit `data.yaml`. A value the other paper does not print stays unlinked. The build then
   checks each linked value against what the other paper printed.
   When one of the two records is a paper's released data or code (kind `dataset` or `software`): link
   each of the paper's values that comes from it, e.g. a curve read from a figure whose numbers are in
   the source data, with a line in the paper's `cited.yaml` that also names `from_source: <the data's
   record id>`. The build then measures each figure reading against the released numbers.
6. Test your relations with `.venv/bin/boxgraph relations {records} --only {a},{b}` and fix those that are
   unverifiable only because of a mistake in *your* mapping or regime. A refuted or not-verified status
   honestly reached is a result: leave it. Put any scratch files under `{check}/`.
7. Validate both records with `.venv/bin/boxgraph validate {records}/{a} {records}/{b}` until SOUND. Their
   models are run, as the check after your job runs them; runs are cached and shared with that check, so
   do not pass `--cache`. Use `--no-run` only for a quick look at the structure first.
   Run one simple command per shell call (no `cd`, no `&&`).
