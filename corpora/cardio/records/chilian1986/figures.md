# Figures of chilian1986

The first reading pass could not run the figure tools, so it read no figures. This figure pass
(2026-11-06) reads every figure that plots data, using calibrated code in `figures/`. Each reading
was checked with `boxgraph figure check`, and every mark sits on the marker or bar it was meant to
read. All renders are at 1200 dpi, and every interval includes the largest tick misfit. The error bars
are SE, as the paper says ("All data are presented as means ± SE", p. 5); the captions do not say.

- **Fig. 1 (p. 3)**: left out. It shows one example recording of phasic aortic and arteriolar pressure
  during a premature beat. The axes have only 0 and 100 ticks, and there is no group value to read.
- **Fig. 2 (p. 4)**: left out. It shows one example recording of microvascular and aortic pressure
  during aortic constriction and release, a single tracing.
- **Fig. 3 (p. 6), diameters of 11 vessels when covered (x = 1), exposed (2) and covered with oil (3)**:
  read as 11 readings, `fig3_vein1`-`fig3_vein5` and `fig3_artery1`-`fig3_artery6`, with the data
  `fig3_*_diam` (measured).
  - Calibration (`_fig3.py`): the y ticks 30-150 are taken from the image. The scan's left frame line
    drifts by about 25 px, so the frame is found row by row. Misfit 5.0 px (about 0.4 um), and
    intervals are ±0.6 um. The x ticks are the three condition marks.
  - Markers: filled markers (veins) are the cores of the distance transform; open markers (arteries)
    are round enclosed holes.
  - Identifying vessels: within a kind, a vessel is chosen by its rank in each condition.
    - The five veins keep the same rank across all three conditions, so all 15 of their values are read.
    - Arteries: when covered, all six are read. When exposed, the ~123-um artery's marker is hidden
      under the vein marker at ~155 um, and the ~54- and ~45-um arteries' markers overlap at 38-40 um
      with converging lines. With oil, the ~170-um artery's marker is under the vein marker at ~168 um.
    - The unassignable points are left out, and each reading's `what` says which.
  - No model in the record takes individual vessels, and none is run. The covered readings are the
    vessels behind the printed control means (96 um for arterioles, 81 um for venules, p. 5) and the
    mean absolute changes (14 ± 4, 12 ± 5 um). Those printed means could be checked from these readings
    by a model that averages them.
- **Fig. 4, left (p. 7), myocardial perfusion, control (1) and papaverine (2) bars with SE**:
  read as `fig4_perfusion`, datum `fig4_perfusion_bars` (measured).
  - Calibration (`_fig4.py`): the 5 inward y ticks (0-400). Misfit 1.8 px.
  - Each bar's value is its top edge. The upper end of the SE bar is read at the cap. The lower end is
    hidden inside the bar and taken as its mirror.
  - Compared with Table 3 through `perfusion_by_condition` (`cmp_fig4_perfusion_t3`, consistency).
    The control bar sits at Table 3's 132, not at the abstract's 139 (see `q_fig4_read`).
- **Fig. 4, right (p. 7), coronary resistance bars with SE**: read as `fig4_resistance`, datum
  `fig4_resistance_bars` (derived: the paper's quotient P/Q).
  - Same method as the left panel, with the 6 ticks 0-1.0. Misfit 4.3 px: the top tick sits a little
    off the regular spacing.
  - Compared with R = mean aortic pressure / perfusion from Table 3 (`coronary_resistance_by_condition`,
    `cmp_fig4_resistance`, reproduction). This settles `q_fig4_not_read`.
- **Fig. 5 (p. 7)**: left out. It shows one example recording of aortic and venular pressure.
- **Fig. 6 (p. 7)**: left out. It shows one example recording of aortic and arteriolar pressure.
- **Fig. 7 (p. 8), mean% of aortic pressure for 4 vessel classes, control (filled) and papaverine
  (open), with SE bars**: read as `fig7_control` and `fig7_papaverine`, data `fig7_control_pct` and
  `fig7_papaverine_pct` (derived, like Table 6). The x index is 1 large arterioles, 2 medium
  arterioles, 3 small venules, 4 medium venules.
  - Calibration (`_fig7.py`): the 5 y ticks (0-100). Misfit 1.7 px, about 0.08%.
  - The broken diameter axis is calibrated from its 5 x ticks and the y axis. It is used only to tell
    the points apart: left of the break, larger diameter = large arterioles; right of the break,
    smaller = small venules.
  - Markers are found by morphological opening. Filled markers are taken as distance-transform cores,
    open markers as round holes.
  - The SE bars are followed along the stem to the cap. The control large-arteriole point has no upper
    bar: it would lie above 100%. That end is taken as the mirror of the lower end.
  - The plotted diameters agree with Tables 4 and 5, except the large arterioles: they are drawn at
    about 290 um (control) and 300 um (papaverine), where the tables give 300 ± 31 and 325 ± 18 um.
    They are probably shifted so the two points can be told apart.
  - Compared with the Mean% from the Table 4/5 group means (`percent_by_vessel_class`,
    `cmp_fig7_control` and `cmp_fig7_papaverine`, reproduction). Also compared with Table 6
    (`table6_percent_by_vessel_class`, `cmp_fig7_t6_*`, consistency).
  - The papaverine large-arteriole point sits at 96%, which is a 4% proximal share, as in Table 6.
    So the figure does not support the "6%" of `q_lart_pap_6pct`.
  - The control large arterioles' lower SE bar is about 4 points long, where Table 6 gives ± 6 (see
    `q_fig7_lart_ctl_se`).
