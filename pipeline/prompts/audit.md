You are auditing the BoxGraph record `records/{id}/`, read from `{file}` (PDF pages {first}-{last}) by
another agent. Text is in `records/{id}/text/`, page images in `records/{id}/pages/`.

Your job is a second, independent reading of the same paper against the record. Check:
1. Every number in `data.yaml` against the page image: digits, sign, exponent, unit, page. OCR errors in
   exponents are the most common mistake.
2. Every model against the equation as printed (page image): symbols, signs, factors. The model must be
   the equation *as printed*, not a corrected one.
3. Printed results the paper claims from its models that the record does not compare yet: add the data,
   runs and comparisons.
4. Unstated inputs: are they in `added.yaml` with a basis and real alternatives?
5. Open questions: anything doubtful that is not recorded yet.

Rules: correct a transcription error (a value or equation entered differently from what is printed) and
log it. Do not change anything that is a judgement of the first reader (an added value, a choice, a
model's scope); if you disagree, add an open question of kind `reading` instead. Never delete a datum,
model or question; never "fix" the paper.

Log every change you make, and every disagreement, in `records/{id}/audit.md` (create it): one bullet
each, with the id and the page. Then run `.venv/bin/boxgraph validate records/{id}` until it is SOUND.
