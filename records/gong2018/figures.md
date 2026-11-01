# Figures of gong2018

Every reading is done by the record's own code in `figures/`, run by each build on the page
region given in `figures.yaml`. Shared code: `_common.py` (first pass: tick finding on MATLAB
boxes, marker templates; unchanged), `_axes.py` (tick calibration on a chosen spine, with
`regular` / `anchored` filters for marks that data add or hide), `_lines.py` (thick lines and
dot bands at chosen x), `_points.py` (filled markers and their error bars), `_bars.py` (bar
charts, y-axis ticks, whiskers), `_boxplot.py` (box plots), `_dashdot.py` (dash-dotted mean
lines), and per-figure modules `_fig3a.py`, `_figs1a.py`, `_figs3d.py`, `_figs7.py`,
`_fig6.py`, `_figs5.py`, `_figs8bc.py`, `_figs8spec.py`, `_fig45b.py`, `_fig45d.py`,
`_figs6a.py`. The only paper values typed into the code are the axis labels (and, where
named in the reading's `what`, legend or category labels matched to a colour or a position).
Intervals are 95%: one source pixel of the upsampled raster (8 px at 1200 dpi; 14 px for the
coarse Fig. 3A squares), half a pixel, the calibration misfit, plus the line or band
thickness where a line or band is read. Every reading was checked with
`boxgraph figure check` and its overlay (figwork/<id>.png). Misfits below are the largest
tick-fit residual, in rendered pixels.

## Main text

- **Fig. 1A** – drawing; no values.
- **Fig. 1B** – read (first pass): `fig1b_reinf` (red circles, annulus template),
  `fig1b_noreinf` (green plus template); ticks on both spines; compared with
  `mean_field_elastic`.
- **Fig. 1C** – left out: single time courses of Pb (one KMC trajectory, which is random, and
  one ODE trace); the record's models give cycle averages, not time courses.
- **Fig. 1D** – read: `fig1d_mean`, the black dash-dotted mean speed (80.4 [79.3, 81.6] nm/s),
  indexed by the caption's eta = 1; ticks on the top and right spines (traces cross the
  others), misfit < 2 px. Compared with `mean_field_sls` (`cmp_fig1d_mean`). The traces
  themselves (KMC random, ODE time course) and the t_life arrow are not read.
- **Fig. 2A, 2C** – heat maps (values are colours); left out.
- **Fig. 2B** – read (first pass): `fig2b_ka01`, `fig2b_ka05`, `fig2b_ka2`.
- **Fig. 3A** – read: `fig3a_kl001` (blue filled squares, square template), `fig3a_kl01`
  (red rings, annulus template, one ring per grid column), `fig3a_kl1` (yellow squares: at
  each column of the marker grid fitted to the blue squares, the rows the yellow square
  fills); ticks on both spines, 0.01/100 and 55 at corners, misfit < 2 px. Markers hidden
  under another series are not read. Compared with the new wrapper `mean_field_sls_taus`
  (ka = 1.1 - kl, eta = ka (tau_s/tau_b)/ron0).
- **Fig. 3B** – heat map; left out.
- **Fig. 3C** – read: `fig3c_means`, the three dash-dotted time averages (black 71.6, green
  82.6, red 61.0 nm/s), each indexed by its legend viscosity; ticks on the top and right
  spines. The light-green dash-dot is told from the solid green trace by colour; the solid
  traces are removed by a vertical opening. Compared with `mean_field_sls` at ka = 1 and the
  added kl = 0.1 (`kl_fig3c_added`). The solid traces (deterministic ODE time courses) are
  not read: no model in the record produces time courses.
- **Fig. 3D** – schematic; left out.
- **Fig. 4A, 5A** – drawings.
- **Fig. 4B** – read: `fig4b_visco` (red dots), `fig4b_elastic` (blue dots), measured
  relaxation stiffness at chosen times 1-45 s (the dots are read as the middle of the
  colour's run in a window); the inset covers the top/right spines, so the box is the left
  and bottom axis lines and the y ticks are kept only near the evenly spaced positions
  between the labelled corners (`anchored`; red dots hide some ticks). Steep points near
  t = 0 are left out. The **inset** (normalized stiffness of the same red data and its fit)
  is not read: it repeats the main panel's red data scaled by its initial value.
- **Fig. 4C, 5C** – relaxation spectra H(tau) (a numerical inversion of the relaxation
  data, narrow peaks on zero) – not read in this pass; the timescales the paper uses from
  them are read where it marks them (Fig. S8B/C crosses, below).
- **Fig. 4D** – read: `fig4d_box` (median with the box), `fig4d_whiskers` (median with the
  whiskers), measured areas, x = position (0 elastic red, 1 viscoelastic blue);
  `fig4d_pred`, the predicted cross and triangle. y from the outward ticks of the y axis
  (0-0.5 x 10^4 um^2). The caption does not say what the boxes and whiskers show.
- **Fig. 4E, 5E, 6A-C** – heat maps; left out.
- **Fig. 5B** – read: `fig5b_visco`, `fig5b_elastic`, as Fig. 4B. Inset not read (same
  reason).
- **Fig. 5D** – read: `fig5d_box`, `fig5d_whiskers`, `fig5d_pred`, as Fig. 4D (0-1.5).
- **Fig. 6D** – read: `fig6d_elastic` (grey), `fig6d_visco` (red), measured mean ± SD
  (caption), bars and whiskers, x = the printed initial moduli 1.4, 3.4, 9 kPa.
- **Fig. 6E** – read: `fig6e_elastic`, `fig6e_visco`, predicted areas (bars only).
- **Fig. 7** – schematic; left out.

## Supporting Information

- **Fig. S1A** – read: `figs1a_ode` (red rings, annulus template), compared with
  `mean_field_elastic` (`cmp_figS1a_ode`); `figs1a_kmc` (blue squares, square template,
  one per column of the fitted marker grid), the KMC result – recorded, not compared (no KMC
  model in the record). Ticks on the top spine and the left spine (`regular` drops the
  marker that touches the spine); misfit < 2 px.
- **Fig. S1B** – two model curves (normalized integrin density, Fca/Fr) on two y axes –
  not read in this pass (no model in the record outputs them).
- **Fig. S1C-D, S2B-C, S3A-B** – single KMC trajectories (random); left out.
- **Fig. S2A, S2F** – drawings. **Fig. S2D** – KMC radius time courses; left out (random).
- **Fig. S2E** – KMC steady radius vs speed (blue points) – not read in this pass.
- **Fig. S3C** – heat maps; left out.
- **Fig. S3D** – read: `figs3d_ka01`, `figs3d_ka05`, `figs3d_ka2`, `figs3d_ka10`, the thick
  lines through the markers at chosen viscosities (the markers overlap at low viscosity);
  positions where a line is hidden under another, or runs steeply (the drops), are left
  out; grey spines (dark threshold 150), ticks on the bottom and left spines, 0.01 and 100
  at the corners. Compared with `mean_field_sls` without reinforcement (`alpha_none`).
- **Fig. S4** – heat maps and tables of levels; left out (first pass, `q_figS4_levels`).
- **Fig. S5A** – read: `figs5a_elastic`, `figs5a_visco`, measured mean ± SD (caption).
- **Fig. S5B** – heat map; left out. **Fig. S5C** – read: `figs5c_elastic`, `figs5c_visco`.
- **Fig. S6A** – read: `figs6a_k14` (blue), `figs6a_k90` (red), `figs6a_k34` (yellow, read
  as a scattered band: median row and 10-90% spread) at 3-90 s; below about 3 s the three
  series and the dashed fits lie on top of each other and are not read. Decade ticks on
  the top spine (long ticks only), y ticks on the right spine. The dashed fits are not read.
- **Fig. S6B** – spectra; not read in this pass (as Figs. 4C, 5C). **Fig. S6C** – drawing.
- **Fig. S7** – read: `figs7_model` (red line, reproduction against `mean_field_elastic`),
  and the measured speeds with error bars `figs7_pa` (black triangle; its column from its
  error bar), `figs7_ha` (blue squares), `figs7_alg` (green circles), each compared with
  `mean_field_elastic` (validation). The x axis is printed as log10 k; readings return k.
  The caption does not say what the error bars are.
- **Fig. S8A, S8D (schematic)** – drawings.
- **Fig. S8B-C, left** – read: `figs8b_bars`, `figs8c_bars` (x = bar position: 0 elastic,
  1 effective timescale, 2 multiple timescales). The bars of positions 1 and 2 are the
  values printed on p. 13: PA 96.9 [96.2, 97.6] vs 97.2 and 101.2 [100.5, 101.9] vs 101.1;
  HA 74.5 [73.8, 75.3] vs 74.6 and 75.7 [74.7, 76.7] vs 75.4 nm/s – consistent within the
  reading. (The build cannot compare a figure reading with a printed scalar, so this is
  stated here; `q_figS8_bars_text`.) The elastic bars (84.3 and 74.5 nm/s) are printed
  nowhere else.
- **Fig. S8B-C, right** – read: `figs8b_cross`, `figs8c_cross`, the green crosses marking
  the timescales chosen for the multiple-timescale runs (tau_i, H_i). The spectrum lines are
  not read. These give the timescales behind 101.1 and 75.4 nm/s but not the ka,i the runs
  used (how H maps to ka,i is not stated), so `q_gel_params` stays open (`q_figS8_crosses`).
- **Fig. S8D** – read (first pass): `figs8d_ka2_05`, `figs8d_ka2_1`, `figs8d_ka2_2`.

## Verdicts of the new comparisons

- Reproduced: Fig. 3A (all three kl, every point read), Fig. S3D for ka = 0.1, 0.5 and 2.
- Close: Fig. 1D mean (77.7 vs 80.4), Fig. S3D ka = 10 (about 5 vs 3 nm/s; `q_figS3d_ka10_floor`).
- Not reproduced: Fig. 3C means (red reproduced, black close, green 77.7 vs 82.6;
  `q_fig3c_green_mean`); Fig. S1A ODE and the Fig. S7 curve between about 1.2 and 2 pN/nm,
  the threshold shift already seen in Fig. 1B (`q_threshold_figS1a_S7`).
- Validation against the Fig. S7 measurements: PA and HA within their error bars;
  alginate close (the two softer gels lie outside the bars).

## Open questions this pass bears on

- `q_audit_unread_results`: Fig. 3A, the Fig. 3C and Fig. 1D means and Fig. S3D are now read
  and compared. The Fig. 1D mean (80.4 [79.3, 81.6]) and the Fig. 3C green mean (82.6
  [81.0, 84.1]) at the same substrate parameters overlap within the reading precision, so
  the two figures are consistent at that precision (`q_fig1d_fig3c_means`).
- `q_gel_params`: partly – see Fig. S8B-C right.
