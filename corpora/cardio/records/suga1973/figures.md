# Figures of suga1973

- **Fig. 1 (p. 2)**: left out. A drawing of the experimental setup (pump, assist cup, servo loop); no values.
- **Fig. 2 (p. 3)**: left out. Recorded traces (pressure, volume) of single beats in one dog: one
  recording, not a result with values to check.
- **Fig. 3A, 3B (p. 4)**: left out. Pressure-volume loops of single beats in one unidentified dog, with
  hand-drawn lines through the loops' left uppermost corners. The loops overlap (3B has many loops on top of
  each other); the corners and the lines' slopes would give Emax and Vd of a dog the paper does not
  identify, so they cannot be matched to any row of Tables 1-2. A single recording, not a result.
- **Fig. 4 (p. 5)**: left out. Recorded traces of pressure, volume and E(t) for single beats (control and
  epinephrine) in one dog, on a chart-paper grid: single recordings.
- **Fig. 5 (p. 6)**: read, as four code readings `fig5_s1` to `fig5_s4` (data `en_fig5_s1` to
  `en_fig5_s4`, origin measured, SD bars). The four symbol series are plotted staggered by about 0.017 in
  t_N around each nominal t_N = 0, 0.1, ..., 1.5, always in the same left-to-right order; reading k takes the
  k-th symbol of each group. The scan under the PDF is bilevel at about 300 dpi, so the symbols themselves
  (solid / open circle, cross, triangle) cannot be told apart and which reading is which series is left open
  (question `q_fig5_symbols`). Rendered at 1200 dpi, crop [5200, 8880, 9080, 11160].
  Calibration (all from the image, shared code `figures/_fig5.py`): the axis lines are the longest
  vertical and horizontal ink runs; the y ticks (labels 0, 0.5, 1.0) are the short marks right of the y
  axis, the x ticks (labels 0, 0.5, 1.0, 1.5) the short marks on the x axis, each set chosen as the most
  evenly spaced candidates. Linear fits: worst misfit 4.0 px on y (0.0023 in e_N) and 6.6 px on x (0.003 in
  t_N). The legend (the two equations) is masked out via its two fraction bars. Error-bar stems are found
  as narrow vertical ink; the marker is the wide band on the stem; each bar end is the centre of its cap.
  Intervals: marker centre ± (2 scan pixels + calibration misfit) = ± 0.007, widened by the marker's
  half-height where the marker touches a cap or the stem has more than one wide band (noted per point);
  bar ends ± the same as outer bounds. At t_N = 1.0 all four markers merge into one dash at e_N = 1 with
  no visible bar (normalization makes every curve 1 there); each reading takes one quarter of the dash and
  reports its SD bar as at most the marker. At t_N = 0.9 the third symbol merges with its neighbours and
  is not read (63 of 64 points read). Checked on the overlays `figwork/fig5_s*.png` and on a combined
  overlay with bar ends: every mark sits on its marker and every bar end on its cap.
  No model in the record produces this curve; it is the measured EN(tN) behind the not-runnable model
  `elastance_normalized`. The readings settle the reading problem of `q_en_not_runnable` (the series can be
  told apart by position, if not by symbol) but not the model: EN is still given only as four sets of means
  (see `q_fig5_symbols`).
- **Fig. 6A, 6B (p. 7)**: left out. Reproduced from Figs. 1B and 3 of Downing and Sonnenblick (cat
  papillary muscle, the paper's ref. 24/26): they are that paper's measurements, not this paper's, and
  belong in a record of that paper read from its own figures.
- **Fig. 7 (p. 8)**: left out. A circuit diagram and step-response traces of the volume-measuring
  instrument; no result values.
