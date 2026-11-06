# Figures of pries2005

Figure pass of 2026-11-04. The earlier pass could not render pages and read no figure; this pass
reads every panel that plots values, with code-mode readings (`figures/`) checked on their overlays
(`boxgraph figure check`; scratch images in `figwork/`, not committed). All panels are vector art,
rendered at 900 dpi.

Shared code: `figures/_kit.py` (line plots of Figs. 2 and 4: frame and outward ticks, thick/thin
ink separation by an opening, curve tracing from seed columns with gap bridging), `figures/_fig1.py`
(the bar charts of Fig. 1). Each reading file names its curve, seeds and matched tick labels.

- **Fig. 1 top (p. 4), VERR**: read, `f1_verr` → datum `f1_verr_fig` (4 bars, x = bar index 1-4:
  In vitro 92, In vivo 94, In vivo ESL without / with HD dependence). y calibrated on the long ticks
  0.6, 0.7, 0.8 (misfit 0.17 px). Bar value = centre of the bar's top stroke; error bar = SEM over 3
  networks (caption); upper end read at the cap, lower end hidden inside the bar and taken as the
  mirror. Values 0.707, 0.648, 0.623, 0.600. No runnable model produces it (the network simulation
  needs unpublished network data, q_network_data), so it is recorded but not compared.
- **Fig. 1 middle (p. 4), NINV**: read, `f1_ninv` → `f1_ninv_fig`; ticks 0, 5, 10, 15, 20 (misfit
  0.20 px); same method. Values 14.3, 10.0, 6.0, 4.7. Not compared (same reason).
- **Fig. 1 bottom (p. 4), HERR**: read, `f1_herr` → `f1_herr_fig`; ticks 0.6, 0.7, 0.8 (misfit
  0.00 px). Values 0.748, 0.707, 0.726, 0.649. Not compared (same reason).
- **Fig. 2 (p. 4), box plot above the graph**: read, `f2_boxplot` → `diameter_percentiles_fig`
  (origin measured): the measured vessel-diameter distribution at the 5th, 10th, 25th, 50th, 75th,
  90th, 95th percentiles (caption), read as circles = 5th/95th, whisker caps = 10th/90th, box edges
  = 25th/75th, inner line = median (the usual convention; the caption does not say which mark is
  which). x calibrated on the graph's axis below (ticks 10, 100; misfit 0.40 px, short ticks within
  0.86 px of the decade pattern). Values 5.3, 6.05, 7.7, 11.3, 17.2, 29.7, 37.3 um. No model
  predicts it.
- **Fig. 2 (p. 4), Weff curves, HD 60/45/30/20/10%**: read, `f2_weff_hd60` ... `f2_weff_hd10` →
  `weff_hd*_fig`; y ticks 0, 0.5, 1, 1.5, 2 (long ticks), x ticks 10, 100; misfit 0.40 px. Each
  curve traced from seeds at x = 7 and 17 um (left and right of the peak, by rank among the five
  dashed lines, matching the label order). Read from 6-7 to 50-60 um: below 6 um the five curves
  run together, and above ~60 um they merge with each other and with the hatched boundary; the peak
  itself (10.5-11 um) is not read. HD 10% at 6 um and HD 20% at 60 um were left out (the trace there
  sat on a neighbouring curve). Compared with `esl_thickness` (Eq. 11) swept over the read diameters
  at the labelled HD (`cmp_f2_weff_hd*`).
- **Fig. 2 (p. 4), Wph (boundary of the hatched area)**: read, `f2_wph` → `wph_fig`, 4-70 um; the
  opening removes the thinner hatching; at 60, 80 and 90 um the boundary runs into a hatch line
  and was left out. Compared with `esl_thickness` output Wph (`cmp_f2_wph`).
- **Fig. 2 (p. 4), dark-shaded constraint region**: left out; its edge is a drawn bound (the 2.8 um
  red-cell constraint), not a result of a model in the record.
- **Fig. 3 (p. 5)**: left out: micrographs, no values.
- **Fig. 4 top (p. 6), in vivo viscosity, thick lines, HD 60/45/30/20/10%**: read,
  `f4top_vivo_hd*` → `eta_vivo_hd*_fig`; log y with ticks 1, 1.5, 2, 3, 4, 5, 6, 8, 10, log x with
  10, 100, 1000; misfit 0.83 px, short x ticks within 1.36 px of the decade pattern. Traced from
  x = 3.15 um (left branch) and 12 um (right branch). Read from 3.2 to 1000 um except near the peak
  (HD 60% runs off the top of the frame at 10.5 um) and at positions where a dash gap was longer
  than 15 columns. Compared with `vivo_viscosity` (`cmp_f4top_vivo_hd*`).
- **Fig. 4 top (p. 6), glass tubes, thin lines**: read, `f4top_vitro_hd*` → `eta_vitro_hd*_fig`,
  4.5 (5 for HD 20%) to 1000 um; below 4.5 um the five steep thin lines cross the thick ones and
  each other too closely to be told apart. Seeded at x = 7 um. Compared with `vitro_viscosity`
  (Eqs. 5-7) (`cmp_f4top_vitro_hd*`).
- **Fig. 4 bottom (p. 6), in vivo HT/HD, thick lines**: read, `f4bot_vivo_hd*` → `htd_vivo_hd*_fig`;
  linear y with ticks 0.4 ... 1.0 (misfit 0.79 px). Below 6 um the five thick lines form one
  bundle, and above ~200 um (100 um for HD 30, 20, 10%) they merge again: those ranges are not read.
  Seeded at 8, 17 and 70 um. Compared with both forms of Eq. 13: `fahraeus_vivo` (as printed) and
  `fahraeus_vivo_core` (the (Dph/D)^2 variant) (`cmp_f4bot_vivo_hd*`, `cmp_f4bot_vivo_hd*_core`).
- **Fig. 4 bottom (p. 6), glass tubes, thin lines**: read, `f4bot_vitro_hd*` → `htd_vitro_hd*_fig`,
  from 4-6 um to 200 um (40 um for HD 20%, 30 um for HD 10%: beyond, the HD 20 and 10% thin lines
  cross thick lines and each other and the trace could not be kept on one of them). Compared with
  `fahraeus_vitro` (Eq. 12) (`cmp_f4bot_vitro_hd*`).

The labelled hematocrits (60, 45, 30, 20, 10%) are recorded as data `hd_fig_*` from the curve labels
of Figs. 2 and 4, so these runs need no added hematocrit.

## What the readings show (verdicts are computed by the build; summarised here)

- Fig. 2: all five Weff curves and Wph are reproduced at every read point by Eqs. 8-11 with the
  printed parameters, which also confirms the readings and the record's reading of Eamp and Ewidth in
  um and 1/um (q_eamp_units).
- Fig. 4 top: the glass-tube curves are reproduced everywhere by Eqs. 5-7; the in vivo curves from
  ~6 um up, and HD 10% everywhere; below ~5 um the model lies above the curves for HD 20-60%
  (new question q_vivo_small_diameters).
- Fig. 4 bottom: the glass-tube curves are not reproduced by Eq. 12 as printed (new question
  q_eq12_constants: they match the older constants 0.35 and 0.01, by a hand check outside the
  record). The in vivo curves are missed at every point by Eq. 13 as printed (factor (D/Dph)^2, which
  puts HT/HD near or above 1) and mostly reproduced by the (Dph/D)^2 variant. This settles the
  direction of the factor asked about in **q_eq13_factor** (new question q_eq13_figure, which leaves
  the existing question's text unchanged); the remaining misses of the variant are of the size the
  Eq. 12 constants explain.
- q_figures (figures not read) is answered by this pass.
