"""Shared reading code for the waveform panels of Figs. 4, 5 and 6 (PDF pp. 8-10): one curve against
time (s) in one panel.

The figures are bitmaps embedded at about 300 dpi (Fig. 4 thresholded to black and white); at 1200 dpi
each source pixel is a block of about 4 x 4 px. The tick marks on the y axes are often only a pixel or
two of the source and are lost; the printed labels are not. Everything below is found in the crop.

Axes. Ink = every channel below AXIS_INK. Vertical axis lines are the narrow (<= 14 px) column groups
whose longest dark run is at least half the longest in the crop, from left to right (Fig. 4: the in vivo
axis, then the model axis of the same row; Figs. 5-6: the pressure axis, then the velocity axis). The x
axis of a panel is the lowest narrow row group whose dark run, inside that panel, covers at least 60% of
the panel width.

y calibration: the printed tick labels. Each label is a group of glyphs (connected ink parts no taller
than 1.6 times their median height) beside the axis (left of a left axis, right of a right axis, within
LABEL_REACH px), grouped into lines by overlapping rows; a label's tick row is the middle of its digits
(the minus sign is left out of the height). The label lines are matched in order, top to bottom, to the
labels passed in the panel's spec, and fitted by a straight line; the largest misfit (px) is reported and
added to every interval. A Fig. 4 model panel prints no labels: it is calibrated with the labels of the
in vivo panel beside it, after checking that the two y axes start and end on the same rows (within
AXIS_MATCH px), which they do when both share one y range; the reading says so.

x calibration: time 0 is the y axis (the bottom row of Fig. 4 and the wave intensity panels of Figs. 5-6
print 0 under it). The tick marks on the panel's own x axis (ink runs of TICK_MIN-TICK_MAX px standing up
from it, at most 12 px wide) are matched to the evenly spaced labels 0.2, 0.4, 0.6, 0.8 s that the
labelled panels print under the same ticks: the evenly spaced set through the axis that the most ticks
fit (within 4 px; at least two of the four). The fit and its misfit are as for y.

Curve. Black curve = every channel below 100; gray curve (Figs. 5-6 velocity) = gray level between 120
and 225 with channels within 25 of each other, opened by a 5 px square so the anti-aliased edges of black
lines drop out. The ink inside the plot (right of the y axis, above the x axis, up to the next axis
line, a margin of 6 px from each axis line) is split into connected parts; parts narrower than 12% of
the plot width (reference numbers, wave names) are dropped. At each time asked, the curve's column is
read: the line's centre lies in the run of ink there, at least half the line's thickness w (the 25th
percentile of vertical runs of the curve) from each end of a run longer than w; runs within 3 w of each
other are one span. Interval (95%): that span, widened by 2 px (the source pixel is about 4 px) and the
y calibration misfit. A time with no curve ink within 2 px, or with two separate spans, is unreadable.
"""

import numpy as np
from scipy import ndimage

AXIS_INK = 160
TICK_INK = 230
TICK_MIN, TICK_MAX = 4, 30
LABEL_REACH = 260
AXIS_MATCH = 6


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    r = _runs(v)
    return max(r, key=lambda x: x[1] - x[0]) if r else (0, 0)


def vaxes(ink):
    """Vertical axis lines: (c0, c1, top, bottom), left to right."""
    W = ink.shape[1]
    ll = [_longest(ink[:, j]) for j in range(W)]
    ln = np.array([b - a for a, b in ll])
    out = []
    for a, b in _runs(ln > 0.5 * ln.max()):
        if b - a <= 14:
            # the line's extent: ink in any of its columns, across gaps of up to 80 px (the thin model
            # axes of Fig. 4 lose stretches of a few source pixels in the thresholded bitmap)
            merged = []
            for p, q in _runs(ink[:, a:b].any(1)):
                if merged and p - merged[-1][1] <= 80:
                    merged[-1][1] = q
                else:
                    merged.append([p, q])
            p, q = max(merged, key=lambda r: r[1] - r[0])
            out.append((a, b - 1, p, q - 1))
    # an axis line meets the x axis at a corner: some row of it lies at one end of a long horizontal
    # run; a tall narrow wave peak (Fig. 5) stands in the middle of the zero line instead
    keep = []
    for a, b, p, q in out:
        for r in range(p, q + 1):
            rr = [(s, e) for s, e in _runs(ink[r]) if s <= b and e > a]
            if rr and rr[0][1] - rr[0][0] >= 0.25 * W and (rr[0][0] >= a - 10 or rr[0][1] <= b + 11):
                keep.append((a, b, p, q))
                break
    return keep


def xaxis(ink, c0, c1):
    H = ink.shape[0]
    cover = np.array([max([q - p for p, q in _runs(ink[i, c0:c1])] or [0]) for i in range(H)])
    rows = [(a, b) for a, b in _runs(cover > 0.6 * (c1 - c0)) if b - a <= 14]
    return rows[-1][0], rows[-1][1] - 1


def label_rows(ink, ax, side, r0, r1):
    """Tick rows of the printed labels beside a y axis."""
    c0, c1, top, bot = ax
    if side == "left":
        a, b = max(0, c0 - LABEL_REACH), c0 - 4
    else:
        a, b = c1 + 5, min(ink.shape[1], c1 + LABEL_REACH)
    sub = ink[max(0, r0):r1, a:b]
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    parts = []
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        parts.append((sl[0].start, sl[0].stop, h, w))
    if not parts:
        return []
    hs = np.median([p[2] for p in parts if p[2] > 8] or [1])
    glyphs = [p for p in parts if 0.5 * hs <= p[2] <= 1.6 * hs]  # digits (minus signs and dots are flat)
    glyphs.sort()
    lines, cur = [], None
    for g in glyphs:
        if cur and g[0] < cur[1] - 2:
            cur = [min(cur[0], g[0]), max(cur[1], g[1])]
            lines[-1] = cur
        else:
            cur = [g[0], g[1]]
            lines.append(cur)
    return [max(0, r0) + (p + q - 1) / 2.0 for p, q in lines]


def _fit(p, v):
    p, v = np.array(p, float), np.array(v, float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - a) / b - p)))
    return a, b, mis


def x_ticks(ink, ax_c, c0, c1, xr0):
    """Tick marks standing up from the x axis. Ink here is every channel below TICK_INK (the ticks of
    Fig. 5 are light gray); the axis line's own blur above its core row is the median run, removed."""
    lengths = []
    for c in range(c0, c1):
        n = 0
        while n < xr0 and ink[xr0 - 1 - n, c]:
            n += 1
        lengths.append(n)
    base = float(np.median(lengths))
    lengths = [n - base for n in lengths]
    pos = [i for i, n in enumerate(lengths) if TICK_MIN <= n <= TICK_MAX]
    out, cur = [], []
    for p in pos + [None]:
        if cur and (p is None or p != cur[-1] + 1):
            if len(cur) <= 12:
                out.append(c0 + (cur[0] + cur[-1]) / 2.0 + 0.5)
            cur = []
        if p is not None:
            cur.append(p)
    return out


def fit_x(cands, x0, labels):
    """Time 0 at the axis x0; the ticks for labels[1:] evenly spaced from it."""
    c = np.array(sorted(cands), float)
    best = None
    for ci in c:
        for k in range(1, len(labels)):
            step = (ci - x0) / k
            if step < 40:
                continue
            pred = x0 + np.arange(1, len(labels)) * step
            d = np.abs(c[None, :] - pred[:, None])
            hit = d.min(1) <= 4
            m = int(hit.sum())
            if best is None or m > best[0]:
                best = (m, [x0] + [float(c[d[q].argmin()]) for q in range(len(pred)) if hit[q]],
                        [labels[0]] + [labels[q + 1] for q in range(len(pred)) if hit[q]])
    if best is None or best[0] < 2:
        raise ValueError(f"x ticks {cands} do not fit labels {labels} from the axis at {x0}")
    return _fit(best[1], best[2])


def curve_mask(img, box, kind):
    r0, r1, c0, c1 = box
    if kind == "black":
        m = img.max(2) < 100
    else:
        g = img.mean(2)
        m = (g > 120) & (g < 225) & (img.max(2) - img.min(2) < 25)
        m = ndimage.binary_opening(m, structure=np.ones((5, 5)))
    sub = np.zeros_like(m)
    sub[r0:r1, c0:c1] = m[r0:r1, c0:c1]
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    keep = np.zeros_like(sub)
    for k, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl[1].stop - sl[1].start >= 0.12 * (c1 - c0):
            keep |= lab == k
    return keep


def line_w(mask):
    lens = []
    for j in range(0, mask.shape[1], 3):
        lens += [b - a for a, b in _runs(mask[:, j])]
    return float(np.percentile(lens, 25)) if lens else 8.0


def calibrate(img, spec):
    ink = img.max(2) < AXIS_INK
    axs = vaxes(ink)
    k = spec.get("axis", 0)  # which vertical axis line bounds the plot on the left
    left = axs[k]
    right = axs[k + 1] if k + 1 < len(axs) else None
    c_end = right[0] if right else ink.shape[1]
    xr0, xr1 = xaxis(ink, left[1] + 1, c_end)
    notes = []
    # y labels: beside the axis named by the spec
    lab_axis = axs[spec.get("label_axis", k)]
    side = spec.get("side", "left")
    rows = label_rows(ink, lab_axis, side, min(left[2], lab_axis[2]) - 40, xr1 + 40)
    if len(rows) != len(spec["y"]):
        raise ValueError(f"y labels: found {len(rows)} label lines at {rows}, expected {len(spec['y'])}")
    if lab_axis != left and side == "left":
        # this panel's own tick marks (short runs right of its axis) must sit on the label rows
        rr = list(range(max(0, left[2] - 10), min(ink.shape[0], xr0 - 8)))
        ns = []
        for r in rr:
            n = 0
            while n < 40 and ink[r, left[1] + 1 + n]:
                n += 1
            ns.append(n)
        base = float(np.median(ns))  # the axis line's own ink right of its core columns
        tk = [r for r, n in zip(rr, ns) if base + 2 <= n <= base + 30]
        tk_rows = [(a + b - 1) / 2 for a, b in _runs(np.isin(np.arange(ink.shape[0]), tk)) if b - a <= 14]
        hit = sum(1 for y in rows if any(abs(y - t) <= AXIS_MATCH for t in tk_rows))
        off = [t for t in tk_rows if all(abs(y - t) > AXIS_MATCH for y in rows)]
        if hit == 0 or len(off) > hit:
            raise ValueError(f"this panel's ticks {tk_rows} do not sit on the label rows {rows} beside it")
        notes.append(f"y labels of the in vivo panel beside it: this panel's own ticks sit on {hit} of "
                     f"{len(rows)} label rows")
    ya, yb, ym = _fit(rows, spec["y"])
    x0 = (left[0] + left[1] + 1) / 2.0
    xc = x_ticks(img.max(2) < TICK_INK, x0, left[1] + 1, c_end, xr0)
    xa, xb, xm = fit_x(xc, x0, spec["x"])
    box = (min(left[2], lab_axis[2]), xr0 - 6, left[1] + 7, c_end - 6)
    return {"ya": ya, "yb": yb, "ym": ym, "xa": xa, "xb": xb, "xm": xm, "box": box, "notes": notes}


def read_envelope(img, at, spec, cal):
    """Wave intensity panels of Figs. 5-6: forward WI is plotted positive and backward WI negative, both
    as black lines that lie on the zero line when there is no wave; expansion waves are filled black
    between the line and zero. spec["envelope"] = "upper" reads the forward line as the top edge of the
    ink in each column, "lower" the backward line as its bottom edge. Ink parts that do not span at least
    40% of the plot width (wave names and their leader lines) are left out. In a column the edge run is
    read like a line when its edge is level with the neighbouring columns' (within w/2 over +-3 px: a
    flat top, a peak or a filled wave), the line centre then w/2 inside the edge; where the edge slopes
    more steeply the line centre may lie anywhere in the run (less w/2 at each end), which is the
    interval. Interval widened by 2 px and the y misfit, as for lines."""
    ya, yb, ym, xa, xb, xm = (cal[k] for k in ("ya", "yb", "ym", "xa", "xb", "xm"))
    r0, r1, c0, c1 = cal["box"]
    m = img.max(2) < 100
    sub = np.zeros_like(m)
    sub[r0:r1, c0:c1] = m[r0:r1, c0:c1]
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    mask = np.zeros_like(sub)
    for k, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl[1].stop - sl[1].start >= 0.4 * (c1 - c0):
            mask |= lab == k
    up = spec["envelope"] == "upper"

    def edge(col):
        rr = _runs(mask[:, col])
        if not rr:
            return None
        return rr[0] if up else rr[-1]

    # line thickness: the zero line where no wave is drawn (the most common run length)
    lens = [b - a for j in range(c0, c1, 5) for a, b in _runs(mask[:, j])]
    w = float(np.median(lens)) if lens else 8.0
    scale = spec.get("scale", 1)
    out = []
    for t in at:
        col = int(round((t - xa) / xb - 0.5))
        run = edge(col)
        nb = [edge(col + d) for d in (-3, 3)]
        if run is None or any(r is None for r in nb):
            out.append({"x": float(t), "y": None, "note": "no curve ink at this time"})
            continue
        top, bot = run[0], run[1] - 1
        e_here = top if up else bot
        e_nb = [r[0] if up else r[1] - 1 for r in nb]
        note = f"{'top' if up else 'bottom'} edge; line {w:.0f} px; misfit x {xm:.1f} px, y {ym:.1f} px"
        if max(abs(v - e_here) for v in e_nb) <= w / 2:
            c = e_here + (w / 2 - 0.5 if up else -(w / 2 - 0.5))
            lo_px = hi_px = c
        else:
            lo_px, hi_px = top + w / 2 - 0.5, bot - w / 2 + 0.5
            if hi_px < lo_px:
                lo_px = hi_px = (top + bot) / 2
            c = (lo_px + hi_px) / 2
            note += f"; steep: the line may lie anywhere in the {bot - top + 1} px run"
        e = 2 + ym
        lo_px, hi_px = lo_px - e, hi_px + e
        y = (ya + yb * (c + 0.5)) * scale
        v1, v2 = (ya + yb * (lo_px + 0.5)) * scale, (ya + yb * (hi_px + 0.5)) * scale
        out.append({"x": float(t), "y": float(y), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(col), float(c)], "px_lo": float(lo_px), "px_hi": float(hi_px), "note": note})
    return out


def read_spec(image, at, spec):
    img = np.asarray(image)[:, :, :3].astype(int)
    cal = calibrate(img, spec)
    if spec.get("envelope"):
        return read_envelope(img, at, spec, cal)
    ya, yb, ym, xa, xb, xm = (cal[k] for k in ("ya", "yb", "ym", "xa", "xb", "xm"))
    mask = curve_mask(img, cal["box"], spec.get("ink", "black"))
    w = line_w(mask)
    scale = spec.get("scale", 1)
    out = []
    for t in at:
        col = int(round((t - xa) / xb - 0.5))
        hits = []
        for dc in (0, -1, 1, -2, 2):
            if 0 <= col + dc < mask.shape[1]:
                hits = _runs(mask[:, col + dc])
                if hits:
                    break
        if not hits:
            out.append({"x": float(t), "y": None, "note": "no curve ink at this time"})
            continue
        grp, cur = [], [hits[0]]
        for r in hits[1:]:
            if r[0] - cur[-1][1] <= 3 * w:
                cur.append(r)
            else:
                grp.append(cur)
                cur = [r]
        grp.append(cur)
        if len(grp) > 1:
            out.append({"x": float(t), "y": None, "note": f"{len(grp)} separate ink spans in this column"})
            continue
        note = "; ".join([f"line {w:.0f} px; misfit x {xm:.1f} px, y {ym:.1f} px"] + cal["notes"])
        top, bot = grp[0][0][0], grp[0][-1][1] - 1
        if bot - top + 1 > w:
            lo_px, hi_px = top + w / 2 - 0.5, bot - w / 2 + 0.5
            if bot - top + 1 > 2 * w:
                note += f"; steep: the line spans {bot - top + 1} px here"
        else:
            lo_px = hi_px = (top + bot) / 2
        e = 2 + ym
        lo_px, hi_px = lo_px - e, hi_px + e
        mid = (top + bot) / 2
        y = (ya + yb * (mid + 0.5)) * scale
        v1, v2 = (ya + yb * (lo_px + 0.5)) * scale, (ya + yb * (hi_px + 0.5)) * scale
        out.append({"x": float(t), "y": float(y), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(col), float(mid)], "px_lo": float(lo_px), "px_hi": float(hi_px), "note": note})
    return out
