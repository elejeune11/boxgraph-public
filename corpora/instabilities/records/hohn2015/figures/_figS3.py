"""Shared reading code for Fig. S3 (PDF p. 7): percentage change of surface area before expansion,
one coloured marker per embryo, and a short black horizontal line (the median, caption).

Calibration (y only; the x axis carries no values): the box is the four long neutral dark lines;
the line labelled 0 is the full-width horizontal line inside the box; the top line of the box is
level with the label 20. The tick marks labelled 10, -10, -20 are short neutral runs leaving the
left or right side of the box; each is matched to the label whose position the two first marks
predict (within 3 px), and the fit of all marks gives the misfit.

Markers: connected parts of coloured pixels (the largest minus the smallest channel above 50:
the fills are red, purple and blue, the axes and the median line are neutral). The value is the
middle of the part's rows; the 95% interval is that +-(1 px + calibration misfit).

Median line: the rows inside the box with a neutral dark run between 25% and 80% of the box
width (shorter than the zero line, longer than a marker), outside the markers.
"""
import numpy as np
from scipy import ndimage as ndi


def _longest(v):
    best, run = 0, 0
    for x in v:
        run = run + 1 if x else 0
        best = max(best, run)
    return best


def _groups(idx):
    out, cur = [], []
    for i in list(idx) + [None]:
        if cur and (i is None or i != cur[-1] + 1):
            out.append(cur)
            cur = []
        if i is not None:
            cur.append(i)
    return out


def calibrate(image):
    im = image.astype(int)
    hi, lo = im.max(axis=2), im.min(axis=2)
    neutral = (hi - lo) < 40
    frame = (hi < 140) & neutral
    H, W = frame.shape
    rows = _groups([r for r in range(H) if _longest(frame[r]) >= 0.6 * W])
    cols = _groups([c for c in range(W) if _longest(frame[:, c]) >= 0.6 * H])
    if len(rows) < 3 or len(cols) < 2:
        raise ValueError(f"box or zero line not found: rows {rows}, cols {cols}")
    c0, c1 = cols[0][-1] + 1, cols[-1][0]
    # positions in continuous coordinates: pixel row r covers [r, r + 1)
    top = float(np.mean(rows[0])) + 0.5
    bottom = rows[-1]
    inner = [g for g in rows[1:-1]]
    zero = float(np.mean(inner[0])) + 0.5 if len(inner) == 1 else None
    if zero is None:
        raise ValueError(f"expected one full-width line inside the box, found {inner}")
    r0, r1 = rows[0][-1] + 1, bottom[0]
    step = (zero - top) / 20.0  # rows per percent, from the two first marks (20 and 0)
    marks = [(top, 20.0), (zero, 0.0)]
    tick = (hi < 235) & neutral
    for v in (10.0, -10.0, -20.0):
        pred = zero - v * step
        best = None
        for side in ("left", "right"):
            for r in range(int(pred) - 4, int(pred) + 4):
                if not (r0 <= r < r1):
                    continue
                seg = tick[r, c0:c0 + 3] if side == "left" else tick[r, c1 - 3:c1]
                if seg.any():
                    best = r if best is None or abs(r - pred) < abs(best - pred) else best
        if best is not None:
            # centre of the run of tick rows around the best row
            rr = [r for r in range(best - 2, best + 3)
                  if (tick[r, c0:c0 + 3].any() or tick[r, c1 - 3:c1].any())]
            marks.append((float(np.mean(rr)) + 0.5, v))
    p = np.array([m[0] for m in marks])
    v = np.array([m[1] for m in marks])
    b, a = np.polyfit(p, v, 1)
    misfit = float(np.max(np.abs(p - (v - a) / b))) if len(marks) > 2 else 1.0
    return dict(a=a, b=b, misfit=max(misfit, 0.5), box=(c0, r0, c1, r1), zero=zero, marks=marks,
                hi=hi, lo=lo, neutral=neutral)


def markers(image):
    cal = calibrate(image)
    c0, r0, c1, r1 = cal["box"]
    colour = (cal["hi"] - cal["lo"]) > 50
    colour[:, :c0 + 1] = False
    colour[:, c1 - 1:] = False
    colour[:r0 + 1] = False
    colour[r1 - 1:] = False
    lab, n = ndi.label(colour)
    out = []
    for i in range(1, n + 1):
        rr, cc = np.nonzero(lab == i)
        if len(rr) < 6:
            continue
        mid = (rr.min() + rr.max() + 1) / 2
        out.append((float(mid), float((cc.min() + cc.max() + 1) / 2), int(rr.min()), int(rr.max() + 1)))
    return cal, out


def value(cal, row):
    return float(cal["a"] + cal["b"] * row)
