Read the code `{file}` into the BoxGraph record `{records}/{id}/`. It is the code released with {papers}
(already read: `{records}/<paper>/`). {page_note}

This record is a source of its own, of kind `software`: what the code says, as written, checked
against what the paper says. Never copy the code into the record: it is someone else's work and is
never committed. The record holds only short quotes that locate a value, and our own code.

1. `source.yaml`: `kind: software`, `file: {file}`, `title`, `authors`, `year` (of the code if it says,
   else of the paper), `url` if known, `language`, `licence` (from a LICENSE file or header; otherwise
   `none stated`), and `version`: the output of `.venv/bin/boxgraph digest {file}`. In `notes`, say what
   the code is (files, entry points) and how it relates to the paper.
2. `quantities.yaml`, then `data.yaml`: every parameter value written in the code that the model uses,
   with its unit as the code's comments or the paper give it, `origin: reported`, and a citation
   `{{file: <path in the code folder>, lines: "<n>" or "<a-b>", quote: "<the assignment as written>"}}`.
   Where the paper prints the same parameter, add `from_source: <paper id>` and `from_datum: <its datum id>`:
   the build then checks the code's value against the paper's. Say so in a question when a value in
   the code differs from the paper, or appears in the code but not in the paper (a hidden choice: a
   scaling factor, a fitted constant, a cut-off).
3. Models. If the code is Python, write an adapter `models/<m>/model.py` with `software: true` in its
   `model.yaml` that imports the code from the folder `os.environ["BOXGRAPH_SOURCE"]` and calls its own
   functions; its outputs then have origin `run`. If the code is in another language (MATLAB, R, C),
   it cannot run here: port the part that computes the paper's results to Python, faithfully, line by
   line, in `models/<m>/model.py` (no `software: true`: the port is our code), and say in the model's
   `notes` which file and lines it ports. Cite the model with `stated: {{file, lines, quote}}`. Keep
   each run short enough to validate in minutes (fewer replicates or a shorter simulated time, said in
   a question).
4. What the paper prints for these models (a value, a table, a curve read from a figure in the paper's
   record): copy the value into this record's `data.yaml` with `from_source`/`from_datum` naming the
   paper's datum, and add runs and `reproduction` comparisons of the code's model against them, so the
   build shows whether the code reproduces the paper.
5. Validate with `.venv/bin/boxgraph validate {records}/{id}` until SOUND. Write `notes` in source.yaml
   last: what the code reproduces, what it does not, and every difference from the paper.
Run one simple command per shell call (no `cd`, no `&&`). Write only inside `{records}/{id}/`.
