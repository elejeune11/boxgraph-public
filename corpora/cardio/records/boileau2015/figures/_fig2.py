"""Shared reading code for Fig. 2 (PDF p. 8): P/Ppeak against x, one panel per scheme, rendered at
1200 dpi. The figure is vector graphics, black on white.

Calibration, all from the image:
- ink is gray < 128;
- the plot frame: the two rows (columns) whose ink spans more than 70% of the crop, top and bottom
  (left and right); their centres are y = 1.0 and y = 0.0 (x = 0 and x = 10), the frame being drawn
  at the outermost tick labels;
- the dotted grid lines at y = 0.2, 0.4, 0.6, 0.8 and x = 2, 4, 6, 8: narrow (at most 8 px) bands of
  rows (columns) holding 15-40% ink, each matched to the label whose position, predicted from the
  frame alone, lies within 6 px (grid lines hidden behind a pulse are not found and not used);
- a straight line is fitted to frame and grid marks of each axis; its largest misfit (px) widens
  every interval.

The thick line (Eq. 15): in each column within +-3 px of x, runs of ink 8 to 30 px tall that lie
away from the frame (more than 12 px inside it) and above the dashed baseline near y = 0 (more than
40 px above the bottom frame). The thin pulse lines are 2-4 px wide and steep, so at x positions
away from the pulses the thick line is the only such run. A column with no or several such runs is
not used; x with no usable column is not read. The value is the median centre of the run; the
interval is half the median run height (the line's thickness) plus the calibration misfit plus the
spread of centres across the columns (the slope).

The inviscid pulse tips (thin solid lines): ink above the 0.3 level, without the top frame line,
is split into 8-connected components. Each pulse crosses the 0.3 level as two to four flank runs
(the inviscid thin line and the viscous dashed line inside it), grouped when closer than 80 px; the
tip is the highest row of those flanks' components within the pulse's columns (+-10 px). The
viscous dashed tip lies lower, inside the thin one, so the highest row is the inviscid tip. A
group whose top lies below 0.8 is a grid dot, not a pulse. The tip's line centre is taken 1.5 px
below its top row, +-2 px plus the misfit. A tip touching the top frame (within 8 px of its centre)
is reported as hidden by the frame: y between 8 px below the frame centre and 3 px above it.
"""

import numpy as np

INK = 128


def ink_mask(image):
    return image[..., :3].astype(float).mean(axis=2) < INK


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _bands(frac, lo, hi, maxw):
    out = []
    for a, b in _runs((frac >= lo) & (frac <= hi)):
        if b - a <= maxw:
            out.append((a + b - 1) / 2.0)
    return out


def _fit(marks):
    p = np.array([m[0] for m in marks], float)
    v = np.array([m[1] for m in marks], float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - (a + b * p)) / b)))
    if mis > 4.0:
        raise RuntimeError(f"calibration misfit {mis:.1f} px: {marks}")
    return a, b, max(mis, 0.5)


def _axis(frac_full, frac_grid, ends, inner):
    frame = [(a + b - 1) / 2.0 for a, b in _runs(frac_full > 0.7)]
    if len(frame) != 2:
        raise RuntimeError(f"frame lines: {frame}")
    lo_px, hi_px = frame
    marks = [(lo_px, ends[0]), (hi_px, ends[1])]
    a0, b0, _ = _fit(marks)
    cands = _bands(frac_grid, 0.15, 0.40, 8)
    for v in inner:
        pred = (v - a0) / b0
        near = [c for c in cands if abs(c - pred) <= 6]
        if len(near) == 1:
            marks.append((near[0], v))
    a, b, mis = _fit(marks)
    return dict(a=a, b=b, mis=mis, frame=(lo_px, hi_px), marks=marks)


def calibrate(image):
    ink = ink_mask(image)
    # y: frame rows top (1.0) and bottom (0.0); grid rows inside
    ycal = _axis(ink.mean(axis=1), ink.mean(axis=1), (1.0, 0.0), [0.2, 0.4, 0.6, 0.8])
    xcal = _axis(ink.mean(axis=0), ink.mean(axis=0), (0.0, 10.0), [2.0, 4.0, 6.0, 8.0])
    return ink, xcal, ycal


def _col(xcal, x):
    return (x - xcal["a"]) / xcal["b"]


def _y(ycal, row):
    return ycal["a"] + ycal["b"] * row


def read_thick(image, at):
    ink, xcal, ycal = calibrate(image)
    top, bot = ycal["frame"]
    left, right = xcal["frame"]
    out = []
    for x in at:
        x = float(x)
        col = _col(xcal, x)
        cs, hs = [], []
        for c in range(int(round(col)) - 3, int(round(col)) + 4):
            if c <= left + 12 or c >= right - 12:
                continue
            rr = [(a, b) for a, b in _runs(ink[:, c])
                  if 8 <= b - a <= 30 and a > top + 12 and b < bot - 40]
            if len(rr) == 1:
                cs.append((rr[0][0] + rr[0][1] - 1) / 2.0)
                hs.append(rr[0][1] - rr[0][0])
        if len(cs) < 3:
            out.append({"x": x, "y": None, "note": f"the thick line is not a single separate run here ({len(cs)} usable columns)"})
            continue
        row = float(np.median(cs))
        h = float(np.median(hs))
        e = h / 2.0 + ycal["mis"] + (max(cs) - min(cs)) / 2.0
        y, y_lo, y_hi = _y(ycal, row), _y(ycal, row + e), _y(ycal, row - e)
        out.append({"x": x, "y": y, "lo": min(y_lo, y_hi), "hi": max(y_lo, y_hi), "px": [col, row],
                    "px_lo": row - e, "px_hi": row + e,
                    "note": f"thick line {h:.0f} px tall; misfit x {xcal['mis']:.1f} px, y {ycal['mis']:.1f} px"})
    return out


def read_tips(image, at):
    ink, xcal, ycal = calibrate(image)
    top, bot = ycal["frame"]
    left, right = xcal["frame"]
    r03 = int(round((0.3 - ycal["a"]) / ycal["b"]))
    band = ink.copy()
    band[: int(top) + 4, :] = False          # the top frame line (about 5 px) is not a pulse
    band[:, : int(left) + 6] = False
    band[:, int(right) - 5:] = False
    from scipy import ndimage
    out = []
    band[r03 + 1:, :] = False
    lab, _ = ndimage.label(band, structure=np.ones((3, 3), int))
    # pulses: the flanks crossing the 0.3 level (row r03 - 2), grouped when closer than 80 px
    flank = [((a + b - 1) / 2.0) for a, b in _runs(band[r03 - 2, :])]
    groups = []
    for c in flank:
        if groups and c - groups[-1][-1] <= 80:
            groups[-1].append(c)
        else:
            groups.append([c])
    for g in groups:
        c0, c1 = int(min(g)) - 10, int(max(g)) + 10
        ids = {int(lab[r03 - 2, int(round(c))]) for c in g} - {0}
        sub = np.isin(lab[:, c0:c1 + 1], list(ids))
        rows = np.flatnonzero(sub.any(axis=1))
        t = int(rows.min())
        if _y(ycal, t) < 0.8:
            continue        # a grid dot crossing the 0.3 level, not a pulse
        cs = np.flatnonzero(sub[t]) + c0
        col = float(np.mean(cs))
        x = float(xcal["a"] + xcal["b"] * col)
        if t <= top + 8:
            row = top
            y_hi = _y(ycal, top - 3)
            y_lo = _y(ycal, top + 8 + ycal["mis"])
            out.append({"x": x, "y": _y(ycal, row), "lo": y_lo, "hi": y_hi, "px": [col, row],
                        "px_lo": top + 8, "px_hi": top - 3,
                        "note": "tip reaches the top frame: hidden by it"})
        else:
            # the tip of a thin line: its uppermost ink row; the line's centre is about 1.5 px lower
            row = t + 1.5
            e = 2.0 + ycal["mis"]
            out.append({"x": x, "y": _y(ycal, row), "lo": _y(ycal, row + e), "hi": _y(ycal, row - e),
                        "px": [col, row], "px_lo": row - e, "px_hi": row + e,
                        "note": f"pulse tip; {len(g)} flank runs at the 0.3 level"})
    return out


def load(path):
    import importlib.util
    import os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    spec = importlib.util.spec_from_file_location(os.path.splitext(path)[0], p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
