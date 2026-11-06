# Audit of bangasser2013

Second, independent reading of `corpus/motor_clutch/2013_Bangasser.pdf` (PDF pp. 1-21) against the record.
Auditor: an agent, 2026-10-31. As in the first reading, the figure tools (high-dpi rendering,
code readings) could not be run in this session: the shell only allowed the `boxgraph` CLI, so
pdftoppm and the digitizer were refused. Every check below was made on the 110 dpi page images
in `pages/` and on the text in `text/`.

## 1. Values in data.yaml against the page images

No transcription error found. Nothing in data.yaml was changed; the audit only added entries
(section 3).

- Table 1 (p. 4): nm_base, Fm_base, vu_base, nc_base, Fb_base, kon_base, koff_base, kc_base all match: 50, 2 pN, 120 nm/s, 50, 2 pN, 0.3 s^-1, 0.1 s^-1, 0.8 pN/nm.
- Fig. S1C (p. 20): nm_chan … kc_chan match: 75, 2 pN, 120 nm/s, 75, 2 pN, 1 s^-1, 0.1 s^-1, 5 pN/nm.
- Table S1 (p. 17): nm_7a 4000, nc_7a 2000, kon_7a 0.3, koff_7a 0.1, kc_7a 0.8, nc_7a_minus_clutch 500, nm_7a_minus_motor 1000, koff_7c 0.004, Fb_7c 8, Fc_7c 8, koffc_7c 10 all match the image.
- Text values: ksub_8, ksub_32 (p. 8), nc_100, nc_300, nc_5 (p. 4, Fig. 2 legend), fold_* (p. 3), nc_stall_text 110 and nc_free_text "six" (p. 4) match. S_nc_text +1.2 (p. 5), S_nm_text −0.3, S_nc_nm_text +0.9, S_kon_text +1.4, S_koff_text −0.4 (p. 6) match; the minus signs are on the image, as the first reader noted. SR_max_single_text 2.6 (p. 5) matches.
- Fig. 3B (p. 5): all 24 S/R/SR values match the image.
- Fig. 5A-C (p. 6): the 5 highlighted pairs and the 5 diagonal S values recorded match the image.
- Fig. S2 (p. 21): every cup_*/clo_* value matches the text and the image. The orange markings in `where` are right (cup_kon_koff, cup_Fb_nm, clo_Fb_nm, cup_nc_nm, clo_nc_nm, cup_nc_koff, cup_kc, clo_kc).
- Values read by eye (q_eye_readings): spot-checked on pp. 4, 7, 8, 20. Nothing is badly off. One small difference, not changed because these are the first reader's readings and get no verdict: tbinding_fig6d (p. 7) reads as "≈ 7" s. I read the dashed line at about 65 on the left axis, which is about 5.8 s on the right axis. Either way it is well below the 15 s from Eq. 10, so q_tbinding stands.

## 2. Models against the printed equations

No transcription error found; no model changed.

- range_eq2 (Eq. 2, p. 2): R = log(pmax/pmin) as printed; base 10 is the first reader's reading (q_log_base). I agree.
- sensitivity_eq3 (Eq. 3, p. 3): S = Δκ p0/(κ^p0 Δp) = d log κ/d log p; slope of a log-log line through the 0.25- to 4-fold points, as the text below Eq. 3 says. Matches.
- sr_eq4 (Eq. 4, p. 3): first line SR = S × R. Matches. The second, approximate line of Eq. 4, SR ≈ log(κ^pmax/κ^pmin), is not modelled; no printed values use it.
- nc_multiplier_eq5 / scale_kon_eq5 (Eq. 5, p. 3): p_i = c p_i,0. Matches.
- catch_slip_eq9 (Eq. 9, p. 3): koff,i* = koff exp(Fi/Fb) + koff,c exp(−Fi/Fc). Signs match the image. The lifetime 1/koff* is the first reader's addition and is already a question (q_lifetime_from_rate).
- binding_time_eq10 (Eq. 10, p. 8): sum over i = 0 … nc−1 of 1/(kon (nc − i)). Matches.
- motor_clutch_ssa (Eq. 1, p. 2; steps 1-8, p. 14): the event times, the order of steps 3-7 and the start of a new clutch at the substrate position agree with the printed algorithm and with q_ssa_details. New question q_sm_equation_number (p. 14): step 2 cites "Eq. 2" for the event times, which are Eq. 1.
- optimal_stiffness, nc_limits (p. 3 definitions): the 5% definitions are implemented as printed. The grids and simulated times are the first reader's choices and are already recorded as questions.

## 3. Printed results not yet compared: added

The record compared R and SR only for the five highlighted pairs of Fig. 5. The audit added the rest of the pairwise tables, all as arithmetic checks on printed values:

- data.yaml: 102 Fig. S2 limits (cup_<row>_<col>, clo_<row>_<col>, p. 21) for the 51 other off-diagonal pairs, and for the same pairs the Fig. 5A S, 5B R and 5C SR values (S_<row>_<col>_5a, R_…_5b, SR_…_5c, p. 6). Also the Fig. 5 diagonal entries not yet recorded: S_Fb_5a, S_Fm_5a, S_vu_5a, R_<p>_5b and SR_<p>_5c for all eight parameters (p. 6).
- runs.yaml: run_R_<row>_<col> (Eq. 2 on the Fig. S2 limits) and run_SR_<row>_<col> (Eq. 4 on the printed S and R), 51 each.
- comparisons.yaml: cmp_R_<row>_<col> against Fig. 5B, and cmp_SR_<row>_<col> against Fig. 5C, 51 each. Also 19 consistency checks between the Fig. 5 diagonals and Fig. 3B: cns_S_{Fb,Fm,vu}_5a, cns_R_<p>_5b, cns_SR_<p>_5c.
- Expected verdicts, from the rule in `boxgraph/precision.py` applied by hand (validate does not print verdicts):
  - R: 43 reproduced, 8 close (kon-Fb, kon-nc, Fm-vu, nm-vu, koff-kon, vu-kon, vu-Fb, vu-nc), none not reproduced.
  - SR: 4 not reproduced (Fb-kon, κc-Fm, κc-nm, koff-Fm), about 15 close, the rest reproduced. All of these are rounding (q_sr_pair_rounding).
  - Diagonals: all consistent; cns_SR_kc_5c passes only at the edge of the interval (q_kc_rounding).
- Still not compared, as before: the S values and the Fig. S2 limits themselves, except kon's S and the nc limits. Each needs a search over many simulations. The validator lists them as never compared.

## 4. Unstated inputs

- added.yaml is empty, and rightly so: every model input is printed (Table 1, Table S1, Fig. S1C, text). The unstated numerical settings (simulated time, seeds, κsub grid, cycle definition) are run settings. They are recorded in the run notes and as `choice`/`unstated_model` questions (q_sim_length, q_optimum_search, q_cycle_definition). No change.
- One unstated input is implicit: Fig. 6 does not say it uses the base set; run_tbinding, run_fig6b and run_fig6d assume it. That is a reasonable reading (Fig. 6E's traction peak of about 38 pN matches the base set's Fig. 2B curve), and q_tbinding already discusses other sets. No change.

## 5. Open questions added

- q_fig5_full_reading (reading, p. 6): the 172 new Fig. 5 values (153 off-diagonal, 19 diagonal) were read from a 110 dpi image; a one-unit misreading of a last digit cannot be excluded.
- q_opposite_direction_convention (reading, pp. 3, 6, 21): the paper does not say which parameter is multiplied and which is divided below the diagonal. Fm-nc and nm-nc show reciprocal limits and opposite signs of S, so the convention seems to differ between cells.
- q_kc_rounding (unexplained_difference, pp. 5-6): κc's S and SR are 0.0/0.0 in Fig. 3B and −0.02/−0.05 in Fig. 5; also −0.02 × 3.0 ≠ −0.05.
- q_sr_pair_rounding (unexplained_difference, p. 6): the four SR cells not reproduced from the printed S × R, and why (rounded S and R).
- q_koff_text_slip (possible_error, p. 16): "an increase in koff is similar to an increase in kon" contradicts p. 14; probably "a decrease in kon" was meant.
- q_sm_equation_number (possible_error, p. 14): step 2 cites Eq. 2 for the event times.

## 6. Disagreements with the first reader (judgements, not changed)

- q_measured_points_not_read (reading, p. 8, p. 20): the measured points with error bars in Fig. 7C (Kong et al.'s lifetimes, to which Eq. 9 was fitted) and Fig. S1B (Chan and Odde's flow rates) are not recorded. The guide asks for every plotted measurement. The Fig. 7C points would allow a fit_quality check of Eq. 9 with no unit conversion. They need the figure tools, which could not be run here either.
- tbinding_fig6d (p. 7): I read about 6 s rather than about 7 s (section 1). It is a by-eye value with no verdict, so I left it as it is.
