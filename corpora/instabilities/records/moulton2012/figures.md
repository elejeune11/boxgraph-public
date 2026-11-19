# Figures of moulton2012

Figure pass (2026-11-14). Readings are in `figures.yaml`, each by a small wrapper in `figures/` around the
shared code `figures/_fig5.py` (its docstring gives the calibration and the intervals). The overlays were
checked by eye: every mark sits on a maximum of the black curve or on the red dashed line.

- **Fig. 5 (p. 5), shell edge radius r_s(t) for the three feedback laws**: read, panel by panel, each
  rendered at 1200 dpi (plot box about 3700 x 470 px).
  - Calibration: x from the long ticks labelled 10, 20, 30 (the short ticks fall at 5.0, 15.0, 25.0 and the
    axis origin at t = -0.008 to -0.001, both checks unused in the fit); y from the evenly spaced ticks, the
    labelled ones (1.0, 2.0) found level with their label text, step 0.2.
  - `fig5{a,b,c}_peak_t` and `fig5{a,b,c}_peak_r`: the time and the height of every maximum of r_s inside the
    box (23 in a, 24 in b, 19 in c), indexed by rib number n counted from t = 0. Peaks are the natural way to
    test a plotted oscillation: rib number, spacing (period) and amplitude, without a phase-sensitive
    point-by-point comparison. Intervals: about +-0.04-0.08 in t (the columns where the flat top stays within
    half a line width, plus the x misfit) and +-0.016-0.02 in r_s.
  - `fig5{a,b,c}_dashed`: the red dashed line (unstressed mantle radius gamma a0) at t = 1, 5, 10, 15, 20, 25,
    29.5; between dashes the value is interpolated from the neighbouring dash centres.
  - Models: `ribs_linear_eq4`, `ribs_tension_eq5`, `ribs_decreasing_eq6` swept over n; and
    `mantle_unstressed_radius` swept over t.
  - What it settles: (b) and (c) are reproduced rib by rib (times within 0.015, heights within 0.01); the
    dashed lines are 1 + 0.05t with a0 = 1. Panel (a) is not reproduced with the printed k_phi = 15 (see
    `q_kphi_fig5a`).
- **Fig. 1, 4, 7, 8**: drawings, left out.
- **Fig. 2, 3, 6(right), 9(b)**: rendered surfaces of simulated shells, left out (no values to read).
- **Fig. 6(left), 9(b, right)**: photographs of a fossil ammonite and a giant clam, left out; no measurement
  is given.
- **Fig. 9(a)**: overlaid aperture curves of the bivalve simulation with unlabelled axes; left out (no scale
  and no stated initial size, so no wavelength or fold count can be compared; `q_bivalve_not_rerun`).
- **Figs. B1, B2, C1, D1** (appendix schematics): left out.

Second pass (2026-11-14): every page (1-11) was looked at again for plotted data. Fig. 5 is the paper's only
figure with labelled axes, and the record holds no eye-read ("~") values. All nine readings were checked again
with `boxgraph figure check` (overlays `figwork/<reading id>.png`): every mark sits on its maximum or dash, and
x misfit is 0.008-0.009 and y misfit 0.004-0.005 as before. Nothing new is read:
- Fig. 9(a) has tick marks on both axes but no tick labels, so it cannot be calibrated. The lobe count of
  the aperture curves is a count, not an axis reading, and nothing in the record predicts it, because the
  bivalve simulation cannot be rerun.
- Fig. 6 (left) and 9(b) (right) are photographs of real shells. The paper gives no measurement from them
  (no rib count, spacing or scale), so they hold no measured data to record.
