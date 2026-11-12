"""Shared reading code for Fig. 2 (PDF p. 5): four scatter plots of per-patient values, men as open
circles, women as filled circles, with a dotted (men) and a dashed (women) regression line and a
text box (Rho, P) in one top corner.

The panels are vector graphics rendered at 1500 dpi: ink is darker than 128.

Calibration, from the image:
- the y axis is the leftmost column whose longest ink run is over 40% of the crop height (a few
  columns: the line's thickness); the x axis the lowest rows whose longest run is over 50% of
  the width. The axis line thickness is also the marker line width `lw`;
- y ticks point left: rows where ink continues more than 3 px left of the y axis. They are all
  the same length; every one is a step of the printed labels' spacing / 2 (the labels stand at
  every other tick, the lowest tick being the axis origin). The tick centres are matched in
  order from the x axis upward to origin, origin + step, ... and a straight line is fitted;
- x ticks point down: columns where ink continues below the x axis. Long ticks carry the labels
  (the first is the y axis itself); short ones (under half the longest) are minor and unused.
  A straight line is fitted through the long ticks and the labels;
- the largest misfit of either fit (px) widens every interval.

Markers. The marker radius: the white holes enclosed by ink inside the plot that are round
(about as wide as high and filling their bounding circle) are the insides of isolated open
circles; their median diameter + 2 lw is the outer diameter 2 R.
- open circles: the fraction of an annulus (radii R - lw + 2 to R - 2, the circle's stroke
  without its edges) that is ink, computed for every pixel by convolution. A centre is a local
  maximum of that fraction over 0.9 within lw px, whose inner disk (radius R - lw - 4) is
  not mostly ink (unexplained ink fraction under 0.7: not a filled marker). The filled markers
  are found first and their disks no longer count, so the ink left inside an open circle is
  the strokes of open circles overlapping it; in a cluster of three (Fig. 2 D near 23 um,
  17.6 um) two crossing strokes cover about half the inner disk, hence 0.7;
- filled circles: ink at least 0.75 R from any paper pixel (the distance transform) is only
  found inside filled disks (every other line is thinner than 2 x 0.75 R); each group of it is
  one disk, its centre the group's centroid. A group longer than 1.4 times its width is two
  touching disks; it is split along its long axis into two halves;
- the text box: candidate centres lying in the bounding box of the text in the panel's top
  corner are left out. The text is found as the ink components inside the plot box whose
  bounding box is not round (letters, digits, '=') in the top third of the plot, grouped; the
  markers' own components are round or larger than 3 R.

A marker's y and x are its centre: within 2 px for the fit plus the calibration misfit; the
interval is that, converted to the axis units. Which group (men or women) is the caller's.
"""

import numpy as np
from scipy import ndimage as ndi
from scipy.signal import fftconvolve

INK = 128
OPEN_MIN = 0.5   # share of a ring not yet explained by other markers
RING_MIN = 0.85  # share of a ring in ink, counting every stroke
FILL_MAX = 0.7   # largest share of an open circle's inside covered by other (unexplained) ink


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v):
    return max([e - s for s, e in _runs(v)] or [0])


def _fit(ticks, labels, name):
    """ticks: (start, end, length) in order from the lowest value. Marks shorter than 0.3 of the
    longest are not ticks (a glyph or line touching the axis); those at least 0.75 of the longest
    are the long ticks. The labels stand at the first and last long tick and at evenly spaced long
    ticks between: n long ticks for m labels gives (n - 1) / (m - 1) ticks per label step."""
    longest = max(n for _, _, n in ticks)
    pos = [(s + e - 1) / 2.0 for s, e, n in ticks if n >= 0.75 * longest]
    k = (len(pos) - 1) / (len(labels) - 1)
    if k != int(k):
        raise RuntimeError(f"{name}: {len(pos)} long ticks do not fit {len(labels)} labels: {pos}")
    v = np.linspace(labels[0], labels[-1], len(pos))
    if not np.allclose(v[::int(k)], labels):
        raise RuntimeError(f"{name}: labels are not evenly spaced over the long ticks")
    b, a = np.polyfit(pos, v, 1)
    mis = float(np.max(np.abs((v - (a + b * np.array(pos))) / b)))
    return pos, v, mis, b, a


def calibrate(image, y_labels, x_labels):
    """y_labels, x_labels: the printed tick labels, lowest first, as numbers."""
    ink = image[..., :3].astype(float).mean(axis=2) < INK
    H, W = ink.shape
    colrun = np.array([_longest(ink[:, c]) for c in range(W)])
    cols = np.flatnonzero(colrun > 0.4 * H)
    ya0 = int(cols[0])
    ya1 = int(cols[cols - ya0 < 30].max()) + 1
    rowrun = np.array([_longest(ink[r]) for r in range(H)])
    rows = np.flatnonzero(rowrun > 0.5 * W)
    xa1 = int(rows.max()) + 1
    xa0 = int(rows[xa1 - rows < 30].min())
    lw = xa1 - xa0
    # y ticks: rows where ink runs left from the axis
    left = np.zeros(H, int)
    for r in range(H):
        n = 0
        while ya0 - 1 - n >= 0 and ink[r, ya0 - 1 - n]:
            n += 1
        left[r] = n
    yr = [(s, e, int(left[s:e].max())) for s, e in _runs((left > 3) & (left < 80)) if e - s < 3 * lw and s <= xa1]
    yt, yv, mis_y, by, ay = _fit(sorted(yr, reverse=True), y_labels, "y")
    # x ticks: columns where ink runs down from the axis
    down = np.zeros(W, int)
    for c in range(W):
        n = 0
        while xa1 + n < H and ink[xa1 + n, c]:
            n += 1
        down[c] = n
    xr = [(s, e, int(down[s:e].max())) for s, e in _runs((down > 3) & (down < 80)) if s >= ya0 - 2]
    xt, xv, mis_x, bx, ax = _fit(xr, x_labels, "x")
    return dict(ink=ink, H=H, W=W, ya1=ya1, xa0=xa0, lw=lw, ay=ay, by=by, ax=ax, bx=bx,
                mis=max(mis_x, mis_y, 0.5), yt=yt, xt=xt, top=int(min(yt)))


def _disk(r):
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    return (xx * xx + yy * yy) <= r * r


def _annulus(r0, r1):
    R = int(np.ceil(r1))
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    d = np.hypot(xx, yy)
    return ((d >= r0) & (d <= r1)).astype(float)


def markers(cal):
    ink, lw = cal["ink"], cal["lw"]
    plot = np.zeros_like(ink)
    plot[cal["top"]:cal["xa0"] - 1, cal["ya1"] + 1:] = True
    filled = ndi.binary_fill_holes(ink)
    holes = filled & ~ink & plot
    hl, nh = ndi.label(holes)
    diam = []
    for sl in ndi.find_objects(hl):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        area = (hl[sl] > 0).sum()
        if h > 2 * lw and abs(h - w) <= 0.1 * max(h, w) and area > 0.7 * np.pi * h * w / 4:
            diam.append((h + w) / 2.0)
    R = (float(np.median(diam)) + 2 * lw) / 2.0
    # text: non-marker components in the top third of the plot box
    lab, n = ndi.label(ink & plot)
    textbox = None
    third = cal["top"] + (cal["xa0"] - cal["top"]) / 3.0
    boxes = []
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        round_ = abs(h - w) <= 0.15 * max(h, w) and abs(max(h, w) - 2 * R) <= 0.15 * 2 * R
        if sl[0].stop < third and not round_ and max(h, w) < 3 * R and h > 4 * lw and w < 1.5 * h:
            boxes.append((sl[0].start, sl[1].start, sl[0].stop, sl[1].stop))
    if boxes:
        b = np.array(boxes)
        textbox = (int(b[:, 0].min()), int(b[:, 1].min()), int(b[:, 2].max()), int(b[:, 3].max()))
    if textbox is not None:
        r0, c0, r1, c1 = textbox
        plot[max(r0 - int(R), 0):r1 + int(R), max(c0 - int(R), 0):c1 + int(R)] = False
    out = []
    # filled circles
    edt = ndi.distance_transform_edt(ink)
    core = (edt > 0.75 * R) & plot
    cl, nc = ndi.label(core)
    for i in range(1, nc + 1):
        rr, cc = np.nonzero(cl == i)
        pts = np.stack([rr, cc], 1).astype(float)
        m = pts.mean(0)
        u, s, vt = np.linalg.svd(pts - m, full_matrices=False)
        sd = s / np.sqrt(len(pts))
        if sd[1] > 0 and sd[0] / sd[1] > 1.4:
            proj = (pts - m) @ vt[0]
            for half in (proj < 0, proj >= 0):
                c = pts[half].mean(0)
                out.append(dict(kind="filled", row=float(c[0]), col=float(c[1]), note="split from a touching pair"))
        else:
            out.append(dict(kind="filled", row=float(m[0]), col=float(m[1])))
    # open circles, greedily: the best-explained ring first; its stroke is then explained and
    # no longer counts for any other ring (a marker drawn over another hides part of it)
    H, W = ink.shape
    yy, xx = np.mgrid[0:H, 0:W]
    explained = np.zeros_like(ink)
    for m in out:
        explained |= (yy - m["row"]) ** 2 + (xx - m["col"]) ** 2 <= (R + 1) ** 2
    ann = _annulus(R - lw + 2, R - 2)
    ann /= ann.sum()
    inner = _disk(int(R - lw - 4)).astype(float)
    # the markers are drawn transparent (each outline stays whole where markers overlap), so a
    # true centre has nearly all of its ring in ink, counting every stroke
    total = fftconvolve(ink.astype(float), ann, mode="same")
    while True:
        free = (ink & ~explained).astype(float)
        fill = fftconvolve(free, inner / inner.sum(), mode="same")
        score = fftconvolve(free, ann, mode="same")
        score[~plot | (fill >= FILL_MAX) | (total < RING_MIN)] = 0
        k = int(np.argmax(score))
        r, c = divmod(k, W)
        if score[r, c] < OPEN_MIN:
            break
        # the centre: the score-weighted centroid of the peak's neighbourhood above 90% of it
        win = score[max(r - 6, 0):r + 7, max(c - 6, 0):c + 7]
        wr, wc = np.nonzero(win >= 0.9 * score[r, c])
        w = win[wr, wc]
        rc = float((wr * w).sum() / w.sum()) + max(r - 6, 0)
        cc = float((wc * w).sum() / w.sum()) + max(c - 6, 0)
        out.append(dict(kind="open", row=rc, col=cc, score=float(score[r, c]),
                        note="" if score[r, c] > 0.9 else f"partly hidden: {score[r, c]:.0%} of its ring visible"))
        d2 = (yy - rc) ** 2 + (xx - cc) ** 2
        explained |= (d2 <= (R + 1) ** 2) & (d2 >= (R - lw - 1) ** 2)
    return out, R, textbox


def read_group(image, y_labels, x_labels, kind):
    cal = calibrate(image, y_labels, x_labels)
    ms, R, _ = markers(cal)
    err = 2.0 + cal["mis"]
    res = []
    for m in sorted((m for m in ms if m["kind"] == kind), key=lambda m: (m["col"], m["row"])):
        x = cal["ax"] + cal["bx"] * m["col"]
        y = cal["ay"] + cal["by"] * m["row"]
        dy = abs(cal["by"]) * err
        dx = abs(cal["bx"]) * err
        note = f"{kind} circle at column {m['col']:.1f}, row {m['row']:.1f}; x read to +/- {dx:.3g}"
        if m.get("note"):
            note += "; " + m["note"]
        res.append({"x": float(x), "y": float(y), "lo": float(y - dy), "hi": float(y + dy),
                    "px": [m["col"], m["row"]], "px_lo": m["row"] - err, "px_hi": m["row"] + err, "note": note})
    return res
