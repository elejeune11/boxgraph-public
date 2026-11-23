"""Shared code for the four readings of Fig. S10 (PDF p. 34): storage modulus G' (upper panel) and
loss modulus G'' (lower panel) of fibrin gels with 10^5 cells/ml (blue) and without cells (orange),
against strain frequency. Loaded with hash pinning by figS10_*.py.

Calibration, all from the image (_kit.box_lines, spine_stubs, line_stubs):
- the plot is a box: left and right spines, top line, the line between the panels and the bottom.
- x (log10): the left spine is 0.1 Hz and the right spine 10 Hz (labels 10^-1 and 10^1 under them);
  the tick stubs above the bottom line are matched in order to 0.2 ... 0.9, 1 (10^0) and 2 ... 9 Hz.
  All 19 marks are fitted on log10(f); the misfit is the largest residual.
- y: tick stubs left of the right spine. Upper panel: 7 stubs matched to 20 ... 140 Pa; lower
  panel: 4 stubs to 20 ... 80 Pa (labels printed at the left spine).
- markers: _kit.read_disks on the series' colour mask (tolerance 60 in RGB). The marker radius r
  is the median depth of the distance transform over components deeper than 8 px; the legend
  markers are drawn larger (depth > 1.5 r) and are skipped with a margin. Markers of the other
  colour drawn on top hide parts of a marker; a marker more than half hidden is not found
  (see figures.md).
"""
import numpy as np
from scipy import ndimage

COLORS = {"blue": [0, 128, 196], "orange": [226, 100, 22]}


def read(k, image, panel, series):
    d = k.dark_mask(image, 110)
    vc, hr = k.box_lines(d)
    L, R = vc[0], vc[-1]
    top, mid, bot = hr[0], hr[1], hr[-1]
    xs = k.line_stubs(d, bot, -1, L + 10, R - 10)
    xs = sorted(xs)
    labels = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    if len(xs) != len(labels):
        raise RuntimeError(f"expected 17 x ticks, found {len(xs)}")
    X = k.Lin([(L, 0.1)] + list(zip(xs, labels)) + [(R, 10.0)], log=True)
    if panel == "upper":
        r0, r1, ylabels = top, mid, [140, 120, 100, 80, 60, 40, 20]
    else:
        r0, r1, ylabels = mid, bot, [80, 60, 40, 20]
    ys = [y for y in k.spine_stubs(d, R, -1, r0 + 8, r1 - 8)]
    if len(ys) != len(ylabels):
        raise RuntimeError(f"expected {len(ylabels)} y ticks in the {panel} panel, found {ys}")
    Y = k.Lin(list(zip(sorted(ys), ylabels)))
    mask = k.color_mask(image, COLORS[series], 60)
    dt = ndimage.distance_transform_edt(mask)
    lab, n = ndimage.label(dt > 8)
    tops = np.array(ndimage.maximum(dt, lab, range(1, n + 1))) if n else np.array([])
    r = float(np.median(tops[tops < 30])) if (tops < 30).any() else 20.0
    legend = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if tops[i - 1] > 1.5 * r:
            legend.append((sl[1].start - 10, sl[0].start - 10, sl[1].stop + 10, sl[0].stop + 10))
    box = (L - 2 * r, r0 + 3, R + 2 * r, r1 - 3)
    out = k.read_disks(X, Y, mask, r, box, legend, note=f"{series}; r {r:.0f} px; x misfit {X.misfit_px:.2g} px, y misfit {Y.misfit_px:.2g} px")
    return out
