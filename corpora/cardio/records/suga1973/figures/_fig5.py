"""Shared reading code for Fig. 5 (p. 6): normalized pressure-volume ratio e_N against normalized
time t_N. Four symbol series (control, epinephrine, five loads, three heart rates) are plotted at
each nominal t_N = 0, 0.1, ..., 1.5, staggered left to right around it, each with a vertical SD bar.

Everything is found in the image: the axis lines, the tick marks (matched to the printed labels
0, 0.5, 1.0 on y and 0, 0.5, 1.0, 1.5 on x), the legend (two fraction bars, masked out), the
error-bar stems, the marker on each stem and the bar's ends. The scan under the PDF is bilevel at
about 300 dpi, so one scan pixel is about 4 px of the 1200 dpi render; intervals include that.
"""

import numpy as np
from scipy import ndimage

STEM_MAX = 20        # px: a stem's cross-section is 12-16 px; anything wider is a marker or a cap
WIN = 10             # px: half-window around a stem in which the marker is looked for
SCAN_PX = 4.0        # px of the render per pixel of the underlying scan


def _ink(image):
    g = image[..., :3].astype(float).mean(axis=2)
    paper, darkest = np.percentile(g, 99), g.min()
    return g < (paper + darkest) / 2


def _runs(v):
    """(start, stop) of each run of True in a 1-D boolean array."""
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _fit(marks):
    """Least-squares line value = a + b * pixel through (pixel, value) marks, and its worst misfit in px."""
    p = np.array([m[0] for m in marks], float)
    v = np.array([m[1] for m in marks], float)
    b, a = np.polyfit(p, v, 1)
    misfit_px = float(np.max(np.abs((v - a) / b - p)))
    return a, b, misfit_px


def _regular(cands, n, labels):
    """The n candidates, in order, whose spacing is most even (labelled ticks are evenly spaced)."""
    import itertools

    best = None
    for sub in itertools.combinations(sorted(cands), n):
        d = np.diff(sub)
        score = float(np.ptp(d)) / float(np.mean(d))
        if best is None or score < best[0]:
            best = (score, sub)
    return list(zip(best[1], labels))


def calibrate(ink):
    colsum = ink.sum(axis=0)
    ycol = int(np.argmax(colsum))
    ycols = np.flatnonzero(colsum > 0.9 * colsum[ycol])
    yax_l, yax_r = int(ycols.min()), int(ycols.max()) + 1
    rowsum = ink.sum(axis=1)
    xrow = int(np.argmax(rowsum))
    xrows = np.flatnonzero(rowsum > 0.9 * rowsum[xrow])
    xax_t, xax_b = int(xrows.min()), int(xrows.max()) + 1
    yrun = max(_runs(ink[:, ycol]), key=lambda r: r[1] - r[0])
    # y ticks: short horizontal marks just right of the y axis, along the axis' length
    probe = ink[:, yax_r + 2: yax_r + 26].all(axis=1)
    yt = [(a + b) / 2.0 for a, b in _runs(probe) if yrun[0] - 5 <= a <= yrun[1] and b - a < 40]
    # x ticks: short vertical marks standing on the x axis line
    probe = ink[xax_t - 14: xax_t - 2, :].all(axis=0)
    xt = [(a + b) / 2.0 for a, b in _runs(probe) if a > yax_r + 20 and 6 <= b - a < 30]
    ymarks = _regular(yt, 3, [1.0, 0.5, 0.0])        # top to bottom
    xmarks = _regular(xt, 4, [0.0, 0.5, 1.0, 1.5])   # left to right
    return dict(yax=(yax_l, yax_r), xax=(xax_t, xax_b), yrun=yrun, ymarks=ymarks, xmarks=xmarks)


def plot_mask(ink, cal):
    """Ink inside the plot, without the axes, their ticks and the legend (the two equations)."""
    m = ink.copy()
    m[:, : cal["yax"][1] + 30] = False
    m[cal["xax"][0] - 16:, :] = False
    # the legend: its two fraction bars are the only long horizontal strokes inside the plot
    bars = []
    for r in range(m.shape[0]):
        for a, b in _runs(m[r]):
            if b - a > 150:
                bars.append((r, a, b))
    if bars:
        r0 = min(b[0] for b in bars)
        r1 = max(b[0] for b in bars)
        c1 = max(b[2] for b in bars)
        m[max(0, r0 - 140): r1 + 140, : c1 + 20] = False
    return m


def stems(m):
    """Vertical error-bar stems: narrow ink, at least 16 px tall, grouped by column."""
    s = np.zeros_like(m)
    for r in range(m.shape[0]):
        for a, b in _runs(m[r]):
            if b - a <= STEM_MAX:
                s[r, a:b] = True
    s = ndimage.binary_opening(s, structure=np.ones((16, 1), bool))
    lab, n = ndimage.label(s)
    pieces = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        rr, cc = np.nonzero(lab[sl] == i)
        if len(rr) == 0:
            continue
        pieces.append(dict(col=float(cc.mean() + sl[1].start + 0.5), top=sl[0].start, bot=sl[0].stop,
                           width=sl[1].stop - sl[1].start))
    pieces = [p for p in pieces if p["width"] >= 6]
    pieces.sort(key=lambda p: (p["col"], p["top"]))
    groups = []
    for p in pieces:
        for g in groups:
            if abs(g["col"] - p["col"]) <= 7 and (p["top"] - g["bot"] < 70 and g["top"] - p["bot"] < 70):
                g["parts"].append(p)
                g["top"] = min(g["top"], p["top"])
                g["bot"] = max(g["bot"], p["bot"])
                g["col"] = float(np.mean([q["col"] for q in g["parts"]]))
                break
        else:
            groups.append(dict(col=p["col"], top=p["top"], bot=p["bot"], parts=[p]))
    return groups


def bar_point(m, g):
    """The bar's two ends (caps included) and the marker on it."""
    c = int(round(g["col"]))
    band = m[:, c - 3: c + 4].any(axis=1)
    top, bot = g["top"], g["bot"] - 1
    while top > 0 and band[top - 1]:
        top -= 1
    while bot < len(band) - 1 and band[bot + 1]:
        bot += 1
    width = m[top: bot + 1, c - WIN: c + WIN + 1].sum(axis=1)
    wide = width >= 2 * WIN - 1
    runs = [(a + top, b + top) for a, b in _runs(wide)]
    # caps are wide rows at the very ends of the bar; a marker is wide rows inside it
    inner = [(a, b) for a, b in runs if a > top + 6 and b < bot - 6]
    note = ""
    if inner:
        a, b = max(inner, key=lambda r: r[1] - r[0])
        if len(inner) > 1:
            note = "more than one wide band on the stem; the tallest is taken as the marker"
    elif runs:
        a, b = max(runs, key=lambda r: r[1] - r[0])
        note = "the marker touches an end of the bar"
    else:
        # no wide band: the marker is the gap between the two stem pieces, if there is one
        parts = sorted(g["parts"], key=lambda p: p["top"])
        gaps = [(parts[i]["bot"], parts[i + 1]["top"]) for i in range(len(parts) - 1)]
        if not gaps:
            return None
        a, b = max(gaps, key=lambda r: r[1] - r[0])
        note = "marker found as the gap between stem pieces"
    return dict(col=g["col"], row=(a + b) / 2.0, half=(b - a) / 2.0, top=top, bot=bot + 1, note=note)


def blobs_without_stem(m, points):
    """Markers whose SD bar is hidden inside them (no stem): solid blobs away from every stem."""
    dt = ndimage.distance_transform_edt(m)
    core = dt >= 7
    lab, n = ndimage.label(core)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        c0, c1 = sl[1].start, sl[1].stop
        if any(c0 - 12 <= p["col"] <= c1 + 12 and p["top"] - 12 <= sl[0].start <= p["bot"] + 12 for p in points):
            continue
        rr = np.nonzero((lab[sl] == i).any(axis=1))[0] + sl[0].start
        # grow back to the blob's full outline
        full = m[sl[0].start - 8: sl[0].stop + 8, c0 - 8: c1 + 8]
        rows = np.nonzero(full.any(axis=1))[0] + sl[0].start - 8
        cols = np.nonzero(full.any(axis=0))[0] + c0 - 8
        out.append(dict(c0=float(cols.min()), c1=float(cols.max() + 1), r0=float(rows.min()),
                        r1=float(rows.max() + 1), row=float(rr.mean() + 0.5)))
    return out


def cap_rows(m, p):
    """Row of each bar end: the centre of the cap (the wide band at the end) where there is one,
    else the outermost ink row of the stem."""
    c = int(round(p["col"]))
    width = m[p["top"]: p["bot"], c - WIN: c + WIN + 1].sum(axis=1)
    runs = [(a + p["top"], b + p["top"]) for a, b in _runs(width >= 2 * WIN - 1)]
    top_end, bot_end = p["top"] + 0.5, p["bot"] - 0.5
    for a, b in runs:
        if a <= p["top"] + 1 and b - a <= 16:
            top_end = (a + b) / 2.0
        if b >= p["bot"] - 1 and b - a <= 16:
            bot_end = (a + b) / 2.0
    return top_end, bot_end


def read_all(image):
    ink = _ink(image)
    cal = calibrate(ink)
    ya, yb, ymis = _fit(cal["ymarks"])
    xa, xb, xmis = _fit(cal["xmarks"])
    m = plot_mask(ink, cal)
    pts = []
    for g in stems(m):
        p = bar_point(m, g)
        if p is None or p["bot"] - p["top"] < 24:
            continue
        if any(abs(q["col"] - p["col"]) < 6 and abs(q["row"] - p["row"]) < 6 for q in pts):
            continue  # the same stem found twice
        p["top_end"], p["bot_end"] = cap_rows(m, p)
        pts.append(p)
    ticks_px = [c for c, _ in cal["xmarks"]]
    hidden = [h for h in blobs_without_stem(m, pts)
              if not (h["r1"] > cal["xax"][0] - 40 and any(h["c0"] - 2 <= t <= h["c1"] + 2 for t in ticks_px))
              and h["c0"] > cal["yax"][1] + 60]
    return dict(cal=cal, ya=ya, yb=yb, ymis=ymis, xa=xa, xb=xb, xmis=xmis, pts=pts, hidden=hidden, m=m)


GRID = 0.1           # the groups sit on a grid in t_N; found from the tick labels' units
OFFSET = 0.017       # the stagger between neighbouring symbols within a group, in t_N


def read_slot(image, k):
    """Readings for the k-th symbol (0 = leftmost) of every group of four, with its SD bar."""
    r = read_all(image)
    ya, yb, xa, xb = r["ya"], r["yb"], r["xa"], r["xb"]
    err_y = 2 * SCAN_PX + r["ymis"]              # px: marker-centre quantisation + calibration misfit
    groups = {}
    for p in r["pts"]:
        x = xa + xb * p["col"]
        g = int(round(x / GRID))
        slot = int(round((x - g * GRID) / OFFSET + 1.5))
        groups.setdefault(g, {}).setdefault(slot, []).append(p)
    out = []
    for g in sorted(set(groups) | {int(round((xa + xb * (h["c0"] + h["c1"]) / 2) / GRID)) for h in r["hidden"]}):
        nominal = g * GRID
        cand = groups.get(g, {}).get(k, [])
        merged = [h for h in r["hidden"] if int(round((xa + xb * (h["c0"] + h["c1"]) / 2) / GRID)) == g]
        if len(cand) == 1:
            p = cand[0]
            e = err_y + (p["half"] if p["note"] else 0.0)
            y = ya + yb * p["row"]
            hi_end, lo_end = ya + yb * p["top_end"], ya + yb * p["bot_end"]
            e_end = 2 * SCAN_PX + r["ymis"]
            out.append(dict(
                x=xa + xb * p["col"], y=y, lo=ya + yb * (p["row"] + e), hi=ya + yb * (p["row"] - e),
                px=[p["col"], p["row"]], px_lo=p["row"] - e, px_hi=p["row"] + e,
                bar_lo=lo_end, bar_hi=hi_end,
                bar_lo_outer=ya + yb * (p["bot_end"] + e_end), bar_hi_outer=ya + yb * (p["top_end"] - e_end),
                note=(f"group at t_N = {nominal:.1f}; " + p["note"]).strip("; ")))
        elif not cand and len(merged) == 1:
            h = merged[0]
            w = (h["c1"] - h["c0"]) / 4.0
            col = h["c0"] + (k + 0.5) * w
            half = (h["r1"] - h["r0"]) / 2.0
            row = h["row"]
            out.append(dict(
                x=xa + xb * col, y=ya + yb * row, lo=ya + yb * (row + err_y), hi=ya + yb * (row - err_y),
                px=[col, row], px_lo=row - err_y, px_hi=row + err_y,
                bar_lo=ya + yb * (row + half), bar_hi=ya + yb * (row - half),
                bar_lo_outer=ya + yb * (row + half + err_y), bar_hi_outer=ya + yb * (row - half - err_y),
                note=(f"group at t_N = {nominal:.1f}: the four markers merge into one dash with no visible "
                      f"bar; this one is placed at quarter {k + 1} of 4 along the dash, and its SD bar is "
                      "reported as at most the marker")))
        # otherwise this symbol cannot be separated from its neighbours in this group (it merges
        # with them in the scan): it is left out, and figures.md says so
    return out
