# Figures of stafford2004

The first pass read no figure (the job could not render pages). This figure pass reads every plotted
data series. All readings use `mode: code`, at 900 dpi, with one shared reading code (`figures/*.py`, which
differ only in their CONFIG block). How the code reads:

- **Calibration**: the plot box is found as the longest dark lines; the tick marks are the short dark runs
  leaving a spine (a tick may sit one pixel off it), and the labelled ticks are matched to the tick labels
  printed beside them. A straight line is fitted through them; the misfit (largest tick residual) is
  reported in every reading's note and added to its interval.
- **Markers**: filled discs by matching a disc template on the dark-ink mask; open circles by a ring
  template with a light centre, kept only if the ring is closed (ink in at least 20-23 of 24 directions),
  which rejects the gaps between touching filled discs. Legends and the Fig. 4 inset are skipped by a
  layout box. Each value's interval is ±3 px plus the axis misfit about the marker centre.
- **Error bars** (one standard deviation, as each caption says): walked along the marker's column in the
  bar-ink mask from just outside the marker to the cap. A bar hidden in its marker is reported as at most
  the marker; an end that runs into another marker in the same column is taken as the mirror of the free
  end (the bars are standard deviations, symmetric), and the note says so. Horizontal (thickness) bars in
  Fig. 2b are not read.

Panels:

- **Fig. 1a-c, 1d (p. 2)**: photograph, AFM image, schematic of the scattering set-up, diffraction pattern.
  Left out: no plotted values (the AFM image's amplitude and wavelength are printed in the caption and
  already in data.yaml).
- **Fig. 2a (p. 3)**: photograph of the gradient film and optical micrographs. Left out: no plotted values.
- **Fig. 2b (p. 3), filled circles**: read as `fig2b_modulus` (datum `E_fig2b`), 10 points, left axis,
  calibrated on the 0-3 GPa major ticks (misfit 0.5 px) and the 160-240 nm major ticks (misfit 1.6 px).
  Error bars read at all 10 points; at 235 and 245 nm one end runs into the open circle of the same column
  and is mirrored. Runs: `run_eq2_fig2b_points` (Eq. 2 on each plotted (h, d) point, paired by thickness)
  reproduces all 10 plotted moduli (computed/plotted 0.976-0.985 with Es = 1.75 MPa, q_fig2b_Es);
  `run_mean_fig2b` gives a mean of 3.43 GPa against the caption's 3.4 ± 0.1 GPa (reproduced).
- **Fig. 2b (p. 3), open circles**: read as `fig2b_wavelength` (datum `d_fig2b`), 10 points, right axis,
  calibrated on its 8-12 µm ticks. The right axis's ticks are unevenly drawn (spacings 345, 325, 325,
  335 px), so the linear fit has a misfit of 8 px (about 0.025 µm), carried in every interval.
  `run_eq1_fig2b` (Eq. 1 with the paper's 3.4 GPa, swept over the plotted thicknesses) reproduces all 10
  wavelengths. This also bears on q_fig1b_inconsistent: by the paper's own data a 7.9 µm wavelength belongs
  to a PS film of about 152 nm (q_fig2b_settles_fig1b).
- **Fig. 3 (p. 4), filled circles**: `fig3_siebimm` (datum `E_fig3_siebimm`), 7 points at 0-40 %
  plasticizer; x calibrated on all nine 5 % ticks, y on the 0.5-3.5 GPa ticks (misfits 0.5 px). Bars at
  30 % (and the top at 20 % and 40 %) are hidden in the markers; lower ends that run into the open circle
  below are mirrored. No model predicts these values (the dashed sigmoid is "a guide to the eye" and is
  not read).
- **Fig. 3 (p. 4), open circles**: `fig3_indentation` (datum `E_fig3_indentation`), 7 points, same
  calibration; upper ends that run into the filled circle above are mirrored. Validation
  `cmp_siebimm_indentation_fig3`: reproduced at 0-15 %, close at 20 % and 40 %, not reproduced at 30 %
  (0.70 against 0.36 GPa), as the paper itself says ("discrepancies appear" above 20 %). The two series are
  on films of different thickness (q_fig3_thickness_mismatch).
- **Fig. 4 (p. 4), filled circles**: `fig4_siebimm` (datum `E_fig4_siebimm`), 13 points at 0.7-50.6 %
  porosity; x calibrated on the eleven 5 % ticks, y on the 2-8 GPa major ticks (misfits 0.5 px). The point
  at 37 % is half covered by the open circle drawn over it; its centre comes from the visible upper
  half-disc, with a three-times wider interval. Most bars are hidden in the markers ("Some error bars are
  smaller than the symbols"). Fit quality `cmp_eq4_fig4` (Eq. 4, a = 1, n = 3.45, E0 = 9 GPa added): within
  every point's bar (q_fig_eq4_all_points). The read end values 8.98 and 0.61 GPa match the caption's 9 and
  0.6 GPa, and the 50.6 % top of the axis settles the unit in q_porosity_percent (q_fig_settles_porosity_unit).
  The dashed line (Eq. 4 as the paper fitted it) is not read: it is the same model the record runs, with
  an E0 the paper does not print.
- **Fig. 4 (p. 4), open circles**: `fig4_indentation` (datum `E_fig4_indentation`), 6 points, same
  calibration. Validation `cmp_siebimm_indentation_fig4`: reproduced or close at five porosities, not
  reproduced at about 0.7 % (9.0 against 6.6 GPa, non-overlapping bars), against the caption's "excellent
  agreement through the entire range" (q_fig4_zero_porosity).
- **Fig. 4 inset (p. 4)**: optical image of isotropic wrinkles. Left out: a micrograph with no values.

Checked overlays: `figwork/<reading id>.png` (magenta crosses on every marker, bar ends as drawn).
