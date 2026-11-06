"""Shared reading code for the MATLAB scatter panels of craig2015 (Figs. 4(c), 4(f), S2(a), S4(a), S1(c)).

Everything is found in the image; only the printed tick labels are given by the caller.

Frame: the panel is boxed by a grey frame. Its sides are the columns and rows with the most
non-white pixels (each spans the whole box).

Ticks: MATLAB draws each tick twice, inside the frame on opposite sides (x ticks at the top and the
bottom, y ticks at the left and the right). A tick is a small dark blob (area < max_tick_area) in a
band just inside one side that has a partner on the opposite side at the same column (x) or row (y)
within 8 px. Their centres, sorted, are matched in order to the printed labels; a linear fit gives
the calibration and the misfit is its largest residual (never under 1 px).

Black dots: dark blobs (grey < 90) larger than min_dot_area inside the frame; the value is the
blob's centroid. The dot nearest each requested x position (within 40% of the tick spacing per
unit) is taken. Interval: +/- (half a raster block (3 px) + misfit) on the y axis.

Error bars: light grey (not white, not dark, not blue) pixels in a 7 px wide column band through the
dot's centre, followed up and down from the dot with gaps of at most `gap` px. The extreme rows are
the bars' caps; the end is the cap's centre (extreme row moved in by half the cap thickness, 3 px).
The outer ends are widened by 3 px + misfit.

Blue exes: blue pixels (B exceeds R and G by > 60). In each requested column window, the tallest
connected blob is the 'x' glyph; its bounding-box centre is the value. MATLAB also draws a short
dashed blue mark just below each 'x' (in Fig. 4(c) and (f)); what it is is not said, so the interval
is widened to reach the centre of that mark too when it is present.
"""
import numpy as np
from scipy import ndimage


def _gray(image):
    return np.asarray(image, dtype=float)[:, :, :3].mean(axis=2)


def frame(image):
    g = _gray(image)
    nw = g < 235
    cs, rs = nw.sum(axis=0), nw.sum(axis=1)
    cols = np.where(cs > 0.8 * cs.max())[0]
    rows = np.where(rs > 0.8 * rs.max())[0]
    return int(cols.min()), int(rows.min()), int(cols.max()), int(rows.max())


def _blobs(mask):
    lab, n = ndimage.label(mask)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        m = lab[sl] == i + 1
        a = int(m.sum())
        rr, cc = np.nonzero(m)
        out.append({"area": a, "r": rr.mean() + sl[0].start, "c": cc.mean() + sl[1].start,
                    "r0": sl[0].start, "r1": sl[0].stop, "c0": sl[1].start, "c1": sl[1].stop})
    return out


def _pairs(a, b, key, tol=8.0):
    out = []
    for p in a:
        q = [x for x in b if abs(x[key] - p[key]) < tol]
        if q:
            out.append(0.5 * (p[key] + q[0][key]))
    # a tick crossed by a curve breaks into pieces: merge positions closer than 8 px
    merged = []
    for v in sorted(out):
        if merged and v - merged[-1][-1] < 8:
            merged[-1].append(v)
        else:
            merged.append([v])
    return [float(np.mean(g)) for g in merged]


def _fit(px, labels):
    if len(px) > len(labels) >= 3:
        # extra candidates (a reference line meeting the frame looks like a tick): keep the subset,
        # in order, that lies best on one linear scale
        from itertools import combinations
        best = None
        for sub in combinations(range(len(px)), len(labels)):
            p = np.asarray(px)[list(sub)]
            A = np.vstack([p, np.ones(len(p))]).T
            k, c = np.linalg.lstsq(A, np.asarray(labels, float), rcond=None)[0]
            res = float((np.abs(A @ [k, c] - labels) / abs(k)).max())
            if best is None or res < best[0]:
                best = (res, p)
        px = best[1]
    if len(px) != len(labels):
        raise ValueError(f"found {len(px)} ticks {np.round(px, 1).tolist()} for {len(labels)} labels")
    A = np.vstack([px, np.ones(len(px))]).T
    k, c = np.linalg.lstsq(A, np.asarray(labels, float), rcond=None)[0]
    res = np.abs(A @ [k, c] - labels) / abs(k)
    return k, c, max(1.0, float(res.max()))


def _frame_lines(image):
    g = _gray(image)
    nw = g < 235
    cs, rs = nw.sum(axis=0), nw.sum(axis=1)
    return np.where(rs > 0.8 * rs.max())[0], np.where(cs > 0.8 * cs.max())[0]


def dark_without_frame(image):
    """Dark pixels with the frame's own lines removed (a black frame would join ticks and bars to it)."""
    a = np.asarray(image, dtype=float)[:, :, :3]
    d = (_gray(image) < 90) & ((a.max(axis=2) - a.min(axis=2)) < 60)  # dark and not coloured (pure blue is dark too)
    rows, cols = _frame_lines(image)
    width = cols.max() - cols.min()
    height = rows.max() - rows.min()
    # only a dark (black) frame line is removed: a grey frame is not in the dark mask, and its rows can
    # coincide with ticks drawn just outside it
    rows = [r for r in rows if d[r, :].sum() > 0.5 * width]
    cols = [c for c in cols if d[:, c].sum() > 0.5 * height]
    d[rows, :] = False
    d[:, cols] = False
    return d


def calibrate(image, xlabels, ylabels, max_tick_area=500, band=45, x_top_only=False, y_inner_only=False, x_inner_only=False,
              inner_margin=12):
    L, T, R, B = frame(image)
    small = [b for b in _blobs(dark_without_frame(image)) if b["area"] < max_tick_area]
    top = [b for b in small if T - 3 <= b["r"] <= T + band and L - 10 <= b["c"] <= R + 10]
    bot = [b for b in small if B - band <= b["r"] <= B - 2 and L - 10 <= b["c"] <= R + 10]
    lef = [b for b in small if L - 3 <= b["c"] <= L + band and T - 15 <= b["r"] <= B + 15]
    rig = [b for b in small if R - band <= b["c"] <= R + 3 and T - 15 <= b["r"] <= B + 15]
    # a blob in a side band (a y tick near a corner) is not an x tick
    side = {id(b) for b in lef + rig}
    top = [b for b in top if id(b) not in side and L < b["c"] < R]
    bot = [b for b in bot if id(b) not in side and L < b["c"] < R]
    if x_top_only:  # one tick may break into pieces: merge blobs closer than 30 px
        xs = []
        for c in sorted(b["c"] for b in top):
            if xs and c - xs[-1][-1] < 30:
                xs[-1].append(c)
            else:
                xs.append([c])
        xs = [float(np.mean(g)) for g in xs]
    else:
        xs = _pairs(top, bot, "c")
    ys = _pairs(lef, rig, "r")
    if y_inner_only:  # ticks on the frame's corners are distorted by it: use the inner ones only
        ys = [y for y in ys if T + inner_margin < y < B - inner_margin]
    if x_inner_only:
        xs = [x for x in xs if L + inner_margin < x < R - inner_margin]
    kx, cx, mx = _fit(np.array(xs), xlabels)
    ky, cy, my = _fit(np.array(ys), ylabels)
    return {"frame": (L, T, R, B), "kx": kx, "cx": cx, "mx": mx, "ky": ky, "cy": cy, "my": my,
            "xticks": xs, "yticks": ys}


def _col(cal, x):
    return (x - cal["cx"]) / cal["kx"]


def _y(cal, row):
    return cal["ky"] * row + cal["cy"]


def _greyish(image):
    a = np.asarray(image, dtype=float)[:, :, :3]
    g = a.mean(axis=2)
    neutral = (a.max(axis=2) - a.min(axis=2)) < 40
    return neutral & (g > 90) & (g < 235)


def read_dots(image, at, xlabels, ylabels, error_bars=True, min_dot_area=400, gap=10, bars="grey", core_r=9):
    """bars="grey": light grey error bars (raster panels), followed from the dot's edge.
    bars="dark": black error bars joined to the dot (vector panels): the dot is found as the core of
    the dark mask (distance to paper > core_r px, thicker than any line), and the bar is the dark line
    followed from the dot's centre."""
    cal = calibrate(image, xlabels, ylabels)
    L, T, R, B = cal["frame"]
    g = _gray(image)
    inside = lambda b: L + 3 < b["c"] < R - 3 and T + 3 < b["r"] < B - 3  # noqa: E731
    if bars == "dark":
        dark = dark_without_frame(image)
        # a thin coloured line crossing a dot splits it in the dark mask: close such gaps first
        core = ndimage.distance_transform_edt(ndimage.binary_closing(dark, iterations=4)) > core_r
        dots = []
        for b in _blobs(core):
            if b["area"] >= 20 and inside(b):
                b = dict(b, r0=b["r0"] - core_r, r1=b["r1"] + core_r)
                dots.append(b)
        grey = dark
    else:
        dots = [b for b in _blobs(g < 90) if b["area"] >= min_dot_area and inside(b)]
        grey = _greyish(image)
    spacing = abs(1.0 / cal["kx"])  # px per x unit
    ky = abs(cal["ky"])
    out = []
    # with no positions given, every dot is read, its x from the calibration
    targets = list(at) if len(at) else [None] * len(dots)
    order = sorted(dots, key=lambda d: d["c"])
    for k, x in enumerate(targets):
        if x is None:
            d = order[k]
            x = cal["kx"] * d["c"] + cal["cx"]
            c = d["c"]
            cand = [d]
        else:
            c = _col(cal, x)
            cand = [d for d in dots if abs(d["c"] - c) < 0.4 * spacing * min(1.0, abs(xlabels[1] - xlabels[0]) / 2)]
            if not cand:
                cand = [d for d in dots if abs(d["c"] - c) < 25]
        if not cand:
            out.append({"x": x, "y": None, "note": "no dot found at this x"})
            continue
        d = min(cand, key=lambda d: abs(d["c"] - c))
        y = _y(cal, d["r"])
        e = (3 + cal["my"]) * ky
        rec = {"x": x, "y": y, "lo": y - e, "hi": y + e, "px": [d["c"], d["r"]],
               "note": f"dot centroid; column {d['c']:.0f} vs expected {c:.0f}"}
        if at is None or not len(at):
            ex = (3 + cal["mx"]) * abs(cal["kx"])
            rec["note"] = f"dot centroid; x read from the image as {x:.1f} (+/- {ex:.1f})"
        if error_bars:
            c0, c1 = int(round(d["c"])) - 3, int(round(d["c"])) + 4
            band = grey[:, c0:c1].any(axis=1)
            if bars == "dark":  # follow the line from the dot's centre; the caps end it
                band = band.copy()
                band[d["r0"]:d["r1"]] = True
            top, r, miss = None, d["r0"] - 1, 0
            while r > T and miss <= gap:
                if band[r]:
                    top, miss = r, 0
                else:
                    miss += 1
                r -= 1
            bot, r, miss = None, d["r1"], 0
            while r < B and miss <= gap:
                if band[r]:
                    bot, miss = r, 0
                else:
                    miss += 1
                r += 1
            w = (3 + cal["my"]) * ky
            if top is not None:
                hi = _y(cal, top + 3)
                rec.update(bar_hi=hi, bar_hi_outer=hi + w, px_lo=top + 3)
            else:
                hi = _y(cal, d["r0"])
                rec.update(bar_hi=hi, bar_hi_outer=hi + w, px_lo=d["r0"])
                rec["note"] += "; upper bar hidden in the dot, reported as at most the dot"
            if bot is not None:
                lo = _y(cal, bot - 3)
                rec.update(bar_lo=lo, bar_lo_outer=lo - w, px_hi=bot - 3)
            else:
                lo = _y(cal, d["r1"])
                rec.update(bar_lo=lo, bar_lo_outer=lo - w, px_hi=d["r1"])
                rec["note"] += "; lower bar hidden in the dot, reported as at most the dot"
        out.append(rec)
    return out


def read_curve(image, at, xlabels, ylabels, color=(0, 0, 255), tol=90, inner=False, legend_text=False):
    """A thin coloured curve: in the column of each x, the run of pixels within `tol` (RGB distance)
    of the curve's colour; the value is the run's centre and the interval its extent (a steep or
    staircase line spans several rows) widened by half a line width (2 px) and the misfits (the x
    misfit times the local slope). With inner=True only ticks away from the frame's corners are used
    (the corner ticks merge with the frame).

    A legend's sample line is a short flat piece of the colour; by default every such piece is dropped.
    With legend_text=True (second pass) a short flat piece is dropped only if dark legend text lies just
    to its right (within 200 px, away from the right frame and its ticks), so flat stretches of a real
    curve cut short by crossing curves are kept."""
    cal = calibrate(image, xlabels, ylabels, y_inner_only=inner, x_inner_only=inner)
    L, T, R, B = cal["frame"]
    a = np.asarray(image, dtype=float)[:, :, :3]
    mask = np.sqrt(((a - np.asarray(color, float)) ** 2).sum(axis=2)) < tol
    mask[:T + 2, :] = False
    mask[B - 1:, :] = False
    # a legend's sample line is a short flat isolated segment: drop such pieces
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    if legend_text:
        dark = (_gray(image) < 90) & ((a.max(axis=2) - a.min(axis=2)) < 60)
    for i, sl in enumerate(ndimage.find_objects(lab)):
        if (sl[1].stop - sl[1].start) < 700 and (sl[0].stop - sl[0].start) < 15:
            if legend_text:
                c0, c1 = sl[1].stop + 5, min(sl[1].stop + 200, R - 50)
                text = dark[max(sl[0].start - 40, 0):sl[0].stop + 40, c0:c1].sum() if c1 > c0 else 0
                if text <= 50:
                    continue
            mask[sl][lab[sl] == i + 1] = False
    ky = abs(cal["ky"])
    out = []
    for x in at:
        c = int(round(_col(cal, x)))
        rows = np.nonzero(mask[:, max(c - 1, 0):c + 2].any(axis=1))[0]
        if not len(rows):
            out.append({"x": x, "y": None, "note": "no curve pixels in this column"})
            continue
        # the run nearest the curve (take the longest run of consecutive rows)
        runs = np.split(rows, np.nonzero(np.diff(rows) > 3)[0] + 1)
        run = max(runs, key=len)
        r0, r1 = run.min(), run.max()
        rc = 0.5 * (r0 + r1)
        y = _y(cal, rc)
        # local slope in value per px of column, from neighbouring columns
        def centre(cc):
            rr = np.nonzero(mask[:, cc])[0]
            return rr.mean() if len(rr) else None
        cl, cr = centre(max(c - 40, 0)), centre(min(c + 40, mask.shape[1] - 1))
        slope = abs(cr - cl) / 80 if cl is not None and cr is not None else 0.0
        e_lo = _y(cal, r1 + 2 + cal["my"] + slope * cal["mx"])
        e_hi = _y(cal, r0 - 2 - cal["my"] - slope * cal["mx"])
        out.append({"x": x, "y": y, "lo": min(e_lo, e_hi), "hi": max(e_lo, e_hi), "px": [c, rc],
                    "px_lo": int(r0), "px_hi": int(r1), "note": f"run of the curve's colour, rows {r0}-{r1}"})
    return out


def read_bars(image, at, xlabels, ylabels):
    """Navy bars with bright blue error bars (Fig. S1(a), (b)). The x axis is categorical: its ticks,
    drawn at the top only (the bars hide the bottom ones), are matched to the category numbers
    1, 2, ... given as xlabels. A bar is a connected navy region (B > 100, R and G < 60) standing on
    the bottom frame; its value is its top edge. The error bar is the bright blue (B > 200, R, G < 120)
    line through the bar's centre: its extreme rows are the caps (ends taken 2 px in from them).
    Intervals: +/- (2 px + y misfit); bar ends widened by 3 px + y misfit."""
    cal = calibrate(image, xlabels, ylabels, x_top_only=True, y_inner_only=True)
    L, T, R, B = cal["frame"]
    a = np.asarray(image, dtype=float)[:, :, :3]
    navy = (a[:, :, 2] > 100) & (a[:, :, 0] < 60) & (a[:, :, 1] < 60) & (a[:, :, 2] < 200)
    bright = (a[:, :, 2] > 200) & (a[:, :, 0] < 120) & (a[:, :, 1] < 120)
    ky = abs(cal["ky"])
    bars = [b for b in _blobs(navy) if b["area"] > 5000 and b["r1"] >= B - 10]
    out = []
    for b in sorted(bars, key=lambda b: b["c"]):
        x = cal["kx"] * b["c"] + cal["cx"]
        c = int(round(b["c"]))
        col = navy[:, c - 3:c + 4].any(axis=1)
        rows = np.nonzero(col)[0]
        top = int(rows.min())
        y = _y(cal, top)
        e = (2 + cal["my"]) * ky
        rec = {"x": float(round(x)), "y": y, "lo": y - e, "hi": y + e, "px": [b["c"], top],
               "note": f"top edge of the bar at column {b['c']:.0f} (category position read as {x:.2f})"}
        br = np.nonzero(bright[:, c - 8:c + 9].any(axis=1))[0]
        if len(br):
            w = (3 + cal["my"]) * ky
            hi, lo = _y(cal, br.min() + 2), _y(cal, br.max() - 2)
            rec.update(bar_hi=hi, bar_lo=lo, bar_hi_outer=hi + w, bar_lo_outer=lo - w,
                       px_lo=int(br.min()), px_hi=int(br.max()))
        out.append(rec)
    return out


def read_exes(image, at, xlabels, ylabels):
    cal = calibrate(image, xlabels, ylabels)
    L, T, R, B = cal["frame"]
    a = np.asarray(image, dtype=float)[:, :, :3]
    blue = ((a[:, :, 2] - a[:, :, 0]) > 25) & ((a[:, :, 2] - a[:, :, 1]) > 25) & (a[:, :, 2] > 150)
    blobs = [b for b in _blobs(blue) if L < b["c"] < R and T < b["r"] < B and b["area"] >= 20]
    spacing = abs(1.0 / cal["kx"]) * abs(xlabels[1] - xlabels[0])
    ky = abs(cal["ky"])
    out = []
    for x in at:
        c = _col(cal, x)
        near = [b for b in blobs if abs(b["c"] - c) < 0.08 * spacing + 30]
        if not near:
            out.append({"x": x, "y": None, "note": "no blue mark found at this x"})
            continue
        r0 = min(b["r0"] for b in near)
        r1 = max(b["r1"] for b in near) - 1
        rc = 0.5 * (r0 + r1)
        y = _y(cal, rc)
        e = (3 + cal["my"]) * ky
        lo, hi = _y(cal, r1) - e, _y(cal, r0) + e
        lo, hi = min(lo, hi), max(lo, hi)
        cc = float(np.mean([b["c"] for b in near]))
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [cc, rc], "px_lo": r0, "px_hi": r1,
                    "note": f"centre of all blue marks at this x ({len(near)} blobs: the light 'x' and the "
                            "darker mark beside it); the interval spans them all"})
    return out
