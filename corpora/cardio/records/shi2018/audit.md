# Audit of shi2018 (second reading)

A second, independent reading of PDF pages 2-8, checked against the record. Figures were not read (that is the next job).

## Values checked against the page images
- `lv_pressure_min_text`, `lv_pressure_max_text` (p. 7): "0 to 120 mmHg" matches the page.
- `arterial_pressure_min_text`, `arterial_pressure_max_text` (p. 7): "80–120 mmHg" matches.
- `mean_flow_text` (p. 7): "about 5 L/min" matches; "~5" is right for "about".
- `peak_aortic_flow_mls`, `peak_aortic_flow_lmin` (p. 7): "about 1000 mL/s (60 L/min)" matches.
- `peak_mitral_flow_mls`, `peak_mitral_flow_lmin` (p. 7): "800 mL/s (48 L/min)" matches.
- `lv_volume_min_text`, `lv_volume_max_text`, `stroke_volume_text` (p. 7): "55 mL to 130 mL" and "75 mL" match.
- The text of pages 2-8 prints no other numerical result. The quiz figures of 33% and 22% (p. 7) come from ref [20], and no model produces them; the first reader left them out, and I agree.
- I found no transcription errors and changed no values.

## Models
- `circulation_fig1d` (pp. 3-4): the paper prints no equation. The schematic (Fig. 1(d), p. 4) and the text agree with the record's description. Marking it not runnable is right.
- `stroke_volume_difference` (p. 7): SV = V_max - V_min, stated in words. It matches the text; no change.

## Comparisons
- Every printed scalar result that this paper can check on its own is compared: `cmp_stroke_volume` and the two unit-conversion consistency comparisons. The other results depend on the unrunnable model and are covered by `q_model_unstated`.

## Added
- Question `q_mean_flow_vs_stroke_volume` (p. 7, unstated_input): the heart rate links the mean flow (5 L/min) and the stroke volume (75 mL), but the paper never prints it, so the two cannot be cross-checked here.

## Notes, not changed (judgements or metadata)
- There is no `added.yaml`. That is correct: the only runnable model takes printed inputs only.
- The p. 4 text says "the cardiovascular models in Figure 1(a,d) have been represented using the CellML", which probably means (a–d). No record id depends on it, so I added no question.
- `source.yaml` gives `reader.model: None`. I left the first reader's metadata as it is.
