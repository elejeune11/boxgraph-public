"""Fig. 2H and 2I (p. 3): points with error bars (+-2 SD, N = 100, caption) against tree size, and a red
fitted line through them; 2H also has blue sphere-proximity points.

Calibration (both panels): y axis = the left long vertical line, ticks out to the left matched to the
printed labels; x axis = the bottom long line, its long (labelled) ticks below it matched to 0, 200, 400
(the 0 tick sits under the y axis). Shorter minor ticks (every 20) are not used.

Points (read_points; tried, and not used by any reading: at this density it separated only 24 of the 51
points of 2I and misread several bar ends; see figures.md): boxgraph.digitize.read_markers on the black mask (gray < 110) with error bars: the thin stems
are opened away, each remaining blob is a marker at its centre, and its error bar is walked up and down
along the stem through the marker. The legend's marker is dropped: it has no error bar on either side
and the red legend line runs level through it on both sides. Markers merged with a neighbour (touching
squares in 2H) come out as one blob whose centre lies between them; such blobs, wider than 1.6 marker
widths, are dropped and named in the note of the nearest point.

Blue points (2H): the dots overlap into one band; it is traced as a line (blue mask) from x = 300.
Red fitted line: traced as in _curves.py from x = 300.
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402
import _curves as K  # noqa: E402

from boxgraph import digitize as D  # noqa: E402


def axes(image, ylabels):
    rows, cols = C.frame(image, 110, 0.45)
    yc = cols[0]
    xr = rows[-1]
    yt = [t[0] for t in C.ticks_on_vertical(image, yc[1], yc[2], "out", 20, 0, xr[2] + 20, 110, 16)]
    if len(yt) != len(ylabels):
        yt = D.regular_ticks(yt, tol=3.0)
    m = (len(yt) - 1) // (len(ylabels) - 1)
    if len(yt) != len(ylabels) and (len(yt) - 1) % (len(ylabels) - 1) == 0:
        # minor ticks as long as the labelled ones (2H: every 0.001): the labelled ones are every m-th
        yt = yt[::m]
    if len(yt) != len(ylabels):
        raise RuntimeError(f"expected {len(ylabels)} y ticks, found {yt}")
    xt = [t[0] for t in C.ticks_on_horizontal(image, xr[1], xr[2], "out", 40, yc[1] - 6, image.shape[1], 110, 32)]
    if len(xt) != 3:
        raise RuntimeError(f"expected 3 labelled x ticks (0, 200, 400), found {xt}")
    ax_x = D.Axis("linear", list(zip(xt, [0, 200, 400])))
    ax_y = D.Axis("linear", list(zip(yt, ylabels)))
    box = (yc[2] + 3, 0, image.shape[1], xr[1] - 2)
    return ax_x, ax_y, box


def _red(image):
    return C.hue_mask(image, (235, 30, 35), 80)


def read_points(image, ylabels, stem_px=5):
    """Markers: the black mask opened with a (stem_px + 4)-square removes the stems and caps; blobs are
    labelled. A single marker is a blob whose area is within 0.7-1.35 of the median blob area and which
    fills at least 0.6 of its bounding box (letters of the legend text are rings or strokes and fill
    less). Larger blobs are touching markers: they are not split, and are listed in the first point's
    note. Each marker's error bar is read by boxgraph.digitize's walk along the stem through it. The
    legend's marker is dropped: it has no stem and the red legend line runs level through it on both
    sides."""
    from scipy import ndimage

    ax_x, ax_y, box = axes(image, ylabels)
    mask = D._restrict(D.color_mask(image, "#000000", 110), box)
    k = stem_px + 4
    marks = ndimage.binary_opening(mask, structure=np.ones((k, k), bool))
    lab, n = ndimage.label(marks)
    blobs = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        sub = lab[sl] == i + 1
        area = int(sub.sum())
        if area < 100:
            continue
        fill = area / float(sub.shape[0] * sub.shape[1])
        blobs.append((sl, sub, area, fill))
    med = float(np.median([b[2] for b in blobs if b[3] >= 0.6]))
    red = _red(image)
    out, merged, dropped = [], [], []
    for sl, sub, area, fill in blobs:
        rr, cc = np.nonzero(sub)
        rr = rr + sl[0].start
        cc = cc + sl[1].start
        r, c = rr.mean() + 0.5, cc.mean() + 0.5
        if fill < 0.6 or area < 0.7 * med:
            continue
        if area > 1.35 * med:
            merged.append(f"x ~ {ax_x.to_value(c):.0f} ({area / med:.1f} markers)")
            continue
        h = 1.0 + max(ax_y.residual_px, 0.5)
        a, b = ax_y.to_value(r - h), ax_y.to_value(r + h)
        rd = D.Reading(ax_x.to_value(c), ax_y.to_value(r), min(a, b), max(a, b), True, f"marker of {area} px", (c, r))
        rd = D._bar_reading(rd, mask, int(rr.min()), int(rr.max()), ax_y, True)
        row, col = int(r), int(c)
        left = red[max(row - 3, 0): row + 4, max(col - 80, 0): col - 30].any()
        right = red[max(row - 3, 0): row + 4, col + 30: col + 80].any()
        if "within the marker" in (rd.note or "") and "upper" in rd.note and "lower" in rd.note and left and right:
            dropped.append(f"the legend marker at x ~ {rd.x:.0f}")
            continue
        out.append({"x": rd.x, "y": rd.y, "lo": rd.lo, "hi": rd.hi, "px": [c, r],
                    "bar_lo": rd.bar_lo, "bar_hi": rd.bar_hi, "bar_lo_outer": rd.bar_lo_outer, "bar_hi_outer": rd.bar_hi_outer,
                    "note": rd.note})
    out.sort(key=lambda o: o["x"])
    extra = []
    if merged:
        extra.append("touching markers not read: " + ", ".join(merged))
    if dropped:
        extra.append("dropped " + ", ".join(dropped))
    if out and extra:
        out[0]["note"] = (out[0]["note"] or "") + "; " + "; ".join(extra)
    return out


def read_blue(image, ylabels):
    ax_x, ax_y, box = axes(image, ylabels)
    rs = D.read_markers(image, ax_x, ax_y, (20, 20, 240), 90, box=box, min_area=60)
    out = [{"x": r.x, "y": r.y, "lo": r.lo, "hi": r.hi, "px": [r.px[0], r.px[1]], "note": r.note} for r in rs]
    # the legend dot stands alone far above the points: drop blobs more than 10 marker heights above the median row
    if out:
        med = float(np.median([o["px"][1] for o in out]))
        out = [o for o in out if abs(o["px"][1] - med) < 200]
    return out


def read_fit(image, at, ylabels, colour=(235, 30, 35), tol=80):
    ax_x, ax_y, box = axes(image, ylabels)
    ax_x2 = C.Axis([m[0] for m in ax_x.marks], [m[1] for m in ax_x.marks])
    ax_y2 = C.Axis([m[0] for m in ax_y.marks], [m[1] for m in ax_y.marks])
    return K.read_traced(image, at, ax_x2, ax_y2, box, colour, tol, 300, pick="lowest", max_gap=40)
