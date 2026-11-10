# Audit of menon2025

Second, independent reading of `corpus/cardio/2025_Menon.pdf` (PDF pp. 1-8) against the record,
2026-11-09. All eight page texts were read; the page image of p. 4 (Fig. 1 and "Software details")
was checked.

## Checks

- `data.yaml`, `added.yaml`, runs, comparisons: none exist, and none are owed. The paper prints no
  parameter value, no equation, no table and no numerical result (pp. 1-5); the only numbers in it are
  bibliographic, grant numbers and the "several hours or days on hundreds of CPU cores" remark about
  3D simulations (p. 2), which is not a result of any model in the paper. No printed result is left
  uncompared.
- Models (`svzerodsolver_assembly` p. 4, `windkessel_bc`, `coronary_bc`, `valve_tanh`,
  `chamber_elastance_inductor` p. 5): each matches the paper's words; the quotes are on the pages
  cited. No equation is printed, so there is no symbol, sign or factor to check; all are correctly
  `runnable: false`.
- Fig. 1 (p. 4, page image): the 14 block names and the Left/Right subclasses of ClosedLoopCoronaryBC
  listed in `q_blocks_after_paper` match the figure exactly. There is no impedance and no
  variable-resistance coronary block in the figure, as the record says.
- `references.yaml` (pp. 5-8): the 32 entries match the printed list (including the printed
  "UpdePac, A." in Taylor et al. 2023, p. 7, kept as printed); `ref-kim2010` links to the record kim2010,
  which exists.
- `source.yaml`: title, authors, venue 10(109) 7595, DOI and page labels match p. 1 and the footers.

## Changes

- No transcription errors found; nothing was corrected.

## Disagreements and additions (questions)

- `q_audit_blocks_without_models` (p. 5, also pp. 2, 4): added. The paper names blocks with no model
  in the record (stenosis blood vessel, junctions, flow/pressure/resistance BCs,
  ClosedLoopHeartPulmonary) and the svZeroDCalibrator; scope is the first reader's choice, so only a
  `reading` question.
- `q_audit_code_record_missing` (no page): added. The record defers every equation to `svzerod_code`
  and states its commit date ("November 2026" in `q_blocks_after_paper`), but no such record exists in
  the corpus at audit time, so those statements are unchecked.
