# Figures of westerhof1971

All readings are by the record's own code (`mode: code`): a thin wrapper per reading in
`figures/<id>.py` and the shared code in `figures/_imp.py`. Calibration in every panel: the scan
is rotated by 0.35-0.91 degrees, measured on the frequency axis line (a straight line fitted
through the centres of its runs) and corrected by reading in a rotated frame; the frequency ticks
are the short stubs under the axis, matched to the printed labels 0, 2, ..., 14; the ordinate
ticks are the stubs left of the ordinate line, matched to the printed labels and the evenly spaced
unlabelled ticks between them. The axes are hand drawn (tick spacings vary by up to 10%), so the
worst misfit of the straight-line fit enters every interval. A phase panel has no frequency axis
of its own; its crop includes the modulus panel's frequency axis above it, whose ticks it shares.
Boxes around each panel's words (|Z|, the unit, FREQ (HZ), PHASE) are masked. Each reading was
checked with `boxgraph figure check` and its overlay (`figwork/<id>.png`) inspected.

Lines are read where they run alone (one run per column, no thicker than the line at its slope);
where a symbol touches the line it is interpolated (quadratic through the clean columns on both
sides) and the interval widened. Dots are what survives an opening wider than the line; rings are
found with an annulus template sized on the clean rings; crosses by their shape, inside a ring
(both diameters inked) or by the arm that sticks out of the line.

- Fig. 1 (p. 2): circuit and hydraulic diagrams and a photograph; no values. Left out.
- Fig. 2, modulus (p. 3; dog systemic model): read.
  `fig2_mod_line` (the measured model, fully drawn line) at 1-14 Hz; misfit 3.6 px in f, 4.0 px in y
  (ticks 0-800 every 200); the 1 Hz value lies on the steep part, interval about ±100.
  `fig2_mod_dots` (literature dots, measured): about 130 dots, including the outliers above 800 and
  beyond 14 Hz; a few touching pairs read as one, dots fused with the line on its steep part not read.
- Fig. 2, phase: read. `fig2_ph_line` at 1-14 Hz (misfit 6.2 px in f, 6.8 px in y; ticks -50, 0,
  +50); `fig2_ph_dots`: about 130 dots, including those above +50; one or two elongated dots missed.
- Fig. 3, modulus (p. 4; dog pulmonary model): read. `fig3_mod_line` at 1-14 Hz, `fig3_mod_dots`
  (56 dots). Ticks 0-800 every 100. The frequency ticks are the most irregular of the paper:
  misfit 20 px (0.12 Hz) in f, 14 px in y. Two small clusters of dots on the line near 1.5 and
  3.3 Hz are read as one or two dots or missed.
- Fig. 3, phase: read. `fig3_ph_line` at 1-13 Hz (the line ends just short of 14 Hz),
  `fig3_ph_dots` (58 dots); misfit 33 px (0.12 Hz) in f. A vertical cluster of four dots on the line
  near 2.6 Hz is not read.
- Fig. 4, modulus (p. 4; cat systemic model, axis "x 1000", read in kg cm^-4 sec^-1): read.
  `fig4_mod_line` (theoretical impedance) at 1.5-14 Hz (at 1 Hz the line is almost vertical and
  covered by a ring: not read); `fig4_mod_circles` (13 circles, 0.5-14 Hz, measured with the
  adapter); `fig4_mod_crosses` (10 crosses: those inside the rings at 0.5-4 Hz, on the line at 8,
  10, 12 Hz and apart at 14 Hz; the crosses at 1, 5 and 6 Hz, hidden in a filled ring or under a
  ring, are not read). Misfit 6.8 px in f, 8.7 px in y.
- Fig. 4, phase: read. `fig4_ph_line` at 1-14 Hz (1 Hz interpolated across the cluster of rings at
  the minimum, wide interval); `fig4_ph_circles` (13); `fig4_ph_crosses` (10; the crosses at 2.5
  and 3 Hz on the line next to rings are not read).
- Fig. 5, modulus (p. 5; cat pulmonary model, "x 1000"): read. Neither axis has a tick at its
  printed 0, so the axes' crossing is used as the 0 of both (the ticks 1-4 alone extrapolate to
  0.03 at the frequency axis: the hand-drawn scale is not quite linear; misfit 14 px in y).
  `fig5_mod_line` at 1-14 Hz; `fig5_mod_circles` (14; the first circle near 0.25 Hz sits on the
  ordinate line and is not read); `fig5_mod_crosses` (9; those under the rings at 3.5-4 Hz are
  not read).
- Fig. 5, phase: read. `fig5_ph_line` at 1-14 Hz; `fig5_ph_circles` (13; the circle near 8 Hz is
  drawn open, like a C, and is not found by the template); `fig5_ph_crosses` (12).
- Fig. 6 (p. 5): pressure and flow recordings of one isolated cat heart against time, with no time
  scale; single trajectories. Left out.

Every reading is a datum (`f<fig>_<panel>_<kind>_read`) compared with the three-element model
`impedance_3el` (Fig. 1A, Rc + Rp/(1 + j omega Rp C)) run with the Table 1 values of that species
and bed, swept over the reading's frequencies. The theoretical lines of Figs. 4-5 are
reproductions; the measured lines, dots, crosses and circles are validations.

What the figures settle or raise:
- q_figures_not_read: the figures are now read (q_figures_read).
- Fig. 4's theoretical line levels off near 1.13 x 10^3, below R_c = 1,200 of Table 1, and its phase
  is a few degrees more negative than the model with the Table 1 values (q_fig4_theory_rc); together
  with the measured d-c resistance (q_dc_resistance) it suggests the drawn theory used other values.
- Fig. 5's theoretical line is 2-4% under R_c = 750 at high frequency, within the uncertainty of the
  hand-drawn scale (q_fig5_theory_level).
- The measured hydraulic models turn to positive phase and rising modulus at high frequency, which
  the three-element model cannot follow (q_hydraulic_inertance); the dots are pooled literature data
  (q_literature_dots).
