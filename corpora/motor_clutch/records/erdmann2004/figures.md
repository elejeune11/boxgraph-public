# Figure readings: erdmann2004

The data now use the second-pass readings (`*_code`, own code at 1800–2000 dpi; see
"Second pass (own code)" at the end). The first-pass readings below stay in `figures.yaml`, unused,
for comparison. The paper is theory only: every plotted curve is a model result (analytic or Monte
Carlo). No measured points, bars, histograms or error bars appear in any figure.

First pass: all readings are at 300 dpi on the PDF page. Calibration marks are the tick positions
printed by `boxgraph figure axes`. In the Fig. 2 panels, curves crowd the bottom and left
axes and hide the ticks there, so the marks come from dark-pixel profiles along the
inside of the top and right frame. Those ticks mirror the labelled ones and no curve
touches them. Misfit is the largest distance of a mark from the fitted axis, in pixels
(x, y). Overlays from `figure check` are in `figwork/<reading id>.png`; every mark was
checked to sit on the intended curve.

Axes printed as "log N" or "log T", with labels such as 0, -1, 4, 16, are calibrated on a
log10 scale with the same marks written as powers of ten ("10^-1", "10^16"). Fig. 4(a)'s
"log f/N0" axis is treated the same way. The base 10 is confirmed by the readings: Eq. 8
matches Fig. 4(b) on a log10 axis at all 18 points, and a natural log would be off by a
factor of 2.3.

## Fig. 1 (p. 2)
- Left out: a schematic of the model, with no values.

## Fig. 2 (p. 2): state probabilities, N0 = 10
- **(a)**: read: `fig2a_p0` is the p0 curve (gamma = 0, f = 0), at tau = 3 to 5.5, after it has
  cleared the p1/p2 bumps. x is calibrated on the top-frame ticks 1–5 and y on the right-frame
  ticks 0.2–0.8. Misfit 0.40 / 0.40 px. Compared with Eq. 5 (`cmp_fig2a_p0`): close, with one point
  just outside its interval (q_fig_reading_close). Left out: p1…p10, overlapping bumps of the same
  colour that come from the same Eq. 5 and add nothing p0 does not test.
- **(b)**: read: `fig2b_p5` is the highest plateau, p5 (gamma = 1, f = 0, reflecting), at
  tau = 1.5 to 3.5, left of its label. Misfit 0.30 / 0.33 px. Eq. 5 (`cmp_fig2b_p5`): reproduced.
  Left out: the lower plateaus, which come in coinciding pairs (p4 = p6, p3 = p7, ...) and cannot be
  told apart.
- **(c)**: read: `fig2c_p0` is the rising straight line p0 at tau = 32 to 48. The tau = 10 point was
  dropped because the trace jumped to p5 there. `fig2c_p5` is the highest tilted plateau at
  tau = 5 to 45. Both are Monte Carlo (absorbing boundary, gamma = 1, f = 0 as in (b)). x is
  calibrated on top-frame ticks 10–40 and y on right-frame ticks 0.1–0.4. Misfit 0.30 / 0.30 px.
  Compared with the exact Eq. 1 solution (q_fig_mc_exact): p5 reproduced, p0 close at one point.
- **(d)**: read: `fig2d_p0` is the p0 curve (gamma = 0, f = 50) at tau = 0.0015 to 0.003, after
  it crosses p10 and p9. Misfit 0.30 / 0.30 px. The caption says (d) follows from Eq. 6. **Eq. 6 as
  printed is not reproduced** (`cmp_fig2d_p0_eq6`: it gives p0 = 1 everywhere), while Eq. 1
  (`cmp_fig2d_p0_eq1`) reproduces all four points. This is new question **q_eq6_exponent**: in print,
  the exponential sits inside the product. Left out: p10, p9 and the smaller p_i, which crowd
  together where they cross.

## Fig. 3 (p. 3): mean number of closed bonds
- **(a)**: read: all five lines (f = 0, gamma = 1), identified from the caption ("N0 = 1, 2, 5, 10,
  and 15 (lower to upper lines)"). `fig3a_N15` and `fig3a_N10` are read at tau = 10 to 70,
  `fig3a_N5` at tau = 10 to 70, `fig3a_N2` at tau = 2 to 14, and `fig3a_N1` at tau = 2 to 8. Each
  is seeded on its own line. x is calibrated on 7 ticks (10–70) and y on 5 decades. Misfit
  0.29 / 0.20 px. Compared with the exact mean of Eq. 1: N0 = 1, 2, 10 and 15 reproduced, N0 = 5
  close at its last point. **This figure settles the pairing of the printed decay rates**
  (q_leak_order, q_num_order). The slopes give a ≈ 0.59, 0.13 and 0.008 for N0 = 2, 5 and 10, which
  is the printed list in reverse. New question **q_fig3a_order**. The N0 = 15 line is too flat to
  settle q_num_N0_15: the difference between the candidate rates is under one pixel over the plotted
  range.
- **(b)** and **(c)**: left out. They show single Monte Carlo trajectories, which no model predicts.
  The dotted mean curves N(tau) are interleaved with the fluctuating trajectories of the same colour
  and are themselves dotted, so neither a trace nor a marker reading can isolate them.
- **(d)**: read: the stochastic solid lines `fig3d_stoch_N10` (tau = 1 to 3) and `fig3d_stoch_N5`
  (tau = 1 to 2) as traced curves, avoiding tau ≤ 0.5, where solid and dashed coincide, and the
  crossings. The deterministic dashed lines `fig3d_det_N10` and `fig3d_det_N5` are read in markers
  mode: each dash is one blob, inside a sub-box that holds only that dashed line. The solid lines
  crossing the sub-box are long blobs, excluded by max_area. This is needed because the dash gaps
  (about 10 px) are longer than the trace can bridge. x is calibrated on 6 ticks (0.5–3). y has only
  the two labelled marks (log N = 0 and 1); no other tick is printed, hence the validator warning.
  Misfit 0.40 / 0.00 px. Stochastic vs exact Eq. 1 mean: reproduced. Deterministic vs Eq. 4
  integrated numerically: N0 = 5 reproduced, N0 = 10 close (two dashes within a pixel). The
  figure's point, that stochastic and deterministic N(tau) differ, is borne out by both models.

## Fig. 4 (p. 4): cluster lifetime T, in units of 1/k0
- **(a)**: read: the five solid lines (gamma = 0, N0 = 1 to 10 000 from lower to upper), each on
  its plateau and shoulder, left of where it meets the dotted curve: `fig4a_N10000`, `fig4a_N1000`,
  `fig4a_N100`, `fig4a_N10` and `fig4a_N1`. x is calibrated on 6 decades (10^-5 to 1) and y on
  T = 2–10. Misfit 0.37 / 0.30 px. Compared with the gamma = 0 lifetime T = sum 1/r(i): all
  reproduced. Also read: the dotted approximation `fig4a_approx`, three dashes at the top left
  where it is clear of the solid lines, in markers mode in a sub-box. It is reproduced by
  T = ln[0.61(N0/f)] (`cmp_fig4a_approx`). With a factor 1 the curve would sit about 0.5 higher
  (≈ 12 px), so the drawn curve does use the printed 0.61. This lets the curve be checked, which
  q_fig4a_061 said was impossible, but it does not explain where 0.61 comes from, so q_fig4a_061
  stays open. Left out: the region f/N0 > 10^-2, where all solid lines merge with each other and
  with the dotted curve.
- **(b)**: read: all four lines (f = 0; gamma = 0.0, 0.1, 1.0, 10.0 from lower to upper).
  `fig4b_g10` is read at N0 = 5 to 20 (it leaves the plot at log T = 20), `fig4b_g1` at
  N0 = 10 to 70, `fig4b_g01` at N0 = 40 to 70, and `fig4b_g0` at N0 = 50 to 70. The two lowest
  lines run within a few pixels of each other at smaller N0. x is calibrated on 7 ticks (10–70) and
  y on log T = 4, 8, 12, 16. Misfit 0.29 / 0.40 px. Compared with Eq. 8 (dimensionless): all
  reproduced.

## Second pass (own code)

Each first-pass reading has been re-read by the record's own code (`mode: code`), with id
`<old id>_code`, the same curve and the same `at` positions. The dashed lines read as dashes have
no `at`, as before. Each datum that used an old reading now uses the new one; nothing else in the data
changed. Crops are rendered at 1800 dpi (Figs. 2 and 4) or 2000 dpi (Fig. 3), so each plot box is
1580–1660 px on its shorter side. Overlays: `figwork/<id>_code.png`; on every overlay the marks sit on
the intended line or dash.

**How it reads** (`figures/_axes.py`, shared; each `figures/<id>.py` names its panel and curve):
- *Frame*: the four longest dark lines.
- *Ticks*: strokes in a band 9–15 px inside the frame. At this resolution the dotted minor ticks
  reach 6–7 px and the major ones 18–20 px, so the band holds only major ticks. Then the longest
  evenly spaced subset. Values come from the printed labels matched to the ticks: an anchor (a
  labelled frame edge, or the first tick in Fig. 4(b)) and a step per tick. Labelled frame edges are
  added as marks. The bottom frame is used only where no curve lies along it.
- *Fig. 3(d) y axis*: it has only two printed labels, and its minor ticks are at log10 of 2…9 and
  0.5…0.9. Every tick, minor or major, is matched to its log10 value: 13 marks, misfit 0.53 px.
- *Curves*: a dark run picked by a stated rule (e.g. "the topmost line just inside the right frame",
  "the second line from the bottom at N0 = 70") is followed column by column. Each step takes the run
  nearest a straight-line prediction from the last 40 traced columns; a run thicker than 1.3× the line
  is a crossing, where the prediction is kept. Where labels or dashes would interfere, only blobs of at
  least 20000 px are traced: in Fig. 2(c) p5 that removes the "(c)" and "p5" labels, and in Fig. 3(d)
  the solid lines, it removes the dashes.
- *Dashes*: separate blobs of 300–4000 px, linked into chains along each dash's direction. Each dash
  is read at its centroid.
- *Interval (95%)*: a quarter of the line thickness (≈ 3 px) + the y misfit (≥ 0.5 px) + |slope| ×
  the x misfit (≥ 0.5 px); at a crossing, the whole merged run. Dashes take 1 px + the misfits.

| new reading | rule | misfit x / y (px), marks | vs old reading (same x unless noted) |
|---|---|---|---|
| `fig2a_p0_code` | topmost line at the right frame | 0.00 (6) / 0.40 (5) | +0.4 to +1.4 %; interval ±0.2–0.6 % (old ±0.8–2.2 %) |
| `fig2b_p5_code` | topmost line at the right frame | 0.42 (11, every 0.5) / 0.40 (5) | +0.4 to +2.2 %; ±0.9 % (old ±3 %) |
| `fig2c_p0_code` | topmost line at the right frame | 0.44 (10) / 0.42 (10, every 0.05) | +0.5 to +0.7 %; ±0.4–0.5 % (old ±1.4–2 %) |
| `fig2c_p5_code` | topmost line at tau = 5, lines only | 0.44 / 0.42 | τ = 5–20: −0.0 to +0.5 %. **τ = 40, 45: old 0.279, 0.309; new 0.178, 0.171.** The old trace had jumped onto p0 (0.279 is p0 at τ = 40); the new one stays on p5. |
| `fig2d_p0_code` | topmost line at the right frame | 0.46 (7) / 0.30 (5) | +0.3 to +1.0 %; ±0.2–0.6 % (old ±0.9–2.1 %) |
| `fig3a_N15_code` | top line at tau = 40 | 0.00 (9) / 0.00 (6 decades) | +1.0 to +2.9 %; ±2.5 % (old ±8–10 %) |
| `fig3a_N10_code` | 2nd from top at tau = 40 | same | +0.3 to +2.9 %; ±2.6 % (old ±7–10 %) |
| `fig3a_N5_code` | 3rd from top at tau = 40 | same | −2.1 to +1.9 %; ±3.1–3.6 % (old ±12–15 %) |
| `fig3a_N2_code` | 2nd from bottom at tau = 5 | same | −11.5 to +1.9 %; ±7.3–7.8 % (old ±26–35 %) |
| `fig3a_N1_code` | lowest at tau = 5 | same | −9.3 to −0.2 %; ±12–13 % (old ±41 %) |
| `fig3d_stoch_N10_code` | upper solid line at tau = 1.5 | 0.39 (7) / 0.53 (13, log minor ticks) | −1.9 to +0.9 %; ±0.8 % (old ±3–3.6 %) |
| `fig3d_stoch_N5_code` | lower solid line at tau = 1.5 | same | −0.9 to +0.8 %; ±0.8 % (old ±3.1–3.3 %) |
| `fig3d_det_N10_code` | dashed chain reaching furthest right | same | 14 dashes, τ = 0.82–3.12 (old: 5 dashes, τ = 2.1–2.9). Where both have a dash: −0.4 to −1.5 % (old y calibration, see below); ±0.3 % (old ±1.9 %) |
| `fig3d_det_N5_code` | the other dashed chain | same | 9 dashes, τ = 0.65–2.12 (old: 6, τ = 1.38–2.51). Common dashes: −0.4 to −0.6 %; ±0.3 % (old ±1.9 %). The old dash at τ = 2.51 lies past the crossing with the solid N0 = 10 line. The chain read now ends at the crossing, so that dash is not read. |
| `fig4a_N10000_code` | top line at the left frame | 0.43 (7) / 0.22 (6) | −0.2 to −0.4 %; ±0.3 % (old ±0.9–1.2 %) |
| `fig4a_N1000_code` | 2nd from top at the left frame | same | −0.2 to −0.5 %; ±0.3 % (old ±1.1–1.5 %) |
| `fig4a_N100_code` | 3rd from top | same | −0.5 to 0.0 %; ±0.5 % (old ±1.6–2.2 %) |
| `fig4a_N10_code` | 4th from top | same | −1.3 to +1.3 %; ±0.8–1.1 % (old ±2.7–4 %) |
| `fig4a_N1_code` | lowest | same | −5.2 to +3.4 %; ±2.4–2.8 % (old ±8–14 %). New T = 1.003 on the plateau (exact 1). |
| `fig4a_approx_code` | all dashes in chains of ≥ 2 (top one cut by the margin) | same | The same 3 dashes; T equal to ±0.6 % (old 10.79 at the top dash, new 10.73); x differs by up to 4 % on the lower two dashes. The new (x, T) agree with ln(0.61/x) to 3 digits; the old ones are 0.04 higher in T at the middle dash. The cause in the old reading was not investigated.; ±0.1–0.2 % (old ±0.6 %) |
| `fig4b_g10_code` | topmost at N0 = 10 | 0.43 (7) / 0.34 (11) | −16 to +17 % in T (≤ 0.07 in log T); ±27–29 % (old ±100–114 %) |
| `fig4b_g1_code` | topmost at N0 = 50 | same | −1 to +10 %; ±13 % (old ±40–57 %) |
| `fig4b_g01_code` | 2nd from bottom at N0 = 70 | same | −2 to +10 %; ±10 % (old ±34–37 %) |
| `fig4b_g0_code` | lowest at N0 = 70 | same | +1 to +8 %; ±10 % (old ±34 %). The old reading was flat at 4.431 at all three N0; the new one rises 4.48 → 4.80, like H_N0. |

**Verdicts with the new readings.** Reproduced at every point: all of Fig. 2 except Eq. 6,
`cmp_fig3a_N1`, `N10`, `N15`, all of Fig. 3(d), and all of Fig. 4. `cmp_fig2d_p0_eq6` is still
not reproduced (q_eq6_exponent). `cmp_fig3a_N5` and `cmp_fig3a_N2` are close at their last point only
(N ≈ 4 × 10^-4, where the Monte Carlo line is visibly noisy).

**What the figures now settle** (new question q_fig_code_pass; existing questions unchanged):
- q_fig_reading_close: three of its four near-misses (`cmp_fig2a_p0`, `cmp_fig2c_p0`,
  `cmp_fig3d_det_N10`) came from the 300 dpi reading. For Fig. 3(d), the old calibration placed
  log N = 1 about 19 px (at 2000 dpi) below the top frame: a decade of 1234 px instead of 1254. The
  log minor ticks put log N = 1 exactly on the frame, and so does the start of the N0 = 10 curves
  (log 10 = 1 at tau = 0). Only Monte Carlo tails remain close.
- q_num_N0_15: the N0 = 15 line drops 0.011 in log10 N between tau = 10 and 70 (a ≈ 4 × 10^-4).
  That leans towards the eigenvalue over the printed 2.5 × 10^-4, but the difference is about 1.3 px,
  within each point's interval: not settled.
- q_fig3a_order: the new readings give the same slopes, so its conclusion stands.

**Still left out**: Fig. 1 (schematic); Fig. 2 lines other than those read (coinciding pairs and
crowded crossings, as in the first pass); Fig. 3(b), (c) (single trajectories, and dotted means
interleaved with them); Fig. 4(a) for f/N0 > 10^-2 (all lines merge). Nothing measured is plotted
anywhere in the paper, so there are no measured data or error bars to read.
