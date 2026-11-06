Read the data file `{file}` into the BoxGraph record `{records}/{id}/`. It is the data released with
{papers} (already read: `{records}/<paper>/`), e.g. a journal's source-data spreadsheet. {page_note}

This record is a source of its own, of kind `dataset`: the numbers behind the paper's figures, as
released. Never copy the file into the record; it is never committed.

1. `source.yaml`: `kind: dataset`, `file: {file}`, `title`, `authors`, `year`, `url` if known,
   `licence` (as the paper or journal states it; otherwise `none stated`), and `version`: the output of
   `.venv/bin/boxgraph digest {file}`. In `notes`, list the sheets and what each holds.
2. Read the sheets with Python (`.venv/bin/python` with `boxgraph.sources.read_cells(path, sheet, "B2:B9")`,
   or by listing a sheet's cells). For each series the paper plots or compares with a model (a curve,
   a set of bars, points with error bars), add a table datum to `data.yaml`: `origin: measured`, its
   quantity and unit, `table: {{index_quantity, index_unit, index: [...], values: [...]}}` with the
   values exactly as the cells hold them, and a citation `{{sheet: "<sheet>", cells: "<range of the
   values>", where: "source data for Fig. 3b"}}`. Record the spread (SD, SEM, n) the same way when the
   sheet gives it, as tables of their own. Raw per-cell or per-experiment data need not be recorded;
   the means and spreads the figures show do.
3. Validate with `.venv/bin/boxgraph validate {records}/{id}` until SOUND: it checks every value against
   its cells. Write `notes` in source.yaml last.
Run one simple command per shell call (no `cd`, no `&&`). Write only inside `{records}/{id}/`.
