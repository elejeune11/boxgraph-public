"""Shared reading code for the colour-filled stability diagrams of shen2025 (Figs. 2, 5, 13).

Each diagram is a raster image of coloured regions (S light blue, SS yellow, US green,
U dark blue, N mid blue) separated by thin black lines, inside a black frame with
inward ticks. Everything is found in the rendered crop:

* Frame: the outermost groups of near-black rows and columns longer than half the crop.
  Its inner edges' line centres are the axis limits (MATLAB draws the box at the limits).
* Ticks: short near-black marks rising from the inner side of the bottom and top frame
  lines (x) and leaving the left and right frame lines (y). Ticks found on both sides are
  averaged. The ticks plus the two frame lines are matched in order to the printed labels
  (given by the caller as `xlabels`, `ylabels`, first label at the left/bottom frame line),
  and a straight line is fitted; the misfit is the largest residual in pixels.
* Boundary: in the pixel column of each requested x, the runs of near-black pixels inside
  the frame are the drawn boundary lines. Each run is classified by the region colours just
  above and below it (nearest reference colour). The run whose (above, below) pair is the
  one asked for is read at its centre; `pick` chooses the topmost or bottommost when there
  are several. Where the two regions meet without a drawn line, the colour change itself is
  used.
* Interval: the line's half-thickness plus the calibration misfit plus one pixel, converted
  to axis units (the boundary is the centre of a line about 12-15 px thick at this dpi).
"""
import math

import numpy as np

REGIONS = {
    "S": (39, 151, 238),
    "SS": (242, 242, 18),
    "US": (130, 201, 84),
    "U": (58, 36, 160),
    "N": (68, 86, 250),
    "white": (255, 255, 255),
}


def _groups(idx):
    out, cur = [], []
    for i in list(idx) + [None]:
        if cur and (i is None or i != cur[-1] + 1):
            out.append((cur[0], cur[-1]))
            cur = []
        if i is not None:
            cur.append(i)
    return out


def _black(img, thr=95):
    return img.max(axis=2) < thr


def frame(img):
    blk = _black(img)
    H, W = blk.shape
    # 0.25: a curve lying on the bottom line hides much of it
    rows = _groups([r for r in range(H) if blk[r].sum() > 0.25 * W])
    cols = _groups([c for c in range(W) if blk[:, c].sum() > 0.5 * H])
    left, right = cols[0], cols[-1]
    # the frame's top and bottom lines are where its left line starts and ends (a crop may also
    # catch the frame line of the panel above or below)
    def longest(line):
        # longest dark run, bridging gaps of up to 80 px (a curve drawn over the frame line)
        idx = np.nonzero(line)[0].tolist()
        best, start, prev = (0, 0), None, None
        for i in idx + [None]:
            if i is None or (prev is not None and i - prev > 80):
                if start is not None and prev - start > best[1] - best[0]:
                    best = (start, prev)
                start = i
            elif start is None:
                start = i
            prev = i
        return best

    # the longer of the left and right frame lines (a curve may cover part of one)
    r0, r1 = max((longest(blk[:, (g[0] + g[1]) // 2]) for g in (left, right)), key=lambda t: t[1] - t[0])
    top = min(rows, key=lambda g: abs(g[0] - r0))
    bot = min(rows, key=lambda g: abs(g[1] - r1))
    c_r = (top[0] + top[1]) // 2
    q0, q1 = longest(blk[c_r, :])
    left = min(cols, key=lambda g: abs(g[0] - q0))
    right = min(cols, key=lambda g: abs(g[1] - q1))
    return {"top": top, "bottom": bot, "left": left, "right": right}


def _ticks_on(band, axis_len, lo, hi, min_frac=0.7):
    """Centres of tick marks in a band: positions along the band whose pixels are mostly black."""
    frac = band.mean(axis=0) if band.ndim == 2 else band
    # a tick is a thin mark: black across the band here, not 16-20 px to either side
    idx = [i for i in range(lo, hi) if frac[i] >= min_frac
           and frac[max(i - 18, 0)] < 0.4 and frac[min(i + 18, len(frac) - 1)] < 0.4]
    return [(a + b) / 2.0 for a, b in _groups(idx) if b - a <= 30]


def calibrate(img, xlabels, ylabels, tick_len=(3, 15), log_x=False, log_y=False, x_edges=True, y_edges=True):
    """x_edges / y_edges: whether the frame lines carry the first and last labels (True), or
    the labels belong only to ticks inside the frame (False)."""
    fr = frame(img)
    blk = _black(img)
    l_in, r_in = fr["left"][1] + 1, fr["right"][0] - 1
    t_in, b_in = fr["top"][1] + 1, fr["bottom"][0] - 1
    xl = (fr["left"][0] + fr["left"][1]) / 2.0
    xr = (fr["right"][0] + fr["right"][1]) / 2.0
    yt = (fr["top"][0] + fr["top"][1]) / 2.0
    yb = (fr["bottom"][0] + fr["bottom"][1]) / 2.0
    a, b = tick_len
    margin = 25
    # x ticks: rising from the bottom line, hanging from the top line
    xb = _ticks_on(blk[b_in - b:b_in - a + 1, :], None, l_in + margin, r_in - margin)
    xt = _ticks_on(blk[t_in + a:t_in + b + 1, :], None, l_in + margin, r_in - margin)
    yl = _ticks_on(blk[:, l_in + a:l_in + b + 1].T, None, t_in + margin, b_in - margin)
    yr = _ticks_on(blk[:, r_in - b:r_in - a + 1].T, None, t_in + margin, b_in - margin)

    def nearest(cands, start, end, n):
        """Of the candidates, the one nearest each of the n evenly spaced positions between the
        frame lines (within 3% of the span); a list shorter than n if one is missing."""
        got = []
        for k in range(1, n + 1):
            e = start + k * (end - start) / (n + 1)
            near = [c for c in cands if abs(c - e) <= 0.03 * abs(end - start)]
            if near:
                got.append(min(near, key=lambda c: abs(c - e)))
        return got

    def regular(cands, n):
        """Without labelled frame lines: the n candidates that are evenly spaced (the labelled
        ticks), by the shared helper; a list of another length if they cannot be found."""
        from boxgraph.digitize import regular_ticks
        got = regular_ticks(sorted(cands), tol=3.0, min_gap=40)
        return got if len(got) == n else got[:0] if len(got) < n else got

    if x_edges:
        xb = nearest(xb, xl, xr, len(xlabels) - 2)
        xt = nearest(xt, xl, xr, len(xlabels) - 2)
    else:
        xb, xt = regular(xb, len(xlabels)), regular(xt, len(xlabels))
    if y_edges:
        yl = nearest(yl, yb, yt, len(ylabels) - 2)
        yr = nearest(yr, yb, yt, len(ylabels) - 2)
    else:
        yl = regular(sorted(yl, reverse=True), len(ylabels))
        yr = regular(sorted(yr, reverse=True), len(ylabels))
        yl, yr = sorted(yl, reverse=True), sorted(yr, reverse=True)

    def merge(p, q, n):
        if len(p) == n and len(q) == n:
            return [(u + v) / 2 for u, v in zip(p, q)], max(abs(u - v) for u, v in zip(p, q)) / 2
        if len(p) == n:
            return p, 0.0
        if len(q) == n:
            return q, 0.0
        raise ValueError(f"expected {n} inner ticks, found {len(p)} and {len(q)}")

    if x_edges:
        xin, xspread = merge(xb, xt, len(xlabels) - 2)
        xpix = [xl] + xin + [xr]
    else:
        xpix, xspread = merge(xb, xt, len(xlabels))
    if y_edges:
        yin, yspread = merge(yl, yr, len(ylabels) - 2)
        ypix = [yb] + yin + [yt]
    else:
        ypix, yspread = merge(yl, yr, len(ylabels))

    def fit(pix, labels, log):
        u = np.array([math.log10(v) if log else v for v in labels], float)
        p = np.array(pix, float)
        bcoef, acoef = np.polyfit(p, u, 1)
        resid = float(np.max(np.abs(p - (u - acoef) / bcoef)))
        return acoef, bcoef, resid

    ax, bx, rx = fit(xpix, xlabels, log_x)
    ay, by, ry = fit(ypix, ylabels, log_y)
    cal = {
        "frame": fr, "inner": (l_in, t_in, r_in, b_in),
        "x": (ax, bx, max(rx, xspread, 0.5), log_x), "y": (ay, by, max(ry, yspread, 0.5), log_y),
        "xpix": xpix, "ypix": ypix,
    }
    return cal


def to_px(axis, v):
    a, b, _, log = axis
    u = math.log10(v) if log else v
    return (u - a) / b


def to_val(axis, p):
    a, b, _, log = axis
    u = a + b * p
    return 10 ** u if log else u


def classify(rgb):
    rgb = np.asarray(rgb, float)
    best = min(REGIONS, key=lambda k: float(np.sum((rgb - np.array(REGIONS[k])) ** 2)))
    return best


def _region_at(img, col, row, step, limit):
    """Colour class of the first plain (not dark) pixel from `row` in direction `step`."""
    r = row
    for _ in range(40):
        r += step
        if r <= limit[0] or r >= limit[1]:
            return None
        px = img[r, col]
        if px.max() >= 95:
            # move a few pixels further, past the line's blur
            r2 = min(max(r + 4 * step, limit[0] + 1), limit[1] - 1)
            return classify(img[r2, col])
    return None


def lines_in_column(img, cal, col):
    l_in, t_in, r_in, b_in = cal["inner"]
    blk = _black(img)
    out = []
    for a, b in _groups([r for r in range(t_in + 3, b_in - 2) if blk[r, col]]):
        above = _region_at(img, col, a, -1, (t_in, b_in))
        below = _region_at(img, col, b, +1, (t_in, b_in))
        out.append({"top": a, "bottom": b, "c": (a + b) / 2.0, "above": above, "below": below})
    # colour changes without a drawn line
    prev = None
    for r in range(t_in + 3, b_in - 2):
        px = img[r, col]
        if px.max() < 95:
            prev = None
            continue
        k = classify(px)
        if prev is not None and k != prev[0] and r - prev[1] == 1:
            # confirm both sides are stable over 4 px
            up = classify(img[max(r - 5, t_in + 1), col])
            dn = classify(img[min(r + 4, b_in - 1), col])
            if up == prev[0] and dn == k:
                out.append({"top": r, "bottom": r, "c": r - 0.5, "above": up, "below": dn, "noline": True})
        prev = (k, r)
    return sorted(out, key=lambda d: d["c"])


def read_boundary(image, at, xlabels, ylabels, above, below, pick="top", log_x=False, log_y=False,
                  xrange=None, x_edges=True, y_edges=True, tick_len=(3, 15)):
    img = np.asarray(image)[:, :, :3].astype(int)
    cal = calibrate(img, xlabels, ylabels, log_x=log_x, log_y=log_y, x_edges=x_edges, y_edges=y_edges,
                    tick_len=tick_len)
    xa, ya = cal["x"], cal["y"]
    note_cal = (f"x misfit {xa[2]:.1f} px, y misfit {ya[2]:.1f} px; frame and ticks "
                f"{[round(p, 1) for p in cal['xpix']]} / {[round(p, 1) for p in cal['ypix']]}")
    out = []
    for x in at:
        x = float(x)
        if xrange and not (xrange[0] <= x <= xrange[1]):
            out.append({"x": x, "y": None, "note": "outside the range where this boundary is read"})
            continue
        col = int(round(to_px(xa, x)))
        # never read on the frame itself
        col = min(max(col, cal["inner"][0] + 6), cal["inner"][2] - 6)
        ab = above if isinstance(above, (list, tuple)) else [above]
        be = below if isinstance(below, (list, tuple)) else [below]
        cands = [d for d in lines_in_column(img, cal, col) if d["above"] in ab and d["below"] in be
                 and d["bottom"] - d["top"] >= 2]  # a drawn line, not a one-pixel blend
        if not cands:
            out.append({"x": x, "y": None, "note": f"no {above}/{below} boundary in column {col}"})
            continue
        d = cands[0] if pick == "top" else cands[-1]
        half = (d["bottom"] - d["top"] + 1) / 2.0
        err = half + ya[2] + 1.0
        y = to_val(ya, d["c"])
        lo, hi = sorted((to_val(ya, d["c"] + err), to_val(ya, d["c"] - err)))
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [col, d["c"]],
                    "px_lo": d["c"] - err, "px_hi": d["c"] + err,
                    "note": f"{d['above']} above / {d['below']} below, line rows {d['top']}-{d['bottom']}; {note_cal}"})
    return out


# --------------------------------------------------------------------------------------------
# Coloured line curves (Figs. 8-11): same frame and tick calibration; the curve is the set of
# pixels near its colour, traced column by column from a seed so that the legend sample and
# other curves are not taken; a value is a quadratic fit of the traced centres within
# +-`window` columns of the requested x (this bridges the gaps of dashed lines).
# --------------------------------------------------------------------------------------------


def _col_runs(mask, col, min_run):
    return [((a + b) / 2.0, b - a + 1) for a, b in _groups(np.nonzero(mask[:, col])[0].tolist())
            if b - a + 1 >= min_run]


def trace_curve(mask, seed_col, seed_row, max_jump=25, max_gap=120, min_run=4):
    H, W = mask.shape
    path = {}

    def near_seed(c):
        return [r for r in _col_runs(mask, c, min_run) if abs(r[0] - seed_row) <= 80]

    runs = near_seed(seed_col)
    c0 = seed_col
    k = 0
    while not runs and k < max_gap:  # a dash gap at the seed: look sideways
        k += 1
        for c in (seed_col + k, seed_col - k):
            if 0 <= c < W:
                runs = near_seed(c)
                if runs:
                    c0 = c
                    break
    if not runs:
        return path
    r0, t0 = min(runs, key=lambda r: abs(r[0] - seed_row))
    path[c0] = (r0, t0)
    for step in (1, -1):
        hist = [(c0, r0)]
        thick = [t0]
        c, gap = c0, 0
        while True:
            c += step
            if c < 0 or c >= W or gap > max_gap:
                break
            if len(hist) >= 2:
                (ca, ra), (cb, rb) = hist[-1], hist[max(0, len(hist) - 30)]
                slope = (ra - rb) / (ca - cb) if ca != cb else 0.0
                pred = ra + slope * (c - ca)
            else:
                pred = hist[-1][1]
            runs = _col_runs(mask, c, min_run)
            near = [r for r in runs if abs(r[0] - pred) <= max_jump + 0.5 * gap]
            if near:
                r, t = min(near, key=lambda r: abs(r[0] - pred))
                if t < 0.6 * float(np.median(thick)):
                    # the slanted end of a dash covers only part of the line: its centre is off the
                    # line's centre, so it is neither read nor used to predict
                    gap += 1
                    continue
                path[c] = (r, t)
                hist.append((c, r))
                thick.append(t)
                gap = 0
            else:
                gap += 1
    return path


def read_curve(image, at, xlabels, ylabels, color, seed, tol=60, window=45, min_run=4,
               log_x=False, log_y=False, x_edges=True, y_edges=True, max_jump=25):
    """`seed` = (x, y) in axis units: a point near the intended curve, used only to say which
    of the curves of this colour is meant; the values come from the traced pixels."""
    img = np.asarray(image)[:, :, :3].astype(int)
    cal = calibrate(img, xlabels, ylabels, log_x=log_x, log_y=log_y, x_edges=x_edges, y_edges=y_edges)
    xa, ya = cal["x"], cal["y"]
    l_in, t_in, r_in, b_in = cal["inner"]
    dist = np.sqrt(((img - np.array(color)) ** 2).sum(axis=2))
    mask = dist < tol
    inner = np.zeros_like(mask)
    inner[t_in + 4:b_in - 3, l_in + 4:r_in - 3] = True
    mask &= inner
    path = trace_curve(mask, int(round(to_px(xa, seed[0]))), to_px(ya, seed[1]), max_jump=max_jump,
                       min_run=min_run)
    note_cal = (f"x misfit {xa[2]:.1f} px, y misfit {ya[2]:.1f} px; frame and ticks "
                f"{[round(p, 1) for p in cal['xpix']]} / {[round(p, 1) for p in cal['ypix']]}")
    out = []
    for x in at:
        x = float(x)
        col = to_px(xa, x)
        pts = [(c, r, t) for c, (r, t) in path.items() if abs(c - col) <= window]
        if len(pts) < 6 or min(abs(c - col) for c, _, _ in pts) > 0.75 * window \
                or not (min(c for c, _, _ in pts) <= col + 3 and max(c for c, _, _ in pts) >= col - 3):
            out.append({"x": x, "y": None, "note": f"curve not traced at column {col:.0f}"})
            continue
        cs = np.array([p[0] for p in pts], float)
        rs = np.array([p[1] for p in pts], float)
        deg = 2 if (cs.max() - cs.min()) > window and len(pts) >= 10 else 1
        coef = np.polyfit(cs - col, rs, deg)
        row = float(np.polyval(coef, 0.0))
        rms = float(np.sqrt(np.mean((np.polyval(coef, cs - col) - rs) ** 2)))
        thick = float(np.median([p[2] for p in pts]))
        if row + thick >= b_in - 4 or row - thick <= t_in + 4:
            out.append({"x": x, "y": None, "note": f"the curve lies on the frame line at column {col:.0f}, "
                                                    "half hidden by it: its centre cannot be read"})
            continue
        slope = float(coef[-2]) if deg >= 1 else 0.0
        err = ya[2] + abs(slope) * xa[2] + 2 * rms + 0.25 * thick + 1.0
        y = to_val(ya, row)
        lo, hi = sorted((to_val(ya, row + err), to_val(ya, row - err)))
        out.append({"x": x, "y": y, "lo": lo, "hi": hi, "px": [col, row], "px_lo": row - err,
                    "px_hi": row + err,
                    "note": f"{len(pts)} traced columns, line {thick:.0f} px, fit rms {rms:.2f} px; {note_cal}"})
    return out


# --------------------------------------------------------------------------------------------
# Filled round markers of one colour (Fig. 12): pixels near the colour, closed (a line drawn
# over a marker splits it), labelled into blobs; a marker is a compact blob of about the commonest
# size. Its value is the blob's centroid. Interval: calibration misfit + 1 px + a quarter of the
# marker radius (a marker partly covered by another mark has its centroid moved by up to that).
# --------------------------------------------------------------------------------------------


def read_markers(image, at, xlabels, ylabels, color, tol=70, x_edges=True, y_edges=True):
    from scipy import ndimage

    img = np.asarray(image)[:, :, :3].astype(int)
    cal = calibrate(img, xlabels, ylabels, x_edges=x_edges, y_edges=y_edges)
    xa, ya = cal["x"], cal["y"]
    l_in, t_in, r_in, b_in = cal["inner"]
    mask = np.sqrt(((img - np.array(color)) ** 2).sum(axis=2)) < tol
    mask = ndimage.binary_closing(mask, iterations=4)
    lab, n = ndimage.label(mask)
    blobs = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        area = int((lab[sl] == i).sum())
        if area < 50 or not (0.5 <= h / w <= 1.6) or area < 0.55 * h * w:
            continue
        # centre at the marker's widest rows (its diameter): curves drawn over the top or bottom of a
        # marker hide part of it and would move a centroid
        sub = lab[sl] == i
        widths = sub.sum(axis=1)
        rows = np.nonzero(widths >= 0.97 * widths.max())[0]
        r = sl[0].start + float(rows.mean())
        cols = [np.nonzero(sub[k])[0] for k in rows]
        c = sl[1].start + float(np.mean([(cc.min() + cc.max()) / 2.0 for cc in cols]))
        h = w = int(widths.max())  # the diameter
        blobs.append((c, r, h, w, area))
    if not blobs:
        return []
    typical = float(np.median([b[4] for b in blobs]))
    blobs = [b for b in blobs if 0.5 * typical <= b[4] <= 1.6 * typical]
    note_cal = (f"x misfit {xa[2]:.1f} px, y misfit {ya[2]:.1f} px; frame and ticks "
                f"{[round(p, 1) for p in cal['xpix']]} / {[round(p, 1) for p in cal['ypix']]}")
    out = []
    full = max(b[4] for b in blobs)
    for c, r, h, w, area in sorted(blobs):
        rad = (h + w) / 4.0
        # a marker with less area than the fullest one is partly covered: when the cover reaches past
        # its middle the widest visible row is not its diameter, and the centre can be off by up to
        # a radius; widen in proportion to the missing area
        err = ya[2] + 1.0 + 0.25 * rad + min(rad, 2.0 * rad * (1.0 - area / full))
        lo, hi = sorted((to_val(ya, r + err), to_val(ya, r - err)))
        out.append({"x": to_val(xa, c), "y": to_val(ya, r), "lo": lo, "hi": hi, "px": [c, r],
                    "px_lo": r - err, "px_hi": r + err,
                    "note": f"marker {w}x{h} px, area {area}; x read to +-{(xa[2] + 1 + 0.25 * rad) * abs(xa[1]):.3f}; "
                            f"{note_cal}"})
    return out
