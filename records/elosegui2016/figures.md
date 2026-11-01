# Figure readings: elosegui2016

All readings are by the record's own code (`mode: code`). Two passes:

- **First pass** (model lines and the traction/flow data they are compared with): `figures/_kit.py`,
  `figures/_fig3.py` (Fig. 3d,e) and `figures/_fig6.py` (Fig. 6a-i). Unchanged in the second pass.
- **Second pass** (every other plotted measurement, and the Fig. 3a line): `figures/_gen.py` (method) and
  `figures/_panels.py` (per-panel settings: printed tick labels, legend region, series colour and marker
  shape). Each `figures/<reading id>.py` only calls `_panels.read`.

## How the second pass reads

- **Axes.** The y axis is the longest dark vertical run, the x axis the longest dark horizontal run below
  its middle; tick marks are the short dark marks just outside each axis, matched in order to the printed
  labels and fitted by a line (log10 for the rigidity axes). The rms misfit is in every value's note and
  enters every interval (2 x misfit). Misfits are 0.0-0.5 px at 1200-2000 dpi (one tick spacing is
  250-560 px), i.e. below 0.2% of a tick spacing.
- **Markers.** Pixels of the series colour; open markers filled; a small opening removes thin lines. The
  marker size is the candidate blob size (of blobs whose fill matches the shape) that fits the most whole
  markers; panels whose series all use discs share one size, measured on all series together. Markers
  are found by matching a filled template of the shape (disc, diamond, triangle up/down). Every other
  series of the panel, and lines drawn across the markers (Fig. 1 threshold line, Fig. 6k,l reference
  line, Fig. 3a blue line), count as possible cover. A marker with >= 93% of the template in its colour is
  whole and read at the template centroid (for a triangle, the centroid is where its bar is centred).
  A partly covered marker is read at the midpoint of its two bar caps where both are visible, or else, if at
  least half of it is visible, at the best template fit, with an interval widened by the spread of equally good fits and by
  (1 - visible fraction) x a quarter of the marker height; its column is snapped to its own bar stem where
  one is visible. Two fits in one column are one point (the more visible kept).
- **Error bars** (s.e.m.: Methods p. 11, "In all figures, measurements are reported as mean ± s.e.m.").
  From the marker centre the stem is followed up and down (gaps of up to 1.3 markers bridged, where it runs
  behind another series); a cap is a short horizontal band sticking out beyond the marker's own width.
  The bar end is the middle of the outermost cap; a hidden cap is the mirror of the other; a bar with no
  cap outside the marker is reported as at most the marker. Ends are widened by 2 px + 2 x misfit.
- **Bars** (Fig. 4e,f; Supplementary Fig. 1b): the value is the middle of the dark outline on top of the
  coloured fill (half the outline's thickness enters the interval); the error bar (black) above it;
  its lower half is inside the bar, taken as the mirror. Bars are split into the two printed groups at
  the widest gap between bars.
- **Fig. 3a line**: in the 7 columns around each force, the topmost run of blue; the value is its middle
  and the interval covers the whole run (wide where the line is steep).

Each reading was run with `boxgraph figure check` and its overlay (`figwork/<id>.png`) looked at.

## Read (second pass)

| Panel | Readings | What, and notes |
|---|---|---|
| Fig. 1a (p. 2) | `fig1a_control`, `fig1a_shrna`, `fig1a_l325r`, `fig1a_bg` | traction of control (red triangles), talin 2 shRNA (blue inverted triangles), control + talin 1 head L325R (open diamonds), and the background detection level (grey discs). Control and shRNA are the data of Fig. 3d (read there in the first pass); several of their markers lie fully under the diamonds and are not read. The control and shRNA readings are validated against the clutch models as in Fig. 3d. |
| Fig. 1c (p. 2) | `fig1c_control`, `fig1c_shrna`, `fig1c_l325r` | vinculin adhesion length. Sigmoid fit lines not read (fits, no printed parameters). |
| Fig. 1e (p. 2) | `fig1e_control`, `fig1e_shrna`, `fig1e_l325r` | nuclear/cytosolic YAP. Sigmoid fits not read. |
| Fig. 2a,c (p. 3) | `fig2a_*`, `fig2c_*` | β3 and pFAK adhesion lengths, control and shRNA. |
| Fig. 3a (p. 4) | `fig3a_lifetime`, `fig3a_unfolding` | measured FN-αvβ3 bond lifetimes (all 9 points, matching the 9 n values in the caption), and the blue line of talin unfolding times from ref. 25, read at 3.5-6 pN (beyond, the line lies on the x axis and cannot be told from it); compared with 1/k_unf of the record's added slip-bond law (`talin_unfolding_time`, a `fit_quality` comparison: the note says k_unf was fitted to these data). That 1/k_unf is about half the plotted times (q_fig3a_unfolding_fit). This answers the audit's request (q_audit_fig3a_left_out). No model in the record predicts the αvβ3 lifetimes (the model's catch bond is α5β1). |
| Fig. 4a,b,c (p. 5) | `fig4a_*`, `fig4b_*`, `fig4c_*` | traction, YAP, vinculin adhesion length for FL talin 1, rod and head rescues. Fig. 4c has a linear x axis (0-15 kPa) and horizontal error bars on x, which are not read. |
| Fig. 4e,f (p. 5) | `fig4e_*`, `fig4f_*` | bar charts at 5 and 29 kPa: shRNA, FL talin 1, L325R, W359A. |
| Fig. 5a,b,c (p. 6) | `fig5a_*`, `fig5b_*`, `fig5c_*` | FL talin 1 vs IVVI vs shRNA. |
| Fig. 5e,f (p. 6) | `fig5e_*`, `fig5f_*` | VD1 vs VD1 A50I. Fig. 5f has an unlabelled tick at the bottom of the y axis, left out of the calibration. |
| Fig. 6j,k,l (p. 7) | `fig6j_*`, `fig6k_*`, `fig6l_*` | YAP for the three fibronectin, GPen and blebbistatin doses. The blue reference line and the sigmoid fits are not read. The highest GPen dose is labelled "50 mM" in the legend (q_fig6k_legend); the reading is named for 0.50 mM. |
| Supp. Fig. 1b (p. 12) | `figs1b_<control/shrna>_<none/ab/gpen/both>` | % attached cells on 29 kPa gels, one bar each. |
| Supp. Fig. 2 (p. 13) | `figs2_l325r_5kpa`, `figs2_l325r_29kpa`, `figs2_control_*`, `figs2_shrna_*` | single-cell tractions against transfection efficiency (no error bars; overlapping discs found by template matching, so some fully hidden cells are missing: 32 of n = 37 at 5 kPa and 39 of n = 42 at 29 kPa found), and the four mean values with s.e.m. bars, whose x is the rigidity of their colour. The means of control and shRNA are validated against the clutch models. The dotted sigmoid fits are not read. |
| Supp. Fig. 3a,b (p. 14) | `figs3a_*`, `figs3b_*` | β3 integrin density (a.u.) and % area with pFAK adhesions. |
| Supp. Fig. 4a,c,e (p. 15) | `figs4a_*`, `figs4c_*`, `figs4e_wt` | spread area, pMLC/MLC ratio (control, shRNA, wild-type MEFs). |
| Supp. Fig. 5a,b,c (p. 16) | `figs5a_*`, `figs5b_*`, `figs5c_*` | traction and YAP for shRNA + VD1 / VD1 A50I; single-cell YAP against transfection efficiency (no error bars; dashed fits not read). |
| Supp. Fig. 6 (p. 17) | `figs6_5kpa`, `figs6_29kpa` | fibronectin surface density (a.u.) against coating concentration (1, 10, 100 µg/ml), linear x. |

Consistency seen between readings (not compared by the build, which compares curves only at equal x):
the Supplementary Fig. 2 means of untransfected cells (control 29 kPa 137.7 Pa, shRNA 5 kPa 83.3 Pa,
shRNA 29 kPa 37.1 Pa) agree with the Fig. 1a points at the same rigidities (137.4, 83.2 Pa) and with the
Fig. 4e shRNA bars (82.6-83.0 and 36.5-36.8 Pa), as if the same cells were shown; Fig. 1e and Fig. 6j (10 µg/ml)
agree likewise (2.51, 2.79, 2.90 at 11.3, 14.6, 29 kPa in both).

## Read (first pass, unchanged)

| Figure | What | Readings |
|---|---|---|
| Fig. 3d (p. 4) | traction vs rigidity: model with talin (red line) and without (blue line); control and talin 2 shRNA data (= Fig. 1a) | `fig3d_model_talin`, `fig3d_model_notalin`, `fig3d_control`, `fig3d_shrna` |
| Fig. 3e (p. 4) | actin flow vs rigidity: the same two model lines; control and shRNA data | `fig3e_*` |
| Fig. 6a-i (p. 7) | traction vs rigidity at three fibronectin coatings (a-c), GPen doses (d-f) and blebbistatin doses (g-i): solid (talin) and dashed (no talin) model lines; control (filled) and shRNA (open) data | `fig6<p>_model_talin`, `fig6<p>_model_notalin`, `fig6<p>_control`, `fig6<p>_shrna` |

First-pass method: axes calibrated on their own tick marks (log x: 0.1-100 kPa; y: 0-160 Pa or 0-120 nm/s);
model lines read at rigidities away from the markers (0.4-40 kPa); hidden stretches interpolated, with the
note saying so; dashed lines read from their separate dashes only (q_dashed_hidden); markers covered by
another marker not found (q_hidden_points).

## Left out

- **Fit lines**: the sigmoid fits of Fig. 1a,c,e, 4b, 5b,f, 6j-l and Supplementary Figs. 2 and 5c, and the
  blue "reference" YAP line of Fig. 6j-l (a fit to Fig. 1e): empirical fits whose parameters are not printed;
  they are not measurements and no model in the record produces them.
- **Grey detection-level lines** of Fig. 3d and Fig. 6a-i: the measured detection levels are read as points
  in Fig. 1a (`fig1a_bg`).
- **Markers fully covered** by another series' marker (no own colour visible, or only a sliver without a
  bar): not read; each series holds the points that could be found (see q_hidden_points_second_pass).
- **Fig. 1b, 1d, 1f; 2b, 2d; 3b, 3c, 3f; 4d; 5d, 5g; Supplementary Figs. 1a, 4b, 4d, 7**: traction colour
  maps, micrographs, kymographs, drawings and western blots, with no plotted values.
