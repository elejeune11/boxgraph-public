"""Shared reading code for Fig. 7 (PDF p. 8): mean microvascular pressure as % of mean aortic
pressure, control (filled circles) and papaverine (open circles), each point with an error bar.
The x axis is microvessel diameter, broken in two: arterial (350, 250, 150 um, decreasing to the
right) and venous (150, 250, 350 um, increasing to the right).

The figure is a clean black-and-white print: ink is darker than 128.

Calibration, from the image:
- the y axis is the leftmost column of ink whose count is at least 90% of the maximum; the x axis
  is the longest row of ink right of it;
- y ticks point right, into the plot: rows where a band 15-60 px right of the y axis is all
  ink. Their centres, from the x axis (the 0 tick) upwards, are matched to 0, 25, 50, 75, 100.
  A straight line is fitted; its largest misfit (px) widens every interval;
- x ticks point up: columns right of the y axis where the rows 12-45 px above the x axis are all
  ink. In order they are arterial 250, 150, then venous 150, 250, 350; the y axis is arterial 350.
  The axis break lies midway between the two 150 ticks. The diameters are used only to say which
  point is which and are given in each reading's note.

Markers: the ink with its enclosed holes filled, opened with a disk of radius 14 px (wider than
every line, cap and asterisk stroke), leaves the markers. Right of the break and above the 50
tick lie only the legend's markers, which are left out.
- filled markers: groups of ink pixels farther than 0.6 of the largest distance to white (the
  disk's radius) from any white pixel: one group per filled disk, its centre the group's
  centroid;
- open markers: the white holes enclosed by ink (area > 300 px); the centre is the middle of
  the hole along the column of the hole's centroid.
A marker's value is its centre row, with an interval of 3 px + misfit.

Which point is which, from the image: left of the break, the left point of a series is the
larger arterioles (index 1), the right one the medium arterioles (2); right of the break, the
left point is the small venules (3), the right one the medium venules (4).

Error bars: from the marker's edge, the vertical stem (the column of ink nearest the centre,
within 20 px) is followed outward, bridging gaps of up to 2 px, until the ink run across the
row is wider than 3 line widths: that is the cap; the end is the cap's middle row, read with
half the cap's thickness + 2 px + misfit. An end with no stem is not drawn (hidden in the
marker, or above the plot): it is taken as the mirror of the other end, and the note says so.
"""

import numpy as np
from scipy import ndimage as ndi

INK = 128


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _disk(r):
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    return xx * xx + yy * yy <= r * r


def calibrate(image):
    g = image[..., :3].astype(float).mean(axis=2)
    ink = g < INK
    H, W = ink.shape
    cs = ink.sum(axis=0)
    long_cols = np.flatnonzero(cs >= 0.9 * cs.max())
    ya0, ya1 = _runs(np.isin(np.arange(W), long_cols))[0]
    rs = ink[:, ya1:].sum(axis=1)
    long_rows = np.flatnonzero(rs >= 0.9 * rs.max())
    xa0, xa1 = _runs(np.isin(np.arange(H), long_rows))[-1]
    band = ink[: xa1 + 2, ya1 + 15: ya1 + 60].all(axis=1)
    yt = sorted(((a + b - 1) / 2.0 for a, b in _runs(band) if b - a < 40), reverse=True)
    if len(yt) != 5:
        raise RuntimeError(f"expected 5 y ticks, found {yt}")
    p, v = np.array(yt), np.array([0, 25, 50, 75, 100], float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - (a + b * p)) / b)))
    xb = ink[xa0 - 45: xa0 - 12, :].all(axis=0)
    xb[: ya1 + 30] = False  # the y axis line, a little thicker near the bottom
    xt = [(s + e - 1) / 2.0 for s, e in _runs(xb) if e - s < 40]
    if len(xt) != 5:
        raise RuntimeError(f"expected 5 x ticks, found {xt}")
    yc = (ya0 + ya1 - 1) / 2.0
    art = np.polyfit([yc, xt[0], xt[1]], [350, 250, 150], 1)
    ven = np.polyfit(xt[2:], [150, 250, 350], 1)
    brk = (xt[1] + xt[2]) / 2.0
    # line width: the commonest vertical run length of ink in the y axis band of tick rows
    lw = float(np.median([e - s for s, e in _runs(ink[:, ya1 + 30]) if e - s < 60]))
    return dict(ink=ink, a=a, b=b, mis=mis, xa0=xa0, ya1=ya1, art=art, ven=ven, brk=brk, lw=lw, yt=yt, xt=xt)


def _val(cal, row):
    return cal["a"] + cal["b"] * row


def _diam(cal, col):
    c = cal["art"] if col < cal["brk"] else cal["ven"]
    return float(np.polyval(c, col))


def markers(cal):
    ink = cal["ink"]
    H, W = ink.shape
    region = np.zeros_like(ink)
    region[: cal["xa0"] - 5, cal["ya1"] + 5:] = True
    legend_row = min(cal["yt"], key=lambda t: abs(_val(cal, t) - 50))
    region[: int(legend_row), int(cal["brk"]):] = False
    filled = ndi.binary_fill_holes(ink)
    blobs = ndi.binary_opening(filled, structure=_disk(14)) & region
    lab, n = ndi.label(blobs)
    out = []
    edt = ndi.distance_transform_edt(ink)
    rmax = float(edt[blobs].max())
    core, nc = ndi.label((edt > 0.6 * rmax) & blobs)
    for i in range(1, nc + 1):
        rr, cc = np.nonzero(core == i)
        out.append(dict(kind="filled", col=float(cc.mean()), row=float(rr.mean()), r=rmax))
    holes = filled & ~ink & blobs
    hl, nh = ndi.label(holes)
    for i in range(1, nh + 1):
        rr, cc = np.nonzero(hl == i)
        h, w = rr.max() - rr.min() + 1, cc.max() - cc.min() + 1
        # a marker's hole is round: about as wide as high and filling most of its bounding circle
        # (this leaves out the white gaps enclosed between two neighbouring error bars and markers)
        if rr.size < 300 or abs(h - w) > 0.3 * max(h, w) or rr.size < 0.6 * np.pi * h * w / 4:
            continue
        c = int(round(cc.mean()))
        col_rows = rr[cc == c]
        out.append(dict(kind="open", col=float(c), row=(col_rows.min() + col_rows.max()) / 2.0,
                        r=(cc.max() - cc.min()) / 2.0 + cal["lw"]))
    return out


def _end(cal, col, row, r, step):
    """Follow the error bar from the marker's edge; return (cap middle row, cap half-thickness) or None."""
    ink = cal["ink"]
    H = ink.shape[0]
    start = int(round(row + step * (r + 4)))
    cols = [c for c in range(int(col) - 20, int(col) + 21) if ink[start, c]]
    if not cols:
        return None
    sc = int(round(np.median(cols)))
    rr, gap, cap = start, 0, []
    while 0 < rr < H - 1 and gap <= 2:
        rr += step
        if not ink[rr, sc]:
            if cap:
                break
            gap += 1
            continue
        gap = 0
        run = [(s, e) for s, e in _runs(ink[rr, sc - 120: sc + 121]) if s <= 120 < e]
        if run and run[0][1] - run[0][0] > 3 * cal["lw"]:
            cap.append(rr)
        elif cap:
            break
    if not cap:
        return None
    return (min(cap) + max(cap)) / 2.0, (max(cap) - min(cap) + 1) / 2.0


def read_series(image, at, kind):
    cal = calibrate(image)
    ms = [m for m in markers(cal) if m["kind"] == kind]
    left = sorted((m for m in ms if m["col"] < cal["brk"]), key=lambda m: m["col"])
    right = sorted((m for m in ms if m["col"] > cal["brk"]), key=lambda m: m["col"])
    ordered = left + right
    out = []
    for x in at:
        k = int(round(x)) - 1
        if len(left) != 2 or len(right) != 2:
            out.append({"x": x, "y": None, "note": f"expected 2 + 2 {kind} markers, found {len(left)} + {len(right)}"})
            continue
        m = ordered[k]
        y = _val(cal, m["row"])
        tol = 3 + cal["mis"]
        lo, hi = sorted((_val(cal, m["row"] + tol), _val(cal, m["row"] - tol)))
        res = {"x": x, "y": y, "lo": lo, "hi": hi, "px": [m["col"], m["row"]]}
        up, dn = _end(cal, m["col"], m["row"], m["r"], -1), _end(cal, m["col"], m["row"], m["r"], +1)
        note = (f"{kind} marker at diameter {_diam(cal, m['col']):.0f} um; y ticks misfit {cal['mis']:.2f} px")
        if up is None and dn is None:
            res["note"] = note + "; no error bar found outside the marker"
            out.append(res)
            continue
        ends, outer = [], []
        for e, sgn in ((up, -1), (dn, +1)):
            if e is not None:
                v = _val(cal, e[0])
                ends.append(v)
                outer.append(_val(cal, e[0] + sgn * (e[1] + 2 + cal["mis"])))
        if up is None or dn is None:
            which = "upper" if up is None else "lower"
            note += f"; the {which} end of the error bar is not drawn and is taken as the mirror of the other"
            ends.append(2 * y - ends[0])
            outer.append(2 * y - outer[0])
            rows = [m["row"] - (m["row"] - (up or dn)[0]) * s for s in (1, -1)]
        else:
            rows = [up[0], dn[0]]
        res.update(bar_lo=min(ends), bar_hi=max(ends), bar_lo_outer=min(outer + ends), bar_hi_outer=max(outer + ends),
                   px_lo=min(rows), px_hi=max(rows), note=note)
        out.append(res)
    return out
