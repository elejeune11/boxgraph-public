"""Shared reading code for the waveform panels of Figs. 4 and 5 (PDF pp. 8 and 10), vector graphics
rendered at 1800 dpi. Each lettered panel has a top sub-panel (in vivo waves: thin lines for the
volunteers, a thick line for their average) and a bottom sub-panel (the 1-D model: one thick
line), each with its own y axis drawn as a vertical line with two labelled ticks, and one time
scale bar '0.8 s' under both.

Calibration, all from the image (ink: mean RGB < 128):
- the time axis: the scale bar is the lowest row band whose longest ink run spans more than 40%
  of the crop's width; its end ticks are the short vertical runs within 40 px of the bar's ends,
  15 px above or below the bar. Time is measured from the centre of the left end tick (0) to the
  centre of the right one (0.8 s). The figure gives no time origin: x is the time from the left
  end of the scale bar, and the top and bottom sub-panels are taken to share it (they are drawn
  one above the other over the same bar, 'All pulses are plotted in their natural time scale').
- the y axes: in the left 40% of the crop, above the scale bar, the vertical ink runs longer than
  5% of the crop's height, grouped into bands of adjacent columns (at most 40 px wide) sharing
  one run; the two longest bands with distinct row ranges are the top and bottom axis segments
  (the two axes need not share a column). Each segment's ticks are the short horizontal ink runs
  (< 40 px tall) 6-20 px left of its leftmost column, within 15 px of the segment, grouped within
  10 px; exactly two are required; the upper carries the larger label. With two marks per axis
  there is no misfit to measure; 1 px is allowed for where each tick is.
- the sub-panels: the top one runs from the crop's top to midway between the top segment's lower
  end and the bottom segment's upper end; the bottom one from there to 25 px above the scale bar;
  both start 25 px right of the axes.

The thick line: the ink of the sub-panel is opened with a disk of radius 8 px (then 7, then 6, if
needed), which removes the thin lines (about 12 px thick at 1800 dpi) and text strokes and keeps
the thick line; the widest connected component, which must span at least 70% of the sub-panel's
ink, is the thick line (the averaged line of Fig. 4F is thinner than elsewhere and breaks at
radius 8). At each requested time the runs of that
component in the column are found; one run is the line. Where there are several (thin lines
crowding beside the thick one survive the opening), the run nearest to the line interpolated
from single-run columns within 60 px on each side is taken and the note says so; without such
columns the time is not read. The value is the run's centre. With t the line's thickness (the
median run height where the line is flat), the interval is 1 px (centre) + 1 px (calibration) +
|slope| x 1 px (time calibration) + half the difference between the run and t*sqrt(1+slope^2)
(thin lines merged into the run widen it).
"""

import numpy as np
from scipy import ndimage


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    rr = _runs(v)
    return max(rr, key=lambda r: r[1] - r[0]) if rr else (0, 0)


def calibrate(image):
    im = image[..., :3].astype(np.int16)
    ink = (im[..., 0] + im[..., 1] + im[..., 2]) < 3 * 128
    H, W = ink.shape
    # scale bar
    rows = [r for r in range(H) if (lambda a: a[1] - a[0])(_longest(ink[r])) > 0.4 * W]
    if not rows:
        raise RuntimeError("no scale bar found")
    bands = _runs(np.isin(np.arange(H), rows))
    b0, b1 = bands[-1]
    bar_row = (b0 + b1 - 1) / 2.0
    a, b = _longest(ink[int(bar_row)])
    ends = []
    for target in (a, b - 1):
        found = []
        for r in (b0 - 15, b1 + 15):
            if 0 <= r < H:
                found += [(s + e - 1) / 2.0 for s, e in _runs(ink[r]) if e - s < 40 and abs((s + e - 1) / 2.0 - target) < 40]
        if not found:
            raise RuntimeError(f"no end tick near column {target}")
        ends.append(float(np.mean(found)))
    t0, t1 = ends
    # y axis
    left = int(0.4 * W)
    # every vertical ink run longer than 5% of the height, in the left 40%, above the scale bar
    found = {}
    for c in range(left):
        for s, e in _runs(ink[: b0 - 20, c]):
            if e - s > 0.05 * H:
                key = next((k for k in found if abs(k[0] - s) <= 20 and abs(k[1] - e) <= 20 and c - found[k][-1] <= 2), None)
                if key is None:
                    found[(s, e)] = [c]
                else:
                    found[key].append(c)
    # an axis segment: a band of adjacent columns (at most 40 px wide) sharing one long run; the
    # leftmost band for each of the two longest distinct row ranges
    cands = sorted(((k, v) for k, v in found.items() if len(v) <= 40), key=lambda kv: -(kv[0][1] - kv[0][0]))
    segs = []
    for (s, e), cols in cands:
        if all(min(e, e2) - max(s, s2) < 0.5 * (e - s) for (s2, e2), _ in segs):
            segs.append(((s, e), cols))
        if len(segs) == 2:
            break
    if len(segs) != 2:
        raise RuntimeError(f"y axis segments {[k for k, _ in cands[:5]]}")
    segs.sort(key=lambda kv: kv[0][0])
    axes = []
    for (s, e), cols in segs:
        c0 = min(cols)
        rows = set()
        for off in (6, 10, 15, 20):
            if c0 - off < 0:
                continue
            for p, q in _runs(ink[:, c0 - off]):
                if q - p < 40 and s - 15 <= p and q <= e + 15:
                    rows.add((p + q - 1) / 2.0)
        ticks = [float(np.mean(g)) for g in _group(sorted(rows))]
        if len(ticks) != 2:
            raise RuntimeError(f"ticks of segment {(s, e)}: {ticks}")
        axes.append(ticks)
    mid = (segs[0][0][1] + segs[1][0][0]) / 2.0
    x_from = max(max(cols) for _, cols in segs) + 25
    return dict(ink=ink, t0=t0, t1=t1, bar=(b0, b1), axes=axes,
                bands=[(0, int(mid)), (int(mid), int(b0 - 25))], x_from=x_from)


def _group(vals, gap=10):
    out = []
    for v in vals:
        if out and v - out[-1][-1] <= gap:
            out[-1].append(v)
        else:
            out.append([v])
    return out


def _disk(r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def read(image, at, which, labels):
    """which: 0 for the top sub-panel, 1 for the bottom one; labels: (lower, upper) printed tick labels."""
    cal = calibrate(image)
    r0, r1 = cal["bands"][which]
    lo_tick, hi_tick = cal["axes"][which][1], cal["axes"][which][0]  # rows: the lower label is further down
    lab_lo, lab_hi = labels
    ink = cal["ink"][r0:r1, cal["x_from"]:]
    cols_ink = np.flatnonzero(ink.any(axis=0))
    extent = cols_ink[-1] - cols_ink[0] if len(cols_ink) else 0
    m = None
    for rad in (8, 7, 6):
        op = ndimage.binary_opening(ink, structure=_disk(rad))
        lab, n = ndimage.label(op, structure=np.ones((3, 3)))
        if n == 0:
            continue
        objs = ndimage.find_objects(lab)
        widths = [(o[1].stop - o[1].start) if o is not None else 0 for o in objs]
        k = int(np.argmax(widths))
        if widths[k] >= 0.7 * extent:
            m = lab == (1 + k)
            break
    if m is None:
        raise RuntimeError("no thick line spanning 70% of the sub-panel at disk radius 8, 7 or 6 px")

    def runs(c):
        return _runs(m[:, c]) if 0 <= c < m.shape[1] else []

    hs = []
    for c in range(0, m.shape[1] - 12, 6):
        p, q = runs(c), runs(c + 12)
        if len(p) == 1 and len(q) == 1 and abs(sum(p[0]) - sum(q[0])) / 24.0 < 0.05:
            hs.append(p[0][1] - p[0][0])
    t = float(np.median(hs)) if hs else 28.0

    def single(c):
        rr = runs(c)
        return (rr[0][0] + rr[0][1] - 1) / 2.0 if len(rr) == 1 else None

    sec_per_px = 0.8 / (cal["t1"] - cal["t0"])
    val_per_px = (lab_hi - lab_lo) / (hi_tick - lo_tick)  # negative: rows grow downwards
    out = []
    for x in at:
        col_full = cal["t0"] + x / sec_per_px
        c = int(round(col_full)) - cal["x_from"]
        rr = runs(c)
        note = ""
        if not rr:
            out.append({"x": x, "y": None, "note": "the thick line does not reach this column"})
            continue
        if len(rr) > 1:
            left = next((k for k in range(c - 1, c - 61, -1) if single(k) is not None), None)
            right = next((k for k in range(c + 1, c + 61) if single(k) is not None), None)
            if left is None or right is None:
                out.append({"x": x, "y": None, "note": f"{len(rr)} runs and no single-run columns nearby"})
                continue
            pred = single(left) + (single(right) - single(left)) * (c - left) / (right - left)
            rr = [min(rr, key=lambda q: abs((q[0] + q[1] - 1) / 2.0 - pred))]
            note = f"several runs; the one nearest the line interpolated from columns {left - c:+d}/{right - c:+d} px; "
        a, b = rr[0]
        row = (a + b - 1) / 2.0
        nb = [single(k) for k in (c - 10, c + 10)]
        sl = abs(nb[1] - nb[0]) / 20.0 if None not in nb else (b - a) / 20.0
        expected = t * np.sqrt(1 + sl * sl)
        e = 1.0 + 1.0 + sl * 1.0 + abs((b - a) - expected) / 2.0
        R = row + r0
        y = lab_lo + (R - lo_tick) * val_per_px
        ylo = lab_lo + (R + e - lo_tick) * val_per_px
        yhi = lab_lo + (R - e - lo_tick) * val_per_px
        out.append({"x": x, "y": y, "lo": min(ylo, yhi), "hi": max(ylo, yhi), "px": [col_full, R],
                    "px_lo": R - e, "px_hi": R + e,
                    "note": note + f"run {b - a} px (line {t:.0f} px, expected {expected:.0f}); slope {sl:.2f}; "
                                   "two-tick y calibration; time from the scale bar's left end"})
    return out
