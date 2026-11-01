# Audit of erdmann2004

Second, independent reading of `corpus/2004_Erdmann.pdf` (PDF pp. 1-4) against the record,
by claude-opus-5-5 on 2026-10-30. Every value in `data.yaml` and every model equation was checked
against the page images.

## Transcription check (no changes needed)

- `xb_typical`, `T_typical`, `Fb_typical` (p. 1): image shows "xb ~ 1 nm and T ~ 300 K", "Fb ~ 4 pN". Correct, including the "~".
- `gamma_fig3a`, `f_fig3a` (p. 3, Fig. 3 caption): "f = 0, γ = 1". Correct.
- `a_leakage` (p. 3): "a ≈ 4.6 × 10^-4 9.7 × 10^-3, 0.16 and 0.5 for N0 = 2, 5, 10, and 15". Digits, exponents and the missing comma are as recorded.
- `a_numerical` (p. 3): "a = 2.5 × 10^-4, 8.5 × 10^-3, 0.13 and 0.6". Correct.
- `gamma_fc`, `fc_over_N0_printed` (p. 3): "For γ = 1, we have fc/N0 = 0.278". Correct.
- `Gamma_euler` (p. 3): "Γ = 0.577". Correct.
- `k0_1Hz`, `gamma_1`, `gamma_none`, `T_one_day`, `N0_20`, `gamma_01`, `T_gamma01`, `N0_150` (p. 4): "k0 = 1 Hz", "T ~ 10^5 s", "N0 = 20", "γ = 0.1", "7 s", "N0 = 150". Correct.
- `k0_integrin`, `Fb_integrin`, `Fc_set`, `N0_1e4`, `gamma_integrin_pred`, `kon_integrin_pred` (p. 4): "k0 = 0.012 Hz", "Fb = 9 pN", "Fc = 5.5 nN", "N0 = 10^4", "γ = 0.2", "kon = 0.002 Hz". Correct, including the exponent 10^4.

## Model check (no changes needed)

- `force_scale` (p. 1): Fb = kB T/xb as printed; unit conversion checked (gives 4.14 pN at 1 nm, 300 K).
- `leakage_eq5` (p. 2 Eq. 5, p. 3): Eq. 5 matches the image, including the exponent -(1+γ)τ and the denominator (1+γ)^N0; p1(∞) = N0 γ/(1+γ)^N0 is correct.
- `decay_rate_eq1` (p. 2 Eqs. 1-2): the generator matches Eq. 1 with r(i) = i e^{f/i}, g(i) = γ(N0 - i) and an absorbing i = 0. The method (eigenvalue instead of Monte Carlo fit) is the first reader's choice, already in `q_decay_method`.
- `critical_force` (p. 3): fc = N0 plog(γ/e) with x e^x = a as printed; gives 0.2785 at γ = 1.
- `rebinding_from_critical_force` (p. 4): inversion of the same formula with f = F/Fb (p. 1) and γ = kon/k0; correct.
- `lifetime_eq8`, `cluster_size_eq8` (p. 4 Eq. 8): T = 1/(1+γ)[Σ C(N0,n) γ^n/n + H_N0] matches the image. Checked that Eq. 8 at N0 = 2 gives (3+γ)/2, equal to Eq. 7 at f = 0, as the paper states.
- `cluster_size_harmonic` (p. 3): H_N0 ≈ ln N0 + 1/(2N0) + Γ as printed. Gives log10 N0 ≈ 43400 at T = 10^5 s, consistent by eye with the printed ~10^40000.

## Additions

- `cmp_leakage_vs_numerical` (p. 3), new comparison, purpose `approximation`: the paper states "thus, the leakage estimate is rather good", a claim that compares two printed lists (`a_leakage` against `a_numerical`) and was not compared yet.
- `q_fig4a_061` (p. 4), new question, kind `unstated_model`: the factor 0.61 in the Fig. 4(a) approximation T = ln[0.61(N0/f)] has no stated derivation.
- `q_one_day_value` (p. 4), new question, kind `reading`: "one day" is 86400 s, not 10^5 s. With 86400 s the γ = 0.1 cluster size is 147 rather than 149, and the γ = 0 exponent is about 37500 rather than 43400. The γ = 1 result (21) does not change.

## Checked and left as is

- `added.yaml` is empty. I found no input that the paper leaves unstated and the runs need. The cluster size N0 = 20 behind "T is down to 7 s" is implicit, but it is the printed datum `N0_20`, and the doubt is already in `q_lifetime_7s`.
- Fig. 3(b) and 3(c) use f/N0 = 0.25 and 0.3 (γ = 1). The paper says they are "below and above the critical force"; with fc/N0 = 0.2785 this is consistent. It is an inequality, so I recorded no comparison.
- The ~10^40000 is still not a datum (`q_10_40000`). This is the first reader's choice, and as an order of magnitude it would get no verdict.
- Existing questions `q_leak_order`, `q_leak_digits`, `q_num_order`, `q_num_N0_15`, `q_size_target`, `q_lifetime_7s` and `q_Fc_area` were re-derived independently. For example, N0 = 15 gives an eigenvalue of 4.21 × 10^-4 against the printed 2.5 × 10^-4, and Eq. 8 at N0 = 20, γ = 0.1 gives 6.44 s. I agree with all of them.

## Disagreements

- None with the first reader's judgements.
