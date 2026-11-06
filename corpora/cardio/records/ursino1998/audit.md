# Audit of ursino1998

A second, independent reading of `corpus/cardio/1998_Ursino.pdf` (PDF pages 1-15) against the
record. Figures were not read; that is the next job.

## What was checked and found right

- **Table 1 (p. 4)**: all 8 compliances, 10 unstressed volumes, 8 resistances, both inertances and
  Vt = 5,300 ml match the page image digit for digit, including the exponents of L_sa and L_pa
  (0.22·10^-3, 0.18·10^-3; the OCR shows "1023").
- **Table 2 and its legend (p. 4)**: all 16 heart parameters match the page, including the exponents
  of R_la, R_ra (2.5·10^-3), kR_lv (3.75·10^-4) and kR_rv (1.4·10^-3). The table prints Vu_rv = 40.8
  without a unit (already q_vurv_unit). T = 0.833 s, ksys = 0.075 s^2 and Tsys,0 = 0.5 s match too.
- **Text on p. 3-5**: HR 1.2 Hz / 72 beats/min, the ratios 0.59 and 2.45, 70 kg, 1.6 l/min and
  ~30%, and the design targets ~33%, ~200-210%, 70%, 15 and 10 ml/kg match the page.
- **Table 3 (p. 5)**: all 47 entries match the page, including the signs of G_Vu_sv (-265.4),
  G_Vu_ev (-132.5) and G_T_s (-0.13), which the OCR reads as "2". The gain units are per
  spikes/s (ν), stored as ×s.
- **p. 10**: the 30% / 15% pacing statement matches the page.
- **Models against the printed equations (pp. 12-14)**:
  - circulation_baroreflex implements Eqs. 1-10, 12-31 and 33-42 as printed. Checked: the
    signs, the dVu,ev/dt term in Eq. 8, every term of Eq. 9, the Eq. 10 sum, sin^2(πTu/Tsys), and
    Tsys = Tsys,0 - ksys/T. Eq. 30 is integrated through y = P~ - (τz/τp)Pcs, which is equivalent.
  - reflex_static is the steady state of the same equations.
  - emax_ratio, vu_ratio and period_from_rate are as stated.
  - No transcription error was found in any model.
- **References (pp. 14-15)**: the cited works the record uses (refs. 4, 19, 36, 42, 43, 45) match
  the printed list.

## Changes

- `references.yaml`, **ref-41** (p. 15): the title was transcribed as "a- and b-adrenergic"; the
  page prints "α- and β-adrenergic". Corrected.
- `data.yaml`, **L_sa**, **L_pa** (p. 4): added a note that the Table 1 column header prints the
  inertance unit as mmHg·ml·s^-2. The record stores mmHg·s^2/ml. Value, unit and printed string
  are unchanged.

## Questions added

- **q_inertance_unit** (possible_error, p. 4): the printed inertance unit mmHg·ml·s^-2 is not the
  dimension of an inertance in Eqs. 2 and 6. The record silently used mmHg·s^2/ml, and that
  unit is now recorded as a reading of a probable misprint.
- **q_eq35_condition** (reading, p. 14): Eqs. 35 and 38 print the switching condition on fes
  without the delay, while the logarithm takes fes(t - D). The record applies the condition to
  the delayed value. This only matters near the upper saturation of the afferent sigmoid.
- **q_vu_two_thirds** (reading, p. 5): the paper also states that the splanchnic 10 ml/kg is
  "two-thirds of the total reflex response". This claim is not compared as a datum because it is
  printed in words, which the printed-value format cannot hold. It follows from the ratio of the
  Table 3 gains G_Vu,sv and G_Vu,ev. The two absolute values are compared already.

## Disagreements and notes (no change made)

- **source.yaml** `reader.model` is `None`; the first reader did not record its model id. Left
  as is, since it is the first reader's metadata.
- **vu_total_target** (p. 5) is entered as "~15". The page says "approximately as great as
  15 ml/kg", with no sign. Encoding the word as "~" is a fair reading and gives no verdict, as
  the word intends. Left as is.
- **Printed results not compared**:
  - Every other model result in the paper is only plotted (Figs. 2-9) and is left to the
    figure job.
  - The remaining printed numbers on pp. 6-9 are simulation inputs for those figures, not
    results:
    - Pra 1-10 mmHg, SAP 92 mmHg and Pcs 62-122 mmHg for Fig. 5;
    - paced rates of 30-200 beats/min, normalized at 80 beats/min, for Fig. 6;
    - Pcs 40-150 mmHg for Fig. 7;
    - 1.5 Hz and 2 Hz pulsations of 20-60 mmHg for Figs. 3 and 8;
    - a 10% hemorrhage over 5 s, read at 80 s, for Fig. 9.
  - The ">110 beats/min" statement (p. 10) is qualitative.
  - No new datum, run or comparison was needed.
- Judgement calls of the first reader are kept. They are already covered by questions:
  - the added pressures 0 and 250 mmHg for the "whole sensitivity range" (q_range_pressures);
  - the 60 beats/min starting rate for pacing (q_pacing_start);
  - the definition of total systemic resistance (q_total_resistance).
