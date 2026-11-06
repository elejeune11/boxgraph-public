# Figures of bell1978

One bullet per figure panel. Calibrations are in `figures.yaml`; check images in `figwork/`.

- **Fig. 1 (p. 2 = 619), energy against separation of two membranes**: left out. It is a sketch
  with no tick values (only "r_s", "Separation", "Secondary minimum"), and no model in the record
  predicts it.
- **Fig. 2 (p. 2), fluid mosaic membrane**: left out. It is a drawing, not a plot.
- **Fig. 3 (p. 4 = 621), kinds of intercellular bonds A-J**: left out. It is a drawing.
- **Fig. 4 (p. 5 = 622), simplest model of bond formation**: left out. It is a drawing of the
  receptor states N1f, N2f, Nb; its model (Eqs. 10-14) is in the record from the text.
- **Fig. 5 (p. 5), bridging model**: left out. It is a drawing of receptor configurations; the
  model is not runnable (`q_fig5_model`), and no value can be read from it.
- **Fig. 6 (p. 6 = 623), free energy against receptor-ligand separation**: left out. It is a
  sketch with no tick values (labels r0, -E0, F ≈ 0, F ≈ E0/r0).
- **Fig. 7 (p. 6), the two terms of Eq. 17 against Nb**: left out. It is a sketch with no tick
  values (small F, F = Fc, large F), so there is nothing to calibrate. The critical-force
  condition it shows (tangency) is checked through Eqs. 19-20 and Table 2.
- **Fig. 8 (p. 7 = 624), log10 t* against f* = f r0/kT ln(KN2)**: read, four curves, ids
  `fig8_KL300`, `fig8_KL1000`, `fig8_KL3000`, `fig8_KL1e4` (the curves labelled KL = 300, 1000,
  3000, 10^4; KL read as KN2, as the caption's ln(KN2) implies).
  - Crop [140, 60, 1000, 830] at 300 dpi, plot box [125, 28, 842, 707] from `figure axes`.
  - x calibrated on the ticks 1.0, 2, 3, 4 (x2, x3, x4, x7); y on 2, 0, -2, -4, -6, -8 (y1, y3,
    y5, y7, y9, y11). Misfit 1.05 px (x) and 0.65 px (y). The ticks .6 and .8 were left out of
    the calibration: they lie 3 and 6 px off the linear scale that the other four define, and
    adding them would push the misfit past 1.5 px. The y ticks -10 to -14 were not found by
    `figure axes`, so y values below -8 rest on the linear extrapolation.
  - Each curve was followed from a seed at f* = 2 and read at f* = 0.8, 1.0, 1.5, 2, 2.5, 3,
    and 3.5 and 4 where the curve is still inside the box (KL=300 and 1000 to 4, KL=3000 to 3.5,
    KL=10^4 to 3). All 29 magenta marks sit on the intended curve (`figwork/fig8_*.png`),
    including those next to the curve labels and at f* = 0.8, where the curves are closest.
  - Runs: `detach_time_fig8` (Eq. 17 solved numerically in Fig. 8's variables, built from
    `detach_time_eq17`) and `detach_time_eq22_fig8` (Eq. 22, t* = E1(f* ln KN2), which the
    caption calls a good approximation for f* ≳ 1.0). Both sweep f* over each reading.
    Reproduction (Eq. 17): 21 points reproduced, 8 close, none not reproduced. The close points
    are at f* = 0.8 on all curves and near f* = 1-1.5 and 3.5 on some. Approximation (Eq. 22):
    agrees at least as well, including at f* = 0.8 (`q_fig8_low_force`).
  - The steep near-vertical branches at f* ≈ 0.6-0.7 (the critical forces) are not read: they
    are almost vertical, and the four branches overlap there, so a reading at fixed f* is
    meaningless and they cannot be told apart.
  - Bearing on open questions: the KL=300 curve near f* = 0.82 gives log10 t ≈ -4.8 for k- =
    100 /s, which supports the -4.7 reading of the Table 2 entry printed -14.7
    (`q_table2_t_misprint`; see `q_fig8_table2_misprint`). The figure cannot fix KN2 and k-
    separately (`q_table2_KN2`, `q_table2_k_minus`), because each enters log10 t only as a shift.

## Second pass (own code)

Readings are now my own code (`mode: code`) at 900 dpi. The four Fig. 8 data
(`log_tstar_fig8_KL300`, `_KL1000`, `_KL3000`, `_KL1e4`) now use the new readings. Nothing
else in them changed. The 300 dpi readings above stay in `figures.yaml`, unused, so the two
can be compared. No other figure was added. Figs. 1, 6 and 7 were looked at again: they are
sketches with no tick values. Figs. 2-5 are drawings. The paper plots no measured data
(no points, bars or error bars), so the guide's new rules on measured data and error bars
add nothing here.

- **Fig. 8, all four curves**: `fig8_KL300_code`, `fig8_KL1000_code`, `fig8_KL3000_code`,
  `fig8_KL1e4_code`. They use the same `at` positions as the first pass. Code:
  `figures/fig8_KL300_code.py`; the other three files call it for curves 1-3, and a hash pins
  it.
  - Crop [420, 180, 3000, 2490] at 900 dpi (the first pass's crop × 3). The plot box is about
    2150 × 2040 px.
  - **Calibration, all from the image.** The frame is found as the longest dark rows and
    columns.
    - y: 17 unit ticks on the left edge (2 to -14). The 9 label blobs ("2", "0", ..., "-14")
      are matched to their nearest ticks, top label = 2. Linear fit on all 17 ticks: misfit
      2.81 px (≈ 0.025 in log10 t*). The first pass used 6 ticks down to -8 and extrapolated
      below that.
    - x: the 6 ticks rising from the bottom edge, matched in order to .6, .8, 1.0, 2, 3, 4.
      The fit uses 1.0-4 only: misfit 1.69 px. The .6 and .8 ticks sit +4.5 and +12.6 px off
      that line (1.5 and 4.2 px at 300 dpi), as the first pass found.
  - **Curve.** The four curves are told apart by their order in the column at f* = 2. Each is
    traced column by column, keeping only runs of line thickness (10 px) near the predicted
    row. That way the KL labels touching the curves near f* = 3-3.5 are skipped.
  - **Values.** Each value comes from a fit over ±30 columns: a quadratic, or a straight line
    at a curve end (f* = 4), where the window has data on one side only.
  - **Interval.** y misfit + |slope| × x misfit + 2 × local rms + a quarter of the line
    width. That is ±0.06 to ±0.08, against ±0.09 to ±0.13 in the first pass.
  - **Overlays.** `figwork/fig8_*_code.png`: all 29 magenta marks sit on the intended curve,
    including next to the labels and at f* = 0.8.
  - **New against old.** They differ by 0.00 to 0.04 in log10 t*, always within both
    intervals. The new values are a little lower at large |log10 t*|, where the first pass
    extrapolated its y scale. Examples (new / old):
    - KL=300 at f* = 3.5: -10.02 / -9.98; at 4: -11.32 / -11.29.
    - KL=1000 at f* = 1.0: -3.89 / -3.87.
    - KL=3000 at f* = 2.5: -10.05 / -10.02.
    - KL=10^4 at f* = 2.5: -11.42 / -11.39.
    - At f* = 0.8 the two passes agree within 0.01 on all four curves.
  - **Against the models.** The runs and comparisons are unchanged (sweeps over the same
    data). Checked directly with the models, outside the build:
    - Most points lie within 0.06 of Eq. 17.
    - At f* = 0.8 all four curves lie 0.065-0.089 below Eq. 17 and within 0.03 of Eq. 22.
      This confirms `q_fig8_low_force`.
    - KL=3000 at f* = 1.0 and 1.5 lies 0.12 and 0.09 below both Eq. 17 and Eq. 22. KL=300
      at f* = 1.0-2.5 lies 0.04-0.07 below both. With the narrower intervals some of these
      may now fall outside them.
    - New question `q_fig8_code_reading`: the interval covers reading error, not drawing
      accuracy.
  - **Open questions.** The KL=300 value at f* = 0.8 (-2.727) supports
    `q_fig8_table2_misprint` as before. It favours the -4.7 reading of the Table 2 entry
    printed -14.7.
