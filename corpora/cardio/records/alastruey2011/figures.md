# Figures of alastruey2011

An earlier pass read no figure (the figure tools were refused then; question `q_figures_unread`). This pass
reads Figs. 2-5 with calibrated readings by the record's own code (`mode: code`, 1200 dpi crops of vector art),
each checked with `boxgraph figure check` and its overlay inspected (overlays in `figwork/`, not committed).
Every axis is calibrated from the image: the frame is found as the longest dark rows and columns, the tick
marks as short inward marks on the bottom and left frame lines that start a dotted grid line, matched in order
to the printed labels, then fitted by a straight line; the largest misfit is reported in each reading's notes
and added to every interval. Shared code: `figures/_fig3.py` (frame, ticks, legend, line tracing; Fig. 3),
`_fig2.py`, `_fig4.py`, `_fig5.py`. The eye-read data of the earlier pass are kept unchanged.

- **Fig. 1** (p. 2): left out. A schematic of the setup and a photograph with segment labels; no values to read.
  It gives the topology used by `network_1d` (`q_topology`).
- **Fig. 2, top** (p. 5): read, `fig2a_load` and `fig2a_extension` (data `load_fig2a`, `extension_fig2a`,
  measured), during the two holds (20-46 s and 54-110 s, every 2 s; a few load positions unreadable). x ticks
  20-100 s (0 is on the frame), misfit 0.2 px; y ticks 1 to 0 with the 0.2 tick hidden by the curves, matched on
  the even spacing, misfit 2.6 px. The thick dashed extension line makes runs exactly 25 px tall on one row
  column after column; the noisy thin load line makes wandering runs 10-32 px tall; the legend box is found as a
  rectangle and masked. In the preconditioning cycles and the ramps the two lines lie on each other and are not
  read. No model in the record predicts these traces, so they are data only.
- **Fig. 2, bottom** (p. 5): read, `fig2b_loop` (datum `loop_fig2b`, measured), at extension 0.05-0.95. Loading
  (solid) and unloading (dashed), cubic splines through the measured points, lie within about a line width of
  each other, so they are read together as one band: either branch lies within each interval. x and y ticks
  0-1, misfit 0.7 and 0.4 px. The hysteresis area that gives phi through Eq. 9 cannot be measured from it
  (`q_fig2_loop`), so the figure does not settle the value of phi.
- **Fig. 3 (a)-(h)** (p. 6): read, all three curves of all eight panels: `fig3{a..h}_{exp,elas,visc}` (data
  `P15_*_fig3a`, `Q15_*_fig3b`, `P24_*_fig3c`, `Q24_*_fig3d`, `P30_*_fig3e`, `Q30_*_fig3f`, `P3_*_fig3g`,
  `Q3_*_fig3h`; exp measured, elas and visc predicted), at t = 0.01-0.82 s every 0.01 s where all three curves
  of a panel are readable (69-81 positions per panel). x ticks 0.2-0.8 s, y ticks as labelled inside the frame
  (labels on the frame have no tick); misfits 0.1-0.2 px (x) and 0-0.4 px (y). No error bars are drawn. The
  three black lines are told apart by stroke, measured on the legend samples: exp a 14 px solid line, visc a
  14 px dashed line (32 px dashes, 33 px gaps), elas a 5 px line. exp is traced through the opened (thick) ink;
  visc is read from the thick runs other than exp's, interpolated across dash gaps, and taken inside exp's run
  where the dashes fuse with it; elas is traced through the thin ink, and where it is hidden under a thick line
  its interval spans every thick run near its prediction. This settles the doubt of `q_figures_unread` that the
  lines might be inseparable (`q_fig3_read`). Each panel has runs of `network_1d` in both formulations swept
  over its times (`run_fig3*_elas`, `run_fig3*_visc`), compared with the paper's elas and visc curves
  (reproduction, `cmp_fig3*_elas`, `cmp_fig3*_visc`) and with the measured curve (validation,
  `cmp_fig3*_*_vs_exp`). The time origin of the figure (onsets of ejection matched, shift not printed) is an
  unstated input of those comparisons (`q_fig3_time_origin`). The measured curves at these four midpoints are
  not among boileau_data's eight released sites, so they could let a later job recompute Table 3's E_P and E_Q
  there (`q_error_tables`).
- **Fig. 4** (p. 8): read, `fig4_exp`, `fig4_elas`, `fig4_visc` (data `Qhat24_*_fig4`, log10 of ml/s; exp
  measured), all 21 markers of each kind (0 Hz and 20 harmonics). x ticks 5, 10, 15 Hz and y ticks 0, -1, -2,
  misfits 0.0 px. The three legend markers are the templates: a component matching one at intersection over
  union 0.85 or more is a single marker (singles score 0.95 or more, overlaps 0.7 or less); a kind with no single
  marker in a column is read inside the overlapping markers there; markers on the left frame (0 Hz) are cut by
  it and are placed on the frame line. No error bars are drawn. The markers sit at multiples of about 0.978 Hz,
  not at the harmonics of the 0.83 s cycle (`q_fig4_frequencies`); with the spectrum's computation unstated, no
  model in the record produces these amplitudes (`q_fig4_spectrum`), so they are data only (the validator's
  warnings on `Qhat24_elas_fig4` and `Qhat24_visc_fig4` say so).
- **Fig. 5** (p. 8): read, `fig5_elas` (datum `A15_elas_fig5`) at 10.6-15.0 kPa, and the two branches of the
  8 phi loop, `fig5_8phi_upper` and `fig5_8phi_lower` (`A15_8phi_*_fig5`), all predicted. x ticks 11-15 kPa,
  misfit 0.2 px; y ticks 5.6-6.2 cm^2, misfit 0.4 px. The elastic line (17 px) lies inside the narrow
  visco-elastic loop; the reading takes the band of runs within 45 px of a fitted reference curve, so where the
  two touch the interval holds both. The visco-elastic loop itself is not read: it never leaves the elastic
  line by more than about a line width (`q_fig5_visc`). The 8 phi branches are left out where the upper branch
  loops (13.4-14.0 kPa) and where the label's arrow touches the lower one (13.0 kPa). The elastic line is Eq. 5
  with Gamma = 0 at that point: `tube_law_mid` (beta from Table 2's c0, as `network_1d`) and `tube_law_mid_E`
  (beta from E and h) are swept over its pressures and compared (reproduction, `cmp_fig5_tube_c0`,
  `cmp_fig5_tube_E`). The c0 route lies about 0.034 cm^2 above the read line and the E route further above
  (`q_fig5_tube_law`). No run produces the 8 phi loop: `network_1d` does not report the area, and no run uses
  phi = 24 kPa s; the 8 phi branches are therefore data only (validator warnings on `A15_8phi_*_fig5`).
