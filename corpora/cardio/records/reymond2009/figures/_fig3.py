"""Shared reading code for Fig. 3 (PDF p. 7): PWV against mean lumen diameter, an Excel chart
drawn as vector graphics, rendered at 1200 dpi.

Calibration, all from the image (ink: gray < 128):
- the x axis is the row band where more than half of the crop's columns are ink; the y axis is
  the leftmost column band where more than 30% of the rows are ink;
- x ticks: short vertical runs (< 20 px wide) in the row 12 px below the x axis band that are
  gone 40 px below it (an error bar's stem continues further); they carry the printed labels
  0, 5, ..., 30 left to right; exactly 7 are required;
- y ticks: short horizontal runs (< 20 px tall) in the column 12 px left of the y axis band that
  are gone 30 px left of it (the axis-break marks '//' reach further), above the x axis; they
  carry 5, 7, ..., 15 bottom to top; exactly 6 are required;
- a straight line is fitted to each axis' marks; the largest misfit (px, at least 0.5) widens
  every interval; more than 3 px raises an error.
The y axis has a break drawn below the 5 tick. The x axis row lies where the fitted y scale
gives 3.0, so the scale below 5 is read as continuous (an Excel axis starting at 3 with the
break drawn over it); values below 5 say so in their note.

Markers (filled diamonds): the ink is opened with a diamond structuring element of radius 12 px,
which removes lines (curve about 13 px, stems and text about 9 px) and keeps the diamonds
(about 50 px across); each remaining component of at least 400 px is one marker, read at its
centroid +- (1 px + misfit).

Error bars: from the marker's top and bottom, the stem (ink within +-3 px of the marker's
centre column) is followed outwards, bridging gaps of 2 px. It ends either where the ink stops
(an end, valid if a cap is there: a horizontal run 20-45 px wide centred within 5 px of the
stem, within 6 px of the end) or where it enters another marker. The bar end is the outer edge
less half the cap's thickness, +- (1 px + misfit). A bar with one capped end and the other end
entering another marker is taken as symmetric (the mirror of the capped end), if the mirrored
end lies inside that marker; the note says so. Otherwise (stems shared by several markers, as
at d about 29 mm) the bar is not read and the note lists what was found. A stem shorter than
15 px beyond the marker is no bar.

The curve: ink with the markers (dilated by 6 px) and the error-bar stems and caps removed,
restricted to the plot interior, is traced with boxgraph.digitize.trace from a seed found in the
column of x = 25 (the one run there 8-30 px tall). At each requested x the traced centre is the
value, +- (1 px + y misfit + |slope| x misfit); a merged (ambiguous) column takes the merged
run's half-height instead.
"""

import numpy as np
from scipy import ndimage

from boxgraph import digitize as D


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _fit(marks):
    p = np.array([m[0] for m in marks], float)
    v = np.array([m[1] for m in marks], float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - (a + b * p)) / b)))
    if mis > 3.0:
        raise RuntimeError(f"calibration misfit {mis:.1f} px: {marks}")
    return a, b, max(mis, 0.5)


def calibrate(image):
    g = image[..., :3].astype(float).mean(axis=2)
    ink = g < 128
    H, W = ink.shape
    rb = _runs(ink.mean(axis=1) > 0.5)
    if len(rb) != 1:
        raise RuntimeError(f"x axis bands {rb}")
    xr0, xr1 = rb[0]
    cb = _runs(ink.mean(axis=0) > 0.3)
    yc0, yc1 = cb[0]
    xt = [(a + b - 1) / 2 for a, b in _runs(ink[xr1 + 12]) if b - a < 20 and not ink[xr1 + 40, a:b].any()]
    yt = [(a + b - 1) / 2 for a, b in _runs(ink[:xr0, yc0 - 12]) if b - a < 20 and not ink[a:b, yc0 - 30].any()]
    X = [0, 5, 10, 15, 20, 25, 30]
    Y = [5, 7, 9, 11, 13, 15]
    if len(xt) != len(X) or len(yt) != len(Y):
        raise RuntimeError(f"ticks x {xt}, y {yt}")
    xa, xb, xmis = _fit(list(zip(xt, X)))
    ya, yb, ymis = _fit(list(zip(yt[::-1], Y)))
    return dict(ink=ink, xa=xa, xb=xb, xmis=xmis, ya=ya, yb=yb, ymis=ymis,
                box=(yc1 + 2, 0, W, xr0 - 2), axis_row=(xr0 + xr1 - 1) / 2)


def _diamond(r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return (np.abs(x) + np.abs(y)) <= r


def markers(cal):
    ink = cal["ink"].copy()
    c0, r0, c1, r1 = cal["box"]
    ink[:, :c0] = False
    ink[r1:, :] = False
    op = ndimage.binary_opening(ink, structure=_diamond(12))
    lab, n = ndimage.label(op)
    out = []
    for i in range(1, n + 1):
        rr, cc = np.nonzero(lab == i)
        if len(rr) < 400:
            continue
        out.append(dict(row=float(rr.mean()), col=float(cc.mean()), top=int(rr.min()), bot=int(rr.max()),
                        left=int(cc.min()), right=int(cc.max()), label=i))
    return sorted(out, key=lambda m: (m["col"], m["row"])), lab


def _walk(ink, lab, me, col, start, step):
    """Follow the stem from row `start` in direction `step`. Returns (kind, end_row, cap)."""
    c = int(round(col))
    H = ink.shape[0]
    r, last, gap = start, None, 0
    while 0 <= r < H:
        band = ink[r, c - 3: c + 4]
        hit = lab[r, c - 3: c + 4]
        other = [int(h) for h in hit if h and h != me]
        if other:
            return ("marker", r, other[0])
        if band.any():
            last, gap = r, 0
        else:
            gap += 1
            if gap > 2:
                break
        r += step
    if last is None:
        return ("none", None, None)
    return ("end", last, None)


def _cap(ink, col, end, step):
    """A cap near the stem's end: rows within 6 px inward of `end` whose run through the stem is
    20-45 px wide and centred on it. Returns (outer_edge_row, thickness) or None."""
    c = int(round(col))
    rows = []
    for r in range(end, end - 7 * step, -step):
        for a, b in _runs(ink[r]):
            if a <= c < b and 20 <= b - a <= 45 and abs((a + b - 1) / 2 - col) <= 5:
                rows.append(r)
    if not rows:
        return None
    return end, len(rows)


def read_markers(image):
    cal = calibrate(image)
    ink = cal["ink"]
    ms, lab = markers(cal)
    byl = {m["label"]: m for m in ms}
    out = []
    for m in ms:
        x = cal["xa"] + cal["xb"] * m["col"]
        y = cal["ya"] + cal["yb"] * m["row"]
        ey = 1.0 + cal["ymis"]
        rec = {"x": x, "y": y, "lo": cal["ya"] + cal["yb"] * (m["row"] + ey),
               "hi": cal["ya"] + cal["yb"] * (m["row"] - ey), "px": [m["col"], m["row"]]}
        notes = [f"diamond centroid; misfit x {cal['xmis']:.1f}, y {cal['ymis']:.1f} px"]
        if y < 5:
            notes.append("below the 5 tick, past the axis break: read on the continued scale")
        ends = {}
        for name, start, step in (("up", m["top"] - 1, -1), ("down", m["bot"] + 1, 1)):
            kind, end, other = _walk(ink, lab, m["label"], m["col"], start, step)
            cap = _cap(ink, m["col"], end, step) if kind == "end" and abs(end - start) >= 3 else None
            if cap is not None:
                edge, th = cap
                ends[name] = ("cap", edge - step * th / 2.0)
            elif kind == "end" and abs(end - start) >= 15:
                ends[name] = ("nocap", end)
            elif kind == "marker":
                ends[name] = ("marker", other)
            else:
                ends[name] = ("none", None)
        kinds = (ends["up"][0], ends["down"][0])
        e = 1.0 + cal["ymis"]
        rows = None
        if kinds == ("cap", "cap"):
            rows = (ends["up"][1], ends["down"][1])
            notes.append("error bar: both ends capped")
        elif "cap" in kinds and "marker" in kinds:
            capped = "up" if kinds[0] == "cap" else "down"
            hidden = "down" if capped == "up" else "up"
            mr = 2 * m["row"] - ends[capped][1]
            om = byl.get(ends[hidden][1])
            if om is not None and om["top"] <= mr <= om["bot"]:
                rows = (ends["up"][1], mr) if capped == "up" else (mr, ends["down"][1])
                notes.append(f"error bar: the {hidden} end runs into another marker; taken as the mirror of the capped {capped} end")
            else:
                notes.append(f"error bar not read: the {hidden} stem runs into another marker and the mirror of the {capped} end is not inside it")
        elif kinds != ("none", "none"):
            notes.append(f"error bar not read: stem ends {kinds} (stems shared by several markers)")
        if rows is not None:
            up, dn = rows
            rec["bar_hi"] = cal["ya"] + cal["yb"] * up
            rec["bar_lo"] = cal["ya"] + cal["yb"] * dn
            rec["bar_hi_outer"] = cal["ya"] + cal["yb"] * (up - e)
            rec["bar_lo_outer"] = cal["ya"] + cal["yb"] * (dn + e)
            rec["px_lo"], rec["px_hi"] = up, dn
        rec["note"] = "; ".join(notes)
        out.append(rec)
    return out


def read_curve(image, at):
    cal = calibrate(image)
    ink = cal["ink"].copy()
    c0, r0, c1, r1 = cal["box"]
    ms, lab = markers(cal)
    near = ndimage.binary_dilation(lab > 0, iterations=6)
    ink &= ~near
    ink[:, :c0 + 4] = False
    ink[r1 - 4:, :] = False
    # remove error bar stems and caps: thin vertical runs taller than 40 px through marker columns
    for m in ms:
        c = int(round(m["col"]))
        for cc in range(c - 22, c + 23):
            for a, b in _runs(ink[:, cc]):
                if b - a > 40 and abs(cc - c) <= 6:
                    ink[a:b, cc] = False
    # the curve: connected pieces longer than 200 px (text glyphs, about 100 px, and remnants are smaller)
    lab2, n2 = ndimage.label(ink, structure=np.ones((3, 3)))
    sl_ = ndimage.find_objects(lab2)
    keep = np.zeros(n2 + 1, bool)
    for i, s in enumerate(sl_, start=1):
        if s is not None and max(s[0].stop - s[0].start, s[1].stop - s[1].start) > 200:
            keep[i] = True
    curve = keep[lab2]

    def centre(c):
        rr = _runs(curve[:, c]) if 0 <= c < curve.shape[1] else []
        return rr

    # the line's thickness: median run height in columns where the curve is nearly flat
    hs = []
    for c in range(0, curve.shape[1], 5):
        r0_ = centre(c)
        r1_ = centre(c + 10)
        if len(r0_) == 1 and len(r1_) == 1 and abs((r0_[0][0] + r0_[0][1]) - (r1_[0][0] + r1_[0][1])) / 20.0 < 0.1:
            hs.append(r0_[0][1] - r0_[0][0])
    t = float(np.median(hs))
    out = []
    for x in at:
        col = (x - cal["xa"]) / cal["xb"]
        c = int(round(col))
        rr = centre(c)
        if len(rr) != 1:
            out.append({"x": x, "y": None, "note": f"{len(rr)} curve runs in this column"})
            continue
        a, b = rr[0]
        row = (a + b - 1) / 2.0
        nb = [centre(k) for k in (c - 8, c + 8)]
        sl = abs(sum(nb[1][0]) - sum(nb[0][0])) / 32.0 if all(len(n) == 1 for n in nb) else None
        if sl is None:
            out.append({"x": x, "y": None, "note": "the curve is broken next to this column"})
            continue
        expected = t * np.sqrt(1 + sl * sl)
        extra = max((b - a) - expected, 0.0) / 2.0
        e = 1.0 + extra + cal["ymis"] + sl * cal["xmis"]
        y = cal["ya"] + cal["yb"] * row
        lo = cal["ya"] + cal["yb"] * (row + e)
        hi = cal["ya"] + cal["yb"] * (row - e)
        out.append({"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [col, row],
                    "px_lo": row - e, "px_hi": row + e,
                    "note": f"run {b - a} px (line {t:.0f} px, expected {expected:.0f}); slope {sl:.2f}; "
                            f"misfit x {cal['xmis']:.1f}, y {cal['ymis']:.1f} px"})
    return out
