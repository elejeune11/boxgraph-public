# Figures of bowden1998

Figure pass (2026-11-13). Readings are in `figures.yaml`, each by its own code in `figures/`
(shared code in `_fig3.py` and `_fig4a.py`). Every reading was checked with `boxgraph figure check`;
the magenta marks sit on the intended curve in each overlay.

- **Fig. 1 (p. 2), preparation of metal films on PDMS**: left out. It is a schematic: its labels
  (30 um wavelength, 1.5 um depth, 2.5-6.5 cm, 1 cm, 1 mm) are annotations on a drawing, with no axes.
- **Fig. 2a-f (p. 2), optical micrographs of the wave patterns**: left out. They are micrographs with
  scale bars and no plotted values. The measured wavelengths and depths are given in the text
  (`L_measured`, `depth_unheated`, `depth_300C`).
- **Fig. 3 (p. 3), buckle wavelength against t1/t**: read. These are two model curves.
  - `fig3_E1Ep4`: the solid curve (E1/Ep = 4) at t1/t = 1, 5, 10, 15, 20, 30, 40, 50 and 54. It is
    datum `L_fig3_E1Ep4`.
  - `fig3_E1Ep2`: the dashed curve (labelled 2) at t1/t = 7, 10, 15, 20, 30, 40, 50 and 54. It is datum
    `L_fig3_E1Ep2`. Below t1/t of about 7 the two curves touch or are drawn over each other, so the
    dashed one is not read there. The code bridges gaps between dashes by linear interpolation (gaps
    up to 29 px, noted per value).
  - Calibration: rendered at 900 dpi; the plot box is about 2360 x 1790 px. The frame is found from the
    image. The long inward ticks are matched to the labels 10-50 (x) and 5-30 um (y), and a straight line
    is fitted to each axis. Misfit rms is 0.07 in t1/t (the printed ticks are slightly uneven) and
    0.003 um in y. Each 95% interval is about ±0.2-0.25 um: the line half-width (16 px lines), twice
    the rms, and the x misfit times the local slope.
  - Model: `multilayer_wavelength_ratio` is the record's composite-plate reconstruction written in t1/t
    and E1/Ep. Runs `run_multilayer_fig3_E1Ep4` and `run_multilayer_fig3_E1Ep2` sweep over the read
    positions, and comparisons `cmp_fig3_E1Ep4` and `cmp_fig3_E1Ep2` check them. These comparisons are
    reproductions of a reconstructed model, so they are reported apart from the paper's own.
  - What it settles: the curves start at about 3.7 um, which is Eq. 3's first form with t = 55 nm
    (Au/Ti), not 61t and not 50 nm. With t = 55 nm the reconstruction comes within about 5% of both
    curves; with the added 50 nm it is 6-11% low (new question `q_fig3_t55`, bearing on `q_t_which`,
    `q_t_fig3_inset` and `q_multilayer_model`). The comparisons run with the record's added t = 50 nm;
    55 nm is its listed alternative.
- **Fig. 4a (p. 3), sigma_x and sigma_y against x at a step (from Eqs. 4a, 4b)**: read. These are two
  model curves.
  - `fig4a_sx` (the curve labelled sigma_x) and `fig4a_sy` (the curve labelled sigma_y) are read at
    x = -8, -5, -3, -2, -1, 1, 2, 3, 5, 7, 10, 15 and 19 um. They are data `sx_fig4a` and `sy_fig4a`,
    as fractions of sigma_0, with compression plotted upwards.
  - Calibration: rendered at 1200 dpi from a low-resolution bitmap, with lines about 15 px wide. The x
    axis has only its two ticks, 0 and 20 um (43.1 px/um). The y axis has the x axis row as 0 and the
    marked sigma_0 tick (657 px above it). With two marks per axis no misfit can be computed. The
    intervals (about ±0.03-0.05 sigma_0) add the line half-width and the tick half-widths. Far from
    the step (x ≥ about 12 um) the two curves merge into one line and both read its centre. Near
    x = 5-10 um the label arrows are skipped by matching the curves to their neighbouring columns.
  - Model: `step_stress_eq4` is new and is Eqs. 4a and 4b as printed. Its outputs are -sigma/sigma_0,
    to match the figure's upward compression. It is run with l from Eq. 5 (`l_eq5_pred`, about 53 um)
    and nu_m = 0.33 (`run_eq4_fig4a_sx`, `run_eq4_fig4a_sy`), and checked by `cmp_fig4a_sx` and
    `cmp_fig4a_sy`.
  - What it shows: the drawn decay length is about 3.4 um, while Eq. 5 gives about 53 um, so the figure
    is not drawn with the paper's own transition length. sigma_y's minimum (about 0.75 read at ±1 um)
    agrees with Eq. 4b's (1 - nu_m) sigma_0. See new question `q_fig4a_l`.
- **Fig. 4b (p. 3)**: left out. It is a drawing of the patterned PDMS surface; its dimensions (100 um,
  500 um, 10-20 um) are annotations, not data.
- **Fig. 4c (p. 3), stress over strips (Eqs. 6a, 6b)**: left out. The x axis has no scale, only the
  symbols 2d and 2D, so no position can be calibrated. The stress axis shows only 0 and sigma_0.
- **Fig. 4d (p. 3)**: left out. It is an optical micrograph (400 um scale bar) with no plotted values.
