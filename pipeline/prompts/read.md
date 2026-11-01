Read the paper `{file}` into the BoxGraph record `records/{id}/`.

- Record id: `{id}`. PDF pages that belong to it: {first}-{last}. {page_note}
- Its per-page text is in `records/{id}/text/page-NNN.txt` and page images in `records/{id}/pages/page-NNN.png`.
- Other records that exist or are being built in this review: {others}. Do not edit them.
- Today is {date}. Your model id for `reader.model` is `{model}`.

Follow the guide you were given (also at `pipeline/prompts/record_guide.md`). Scope: the paper's
quantitative core. Every model that produces a printed number, the printed inputs it uses, the printed
results it claims, and the comparisons between them. Numbers in the paper that feed no model may be left
out; say what you left out in `notes`.

Validate with `.venv/bin/boxgraph validate records/{id}` and stop only when it reports SOUND.
