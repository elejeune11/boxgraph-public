# Figures of mynard2015

Every panel that plots values is now read with calibrated code (`figures.yaml`, code in `figures/`).
No model in the record can produce these curves, because the full closed-loop model (`circulation_1d_0d`) cannot be
run from the paper (q_full_model_not_runnable). The readings are recorded as data with no runs or comparisons: the
model curves as `predicted`, and the in vivo curves of Fig. 4 as `measured` (with `from_source`), so that a later
paper's model, or this one run from the supplement, can be checked against them.

All figures are bitmaps embedded at about 300 dpi. They are read at 1200 dpi, so one source pixel is about
4 px. Fig. 4 is thresholded to black and white. Intervals include the line thickness, a 2 px allowance for the
source pixel, and the calibration misfit. Where a line is steep, the interval is its whole run in the column.
`figwork/` holds the overlays (`figwork/<id>.png` from `boxgraph figure check`, `t_<id>.png` from development).

## Read

- **Fig. 4 (p. 8): 24 locations x (in vivo, model) = 48 readings `fig4_<loc>_iv` / `fig4_<loc>_mod`**, data
  `<loc>_fig4_invivo` (measured) and `<loc>_fig4_model` (predicted). The locations are: aortic root, thoracic
  aorta I, abdominal aorta V, left common iliac, right common carotid, right internal carotid, right middle cerebral
  and LAD III (flow); MPA, IVC IV, SVC II, left inferior pulmonary vein, middle hepatic vein, hepatic portal vein II,
  left transverse sinus III and coronary sinus (flow); aortic root, left brachial, right radial, right femoral, left
  superficial temporal, MPA, left atrium and right atrium (pressure). The black line is read every 0.025 s over the
  span it covers (19-34 points per curve). Shared code `figures/_wave.py`.
  - y calibration: the printed tick labels' centres (the tick marks are mostly lost in the bitmap), fitted
    linearly. The misfit is at most 1.4 px (about 0.2% of the axis).
  - x calibration: t = 0 at the y axis and the panel's own four x ticks, matched to 0.2-0.8 s (labels printed
    only under the bottom row). The misfit is at most 1.4 px.
  - Model panels use the labels of the in vivo panel beside them. The code checks that the model axis's own tick
    marks fall on those label rows. Both assumptions are in q_fig4_scales.
  - The asterisked in vivo flows are velocities scaled to the model's peak flow (q_fig4_scaled_velocity).
  - Wave labels and reference numbers ("36*", "104") are dropped as narrow ink parts.
- **Figs. 5 (p. 9) and 6 (p. 10): 6 locations x 4 = 24 readings `fig5_<loc>_{p,u,wif,wib}`, `fig6_<loc>_...`**,
  data `<loc>_{p,u,wif,wib}_fig5|6` (predicted). The locations are aortic root, right common carotid and right
  brachial (Fig. 5); MPA, IVC IV and left inferior pulmonary vein (Fig. 6). Each is read every 0.0125 s.
  - P (black, left axis) and U (gray, right axis) are calibrated on their own printed labels. Times where the gray
    U line is hidden under the black P line are left out of `at`.
  - Wave intensity: forward (plotted positive) is the top edge of the black ink; backward (plotted negative) is
    the bottom edge. Filled expansion waves are read at their edge. Wave names and their leader lines are dropped
    as ink parts narrower than 40% of the plot. The axis factor (x10^6 in Fig. 5, x10^5 in Fig. 6) is applied, so
    values are in W/m^2/s^2.
  - Misfits are at most 2.9 px (Fig. 6 MPA wave intensity axis).
- **Fig. 7 (p. 10): 6 paths x (forward, backward) = 12 readings `fig7<a-f>_{fwd,bwd}`**, data
  `wi_peak_{fwd,bwd}_path_<a-f>_fig7` (predicted, log10 axis, values in W/m^2/s^2). Every plotted circle is read
  (11-28 per series). Shared code `figures/_fig7.py`.
  - Circles are found by correlating the ink with a ring, with the radius chosen from the image (19 px). A circle
    partly hidden under the other series' circle is also kept (e.g. Fig. 7(e) at 11 cm).
  - Axes are calibrated from the tick marks. Misfit: x at most 1.1 px, y at most 1.4 px (0.009 in log10).
  - Clusters of overlapping circles (Fig. 7(a) near 38-40 cm and 80 cm, Fig. 7(c) near 30-33 cm and 220-224 cm)
    give wider intervals. A circle wholly hidden under another can be missed.

## What the figures settle or raise

- q_fig5_fig7_peaks: Fig. 7's first circles (aortic root) are about 20% higher than the FCWee peak of Fig. 5 at
  the aortic root, and likewise for the right brachial artery, beyond both readings' intervals. The MPA agrees
  between Figs. 6 and 7.
- q_fig7_orders: the 'about 1-1.5 orders of magnitude' backward/forward gap reads about 1.55-1.6 at the aortic
  root. The claim is approximate, so it gets no verdict.
- No existing question is settled by a figure. The pericardial pressure (q_ppc_above_claim) and pSIP
  (q_sip_ratio_reading) are not plotted.

## Left out

- Fig. 1 (p. 4): schematics of the heart model and chamber interactions; a drawing with no values.
- Fig. 2 (p. 4): schematics of the vascular bed models; a drawing.
- Fig. 3 (p. 5): drawings of the ten 1D networks; a drawing.
- Fig. 4: the in vivo aortic root flow ends at about 0.48 s and some in vivo curves end before 0.85 s; nothing
  is read beyond the drawn line. The first and last points at the axes (t = 0) are not read.
- Figs. 5-6: the P/U panel times at the right axis (t >= 0.8 s), and gray U times hidden by the black line (e.g.
  the aortic root U after about 0.69 s, where only a short gray piece remains), are not read.
