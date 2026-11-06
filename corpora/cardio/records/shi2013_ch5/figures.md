# Figures of Chapter 5

All figures are embedded rasters, black on white. The record's own code reads them
(`figures/_common.py`). The axes are calibrated from the image: the labelled major ticks are
matched to the printed labels and a straight line is fitted per axis. The fit's largest misfit is
added to every interval, and a misfit over 8 px raises an error. The chapter has no measured data:
every plot is a simulation result or the prescribed drive.

- **Fig. 5-1** (p. 3), **Fig. 5-2** (p. 4): a schematic and an equivalent circuit, with no values.
- **Fig. 5-3** (p. 8): the prescribed air pressure Ps, one curve. Reading `fig5_3_ps` covers one
  cycle (36-37 s) and is compared with Eq. 5-12.
- **Fig. 5-4(a), (b)** (pp. 9-10): Pct and Qct, one curve each. Readings `fig5_4a_pct` and
  `fig5_4b_qct` cover 35.1-37.9 s in steps of 0.1 s.
- **Fig. 5-5(a), (b)** (p. 10): diaphragm displacement and velocity, one curve each. Readings
  `fig5_5a_l` and `fig5_5b_u` cover 35.95-37.05 s in steps of 0.05 s.
- **Fig. 5-6(a)** (p. 11): four curves (Pcl, Pct, Pcu, Ps).
  - First pass:
    - `fig5_6a_pcl` reads Pcl (coarse dots) around its peak, where it is the highest ink
      (36.05-36.2 s).
    - `fig5_6a_pcu` reads Pcu (fine dots) where it is the lowest ink, with Ps above it
      (36.1-36.4 s).
  - Second pass:
    - `fig5_6a_pcl_late` reads Pcl at 36.9-37.05 s, on its late rise. There it is again the
      highest ink, 30-45 px above Pct. Read with the same code.
    - `fig5_6a_pcu_late` reads Pcu at 36.05, 37.05 and 37.08 s, after Ps has risen above it.
      There Pcu is the lowest ink. Read with the same code.
    - `fig5_6a_pcu_mid` reads Pcu at 35.97, 36.9 and 36.95 s, where it runs between Ps below and
      Pct/Pcl above. It takes the second-lowest run of ink per column and the median over a
      ±12 px window, and refuses where a neighbouring curve is within 25 px. It refused 36.85 s,
      where Pct and Pcl come down to Pcu.
  - Pct is the curve of Fig. 5-4(a) and Ps that of Fig. 5-3, so neither is read again here.
  - Between about 36.45 and 36.85 s, Pcl, Pct and Pcu run within a few pixels of each other and
    cannot be told apart, so that stretch is left out.
  - The calibration misfit is under 1 px on both axes. Intervals are ±2-5 mmHg.
  - The readings cover Pcu over most of the cycle, from 35.97 s to 37.08 s. Pcu stays between
    about -6 and -3 mmHg throughout, below zero even while Qct is near its peak. This is the
    figure side of question `q_pcu_level`, and the comparisons now check it at more times.
- **Fig. 5-6(b)** (p. 11): five curves (Qci, Qcl, Qct, Qco, Qs).
  - `fig5_6b_qci` reads Qci (dashed) on its positive lobe, where it is the highest ink.
  - `fig5_6b_qs` reads Qs (dash-dot) on its negative lobe, where it is the lowest ink
    (36.5-36.75 s).
  - The lobe edges at about 36.45 and 36.78 s are near-vertical, so they are not read.
  - Qcl and Qct overlap the Qct curve of Fig. 5-4(b) or lie on the zero line, so they cannot be
    told apart and are left out.
  - The two short Qco spikes (dotted, near 36.02 and 36.35 s) were tried in the second pass and
    left out. The spike's own sides and the Qct curve lie within 5-13 px of its top at 36.02,
    36.33 and 36.35 s, and only one point (36.36 s) could be read. Also, `bioreactor_waveform`
    does not output Qco, so no comparison would be possible.
