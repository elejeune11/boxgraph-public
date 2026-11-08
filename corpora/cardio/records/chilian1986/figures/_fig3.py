"""Shared reading code for Fig. 3 (PDF p. 6): the diameters of 11 epicardial microvessels
(open circles: arteries; filled circles: veins) in three conditions, joined by a line per vessel:
covered (x = 1), exposed to atmosphere (x = 2), covered with oil (x = 3).

The figure is a scan, nearly black and white: ink is darker than 128.

Calibration, from the image:
- the frame's left side is the leftmost column of ink whose count is at least 80% of the
  maximum; the bottom of the frame is the lowest row of ink that long;
- y ticks point left, outside the frame: rows where a band 10-30 px left of the frame's
  left side is all ink. They are matched, from the bottom up, to the printed labels 30, 60, 90,
  120, 150 (0 and 180 are at the frame's corners and have no tick). A straight line is fitted;
  its largest misfit (px) widens every interval;
- x ticks point up from the frame's bottom: columns where the rows 15-80 px above it are all
  ink, left to right Covered (1), Exposed to atmosphere (2), Oil (3).

Markers, within 70 px of each x tick's column and inside the frame:
- filled markers (veins): groups of ink pixels farther than 0.6 of the largest distance to white
  from any white pixel (the disk's core), one group per disk; centre = the group's centroid;
- open markers (arteries): the white holes enclosed by ink with an area > 150 px that are
  round (bounding box about square and filling >= 55% of its circle); centre = the middle
  of the hole along the column of its centroid.
A marker's value is its centre row, with an interval of 3 px + misfit.

Which marker belongs to which vessel: veins and arteries are told apart by the marker; within a
kind, a vessel is chosen by its rank from the top (1, 2, ...) or the bottom (-1, -2, ...) in each
condition, as the caller says (`ranks`: one entry per x, None where the vessel's marker cannot
be told apart, with the reason).
"""

import numpy as np
from scipy import ndimage as ndi

INK = 128


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def calibrate(image):
    g = image[..., :3].astype(float).mean(axis=2)
    ink = g < INK
    H, W = ink.shape
    cs = ink.sum(axis=0)
    long_cols = np.flatnonzero(cs >= 0.8 * cs.max())
    fr0, fr1 = _runs(np.isin(np.arange(W), long_cols))[-1]  # the frame's right side (straight)
    # the left side is not straight in the scan (it drifts by ~25 px over the frame's height), so
    # it is found row by row: the right end of the first ink run reaching past 10% of the width
    rs = ink[:, : fr0].sum(axis=1)
    long_rows = np.flatnonzero(rs >= 0.6 * fr0)
    rg = _runs(np.isin(np.arange(H), long_rows))
    (ft0, ft1), (fb0, fb1) = rg[0], rg[-1]
    left_end = np.full(H, -1)
    tick_len = np.zeros(H)
    for r in range(ft1, fb0):
        for s, e in _runs(ink[r, : W // 8]):
            if e > W // 10:
                left_end[r], tick_len[r] = e, e - s
                break
    fl1 = int(np.max(left_end[ft1:fb0]))
    # y ticks: rows where the run ending at the frame's left side is at least 70 px long
    band = tick_len >= 70
    yt = sorted(((a + b - 1) / 2.0 for a, b in _runs(band) if b - a < 40), reverse=True)
    if len(yt) != 5:
        raise RuntimeError(f"expected 5 y ticks, found {yt}")
    p, v = np.array(yt), np.array([30, 60, 90, 120, 150], float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - (a + b * p)) / b)))
    xb = ink[fb0 - 80: fb0 - 15, :].all(axis=0)
    xb[: fl1 + 10] = False
    xb[fr0 - 10:] = False
    xt = [(s + e - 1) / 2.0 for s, e in _runs(xb) if e - s < 40]
    if len(xt) != 3:
        raise RuntimeError(f"expected 3 x ticks, found {xt}")
    return dict(ink=ink, a=a, b=b, mis=mis, yt=yt, xt=xt, top=ft1, bottom=fb0, left=fl1, right=fr0)


def _val(cal, row):
    return cal["a"] + cal["b"] * row


def markers(cal, k):
    """The filled and open markers in the column of x tick k (0, 1, 2), each sorted from the top."""
    ink = cal["ink"]
    c = int(round(cal["xt"][k]))
    c0, c1 = c - 70, c + 71
    r0, r1 = cal["top"] + 3, cal["bottom"] - 3
    sub = ink[r0:r1, c0:c1]
    edt = ndi.distance_transform_edt(sub)
    rmax = float(edt.max())
    core, n = ndi.label(edt > 0.6 * rmax)
    filled = []
    for i in range(1, n + 1):
        rr, cc = np.nonzero(core == i)
        filled.append((float(rr.mean() + r0), float(cc.mean() + c0)))
    holes = ndi.binary_fill_holes(sub) & ~sub
    hl, nh = ndi.label(holes)
    opened = []
    for i in range(1, nh + 1):
        rr, cc = np.nonzero(hl == i)
        h, w = rr.max() - rr.min() + 1, cc.max() - cc.min() + 1
        if rr.size < 150 or abs(h - w) > 0.3 * max(h, w) or rr.size < 0.55 * np.pi * h * w / 4:
            continue
        cm = int(round(cc.mean()))
        col_rows = rr[cc == cm]
        opened.append(((col_rows.min() + col_rows.max()) / 2.0 + r0, float(cm + c0)))
    return {"filled": sorted(filled), "open": sorted(opened)}


def read_vessel(image, at, kind, ranks, why=None):
    """ranks: {x: rank or None}; why: {x: reason the marker cannot be read}."""
    cal = calibrate(image)
    out = []
    for x in at:
        k = int(round(x)) - 1
        rank = ranks.get(int(round(x)))
        if rank is None:
            out.append({"x": x, "y": None, "note": (why or {}).get(int(round(x)), "not read")})
            continue
        ms = markers(cal, k)[kind]
        idx = rank - 1 if rank > 0 else rank
        if not -len(ms) <= idx < len(ms):
            out.append({"x": x, "y": None, "note": f"only {len(ms)} {kind} markers found at x = {x:g}"})
            continue
        row, col = ms[idx]
        tol = 3 + cal["mis"]
        y = _val(cal, row)
        lo, hi = sorted((_val(cal, row + tol), _val(cal, row - tol)))
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [col, row],
                    "note": (f"{kind} marker {rank} of {len(ms)} from the {'top' if rank > 0 else 'bottom'}; "
                             f"{kind} markers here at {', '.join(f'{_val(cal, r):.0f}' for r, _ in ms)} um; "
                             f"y ticks misfit {cal['mis']:.2f} px")})
    return out
