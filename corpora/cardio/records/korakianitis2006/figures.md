# Figures of korakianitis2006: what was read

Every reading is done by code (`mode: code`): `figures/<id>.py` names the panel's printed tick
labels and which curve to take, and the shared method is in `figures/_kor.py`. Each panel is rendered
at 900 dpi. The figures are embedded rasters of about 150 dpi, so one raster pixel is about 6 px.
Every reading was checked with `boxgraph figure check` (overlays in `figwork/<id>.png`): the
crosses sit on the intended curve.

**Calibration.** Both axes are calibrated from the image itself. The axis lines are the strongest
column and row of ink. The labelled ticks are the long, evenly spaced inward ticks, matched in order
to the printed labels. Where the axis corner carries the lowest label, the x-axis row is that mark.
A straight line is fitted through the marks; its largest misfit, in pixels, is listed below and
widens every interval. The misfit is 0.5-5.7 px on y and 0.5-1.5 px on x.

**Separating curves.** All curves are black: solid, dotted or dash-dot, some with triangle markers.
At each time the reading code splits the column's ink, within ±9 px to bridge dotted gaps, into
separate tracks. A reading names, per stretch of t, which track it takes (counted from the top or
the bottom) and how many tracks it expects there. A column with a different number of tracks is
not read, and neither is a near-vertical stretch. Where two curves coincide they form one track and
the reading covers both; the interval spans the track. Each reading's `what` says which track it
takes.

**Times.** Each reading's positions come from one grid per figure family:
- Figs. 5-7 and 9-13: t = 9.85-11.15 s in steps of 0.05 s.
- Figs. 4 and 8: 10.95-12.05 s.
- Fig. 2: 9.95-11.05 s.

A reading's `at` keeps only the grid times its code reads. The times it cannot read (curves not
separable, near-vertical stretches) are left out; the code's rules record why.

**Models.** Two new models produce the curves:
- `circulation_waveform` is the record's `circulation_valves` integration, evaluated at an instant
  t. It outputs every state, the valve flows, the leaflet angles, and the four Eq. 14 terms for the
  mitral leaflet.
- `elastance_eq2_5` gives Eqs. 2, 3 and 5 as printed.

Each reading `<id>` has a run `run_<id>` that sweeps the reading's own times, producing
`<id>_pred`, and a `reproduction` comparison `cmp_<id>`. The exceptions are the Fig. 4 readings,
which have no run (see below). The runs use the configuration the figure shows:
- on-off valves (Fig. 5);
- leaflet dynamics with all K_v set to zero (Fig. 6);
- leaflet dynamics with the vortex term (Figs. 7-10, 12);
- mitral stenosis (Figs. 10, 11);
- aortic regurgitation (Figs. 12, 13).

The paper's plots are all model output; it shows no measurements, so every figure datum has
origin `predicted`.

## Panel by panel

- **Fig. 2** (p. 4), y misfit 0.5 px, x 0.5 px: read.
  - `fig2_elv`: E(lv), solid.
  - `fig2_ela`: E(la), dotted.
  - The legend's sample lines are masked with a box.
  - **Settles q_eq3_activation.** E(lv) rises smoothly from its diastolic level, about 0.07 mmHg/ml,
    to 2.50 at t = 10.30 s and is back down by 10.45 s. It is never negative. Eq. 3 as printed gives
    1.3 mmHg/ml at the start of the cycle and negative values (`cmp_fig2_elv`). The figure was made
    with an activation that peaks at about 0.3 s and ends at about 0.45 s, as the added T_s1 and
    T_s2 assume. See q_fig2_eq3.
  - The diastolic level read, 0.07 (interval about 0.05-0.085), is below Table 1's E_lv,d = 0.1;
    see q_fig2_elvd.
  - E(la) sits at 0.147 with peaks of about 0.235 near 9.95 and 10.95 s, consistent with
    E_la,min = 0.15 and E_la,max = 0.25.
- **Fig. 4(a), (b)** (p. 8), on-off valves, misfits 1.7 / 0.75 px and 3.2 / 0.75 px: read.
  - `fig4a_ao`, `fig4a_mi`, `fig4b_po`, `fig4b_ti`: the valve angles, either 0 or 75 deg.
  - No run: Eq. 7 has no leaflet angle, so no model in the record produces these curves. The
    validator warns that they are never compared; that is expected.
  - The plotted window is 11-12 s, not the 10-11 s of the other figures (q_fig_time_window).
- **Fig. 5(a)-(f)** (p. 9), on-off model, y misfits 1.4-2.9 px: read. Fourteen readings,
  `fig5a_pao` ... `fig5f_vra`, cover every curve in the panels.
  - The steep systolic upstrokes and downstrokes of the ventricular pressures and flows are not
    read, because the curves there are near-vertical or interleaved.
  - **Bears on q_audit_fig5_volume.** V(lv) reads 116.9-130.6 ml at end-diastole and 54.6 ml at
    end-systole. The curve's range is therefore about 55-131 ml (stroke volume about 76 ml), not the
    printed "approximately between 50 and 120 ml" with a stroke volume of 70 ml.
  - P(ao) and P(lv) peak at 132.8 mmHg (t = 10.25 s). That is above both the "130" and the
    "126.4 mmHg" printed for this model.
  - See q_fig5_values.
- **Fig. 6(a), (b)** (p. 10), leaflet dynamics without the vortex term, misfits 1.1-1.4 px: read.
  - `fig6a_ao`, `fig6a_mi`, `fig6b_po`, `fig6b_ti`.
  - Run with every K_v set to the printed "zero" (`Kv_zero`).
- **Fig. 7(a), (b)** (p. 10), with the vortex term, misfits 1.0-1.4 px: read.
  - `fig7a_ao`, `fig7a_mi`, `fig7b_po`, `fig7b_ti`.
  - **Bears on q_theta_min_ao and q_audit_fig_angles.** In Figs. 6, 7, 10 and 12 every closed
    leaflet reads -0.6 to 0.3 deg, with intervals of about ±0.6 deg. None reads Table 4's
    theta_min = 5 deg. The paper's runs therefore used 0 deg as the closed angle, as Section 3.3.2
    says ("changed from 0 to 25"), and every leaflet run in the record (which uses Table 4's 5 deg)
    differs from them on this point. See q_fig_closed_angle.
- **Fig. 8(a)** (p. 11), y misfit 3.4 px: read.
  - `fig8a_pressure`: the pressure effect, which is the only curve distinguishable from the zero
    track at this scale.
  - The friction, velocity and vortex effects lie on the zero track and are not read separately
    in (a); (b) reads them.
  - The pressure effect reaches -5.99e5 rad/s2 at t = 11.25 s.
- **Fig. 8(b)** (p. 11), y misfit 2.4 px: read in mid-diastole (11.55-11.8 s) and on the common zero
  track.
  - `fig8b_pressure`, `fig8b_velocity`, `fig8b_vortex`.
  - The spikes at valve opening and closing (11.0, 11.45 and 11.95 s) are left out: the three
    curves interleave there and are near-vertical.
  - The caption does not name the valve. The text (p. 11) discusses the mitral valve, so the model
    terms are the mitral leaflet's (q_fig8_valve).
- **Fig. 9(a)-(f)** (p. 12), y misfits 1.1-4.4 px: read. Fourteen readings `fig9*` cover the lines
  with triangles (leaflet dynamics with vortex), each run with the vortex-term configuration
  (`run_fig9*`).
  - Where a line with triangles coincides with its plain counterpart, the reading covers both.
  - The plain lines are not read separately: they are the on-off model already read in Fig. 5.
  - P(ao)' peaks at 117.7 mmHg, consistent with the printed 117.9.
- **Fig. 10** (p. 13), y misfit 1.6 px: read.
  - `fig10_normal`, `fig10_stenosis`.
  - **Bears on q_audit_fig_angles.** The stenotic mitral leaflet stays at 44.8-45.1 deg throughout
    diastole, not at the 50 deg limit of Table 4 and the text. See q_fig10_stenosis_angle.
- **Fig. 11(a)-(f)** (p. 14), y misfits 1.8-5.3 px: read. Fourteen readings `fig11*` cover the
  lines with triangles (mitral stenosis), each run with the stenosis configuration (`run_fig11*`).
  - The plain lines (healthy, with vortex) duplicate the lines with triangles of Fig. 9 and are not
    read again.
  - P(la)' and P(lv)' are read only where the three low tracks separate.
- **Fig. 12** (p. 15), y misfit 1.2 px: read.
  - `fig12_normal`, `fig12_regurgitation`.
  - The regurgitant leaflet's closed angle reads 24.4-25.1 deg, consistent with the 25 deg of
    Table 4.
- **Fig. 13(a)-(f)** (p. 16), y misfits 2.2-5.7 px: read. Fourteen readings `fig13*` cover the
  lines with triangles (aortic regurgitation), each run with the regurgitation configuration
  (`run_fig13*`).
  - Q(ao)' reads -38 to -60 ml/s through diastole. That is the persistent regurgitant flow the
    text calls "about 47.9 ml/s" (left out earlier because its statistic is undefined).
  - P(ao)' at the start of the cycle (t = 10.0-10.05 s) reads 66-69 mmHg, near the printed
    end-diastolic 69.3 mmHg.

## Left out

- **Fig. 1** (p. 4) is a circuit schematic and **Fig. 3** (p. 5) a drawing of leaflet forces.
  Neither has values to read.
- **The plain (no-triangle) lines of Figs. 9, 11 and 13** duplicate curves read elsewhere: Fig. 5
  for Fig. 9, and the triangle lines of Fig. 9 for Figs. 11 and 13. Where they are separate tracks,
  reading them again would add no new result.

## Notes on the comparisons

The runs use the record's model, which follows the equations as printed: Eq. 3 with its cosine
activation, Eq. 6 with no sign change, and Table 4's 5 deg closed angle. Those runs do not
reproduce the paper's waveforms (`circulation_valves` already fails the scalar results). The figure
comparisons show where and by how much the printed equations differ from the curves the authors
plotted.
