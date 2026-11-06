"""Shared reading code for this record's lifetime-versus-force panels.

The panels are vector plots: open markers (circles, triangles, squares) or filled
markers (diamonds) joined by lines, with vertical error bars ending in caps, an
L-shaped pair of axes with outward ticks, and in some panels a y axis broken
into two linear segments. Everything is found in the rendered crop; the only
things a reading file supplies are the printed tick labels it matched, which
series to read (colour and marker shape), the rough marker size in pixels and
regions (titles, legends) where markers are not to be looked for.
"""

import numpy as np
from scipy import ndimage as ndi


# ----------------------------------------------------------------------------
# colour masks
# ----------------------------------------------------------------------------

def gray(img):
    return img[..., :3].astype(float).mean(axis=2)


def mask_for(img, colour):
    g = gray(img)
    black = g < 110
    if colour == "black":
        return black
    near_black = ndi.binary_dilation(black, iterations=3)
    if colour == "lightgrey":  # the grey of the Fc/GG-7 series (about 204)
        return (g > 180) & (g < 232) & ~near_black
    if colour == "midgrey":  # filled grey markers (about 150)
        return (g >= 110) & (g <= 180) & ~near_black
    raise ValueError(colour)


def _runs(v):
    """Start and end (exclusive) of runs of True in a 1-d bool array."""
    d = np.diff(np.concatenate([[0], v.astype(np.int8), [0]]))
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))


# ----------------------------------------------------------------------------
# axes and calibration
# ----------------------------------------------------------------------------

def find_axes(black):
    H, W = black.shape
    best_c = [max((e - s for s, e in _runs(black[:, c])), default=0) for c in range(int(W * 0.5))]
    m = max(best_c)
    ycols = [c for c, v in enumerate(best_c) if v >= 0.9 * m]
    ycols = _contiguous(ycols, min(ycols, key=lambda c: -best_c[c]))
    best_r = [max((e - s for s, e in _runs(black[r, :])), default=0) for r in range(H)]
    rows = range(int(H * 0.4), H)
    m = max(best_r[r] for r in rows)
    xrows = [r for r in rows if best_r[r] >= 0.9 * m]
    xrows = _contiguous(xrows, max(xrows, key=lambda r: best_r[r]))
    return (min(ycols), max(ycols)), (min(xrows), max(xrows))


def _contiguous(vals, seed):
    s = set(vals)
    lo = hi = seed
    while lo - 1 in s:
        lo -= 1
    while hi + 1 in s:
        hi += 1
    return list(range(lo, hi + 1))


def _group(idx, min_len=1):
    out = []
    for s, e in _runs(idx):
        if e - s >= min_len:
            out.append((s, e))
    return out


def y_ticks(black, ycols, xrows, min_len=12):
    c0, c1 = ycols
    H = black.shape[0]
    left = np.zeros(H, int)
    right = np.zeros(H, int)
    for r in range(H):
        k = 0
        while c0 - 1 - k >= 0 and black[r, c0 - 1 - k]:
            k += 1
        left[r] = k
        k = 0
        while c1 + 1 + k < black.shape[1] and black[r, c1 + 1 + k]:
            k += 1
        right[r] = k
    near_x = np.zeros(H, bool)
    near_x[max(0, xrows[0] - 3):xrows[1] + 4] = True
    cand = (left >= min_len) & ((right <= 3) | near_x)
    groups = _group(cand, 3)
    if not groups:
        return [], []
    # a tick is horizontal: its left end is the same on every row (the slanted marks of an axis
    # break are not)
    def flat(s, e):
        inner = left[s + 2:e - 2] if e - s > 6 else left[s:e]
        return inner.max() - inner.min() <= 7

    groups = [(s, e) for s, e in groups if flat(s, e)]
    th = np.median([e - s for s, e in groups])
    groups = [(s, e) for s, e in groups if 0.5 * th <= e - s <= 2.0 * th]
    return [(s + e - 1) / 2 for s, e in groups], [int(np.median(left[s:e])) for s, e in groups]


def x_ticks(black, ycols, xrows, min_len=12):
    r1 = xrows[1]
    W = black.shape[1]
    down = np.zeros(W, int)
    for c in range(W):
        k = 0
        while r1 + 1 + k < black.shape[0] and black[r1 + 1 + k, c]:
            k += 1
        down[c] = k
    down[:max(0, ycols[0] - 5)] = 0  # left of the y axis lie its tick labels, not x ticks
    groups = _group(down >= min_len, 3)
    if not groups:
        return []
    th = np.median([e - s for s, e in groups])
    groups = [(s, e) for s, e in groups if 0.5 * th <= e - s <= 2.0 * th]
    return [(s + e - 1) / 2 for s, e in groups]


class Linear:
    """value = a + b * pixel, fitted to (pixel, value) marks."""

    def __init__(self, marks):
        p = np.array([m[0] for m in marks], float)
        v = np.array([m[1] for m in marks], float)
        self.b, self.a = np.polyfit(p, v, 1)
        self.misfit_px = float(np.max(np.abs((v - self.a) / self.b - p))) if len(p) > 2 else 0.0
        self.n = len(p)
        self.lo_px, self.hi_px = float(p.min()), float(p.max())

    def value(self, px):
        return self.a + self.b * px

    def px(self, value):
        return (value - self.a) / self.b


class YAxis:
    """A y axis of one or two linear segments (a broken axis), bottom segment first."""

    def __init__(self, tick_rows, segments):
        rows = sorted(tick_rows, reverse=True)  # bottom first
        labels = [v for seg in segments for v in seg]
        if len(rows) != len(labels):
            raise ValueError(f"found {len(rows)} y ticks at rows {[round(r) for r in rows]}, expected {len(labels)} "
                             f"for labels {labels}")
        self.segs = []
        k = 0
        for seg in segments:
            self.segs.append(Linear(list(zip(rows[k:k + len(seg)], seg))))
            k += len(seg)
        # a row above the midpoint between two segments' end ticks belongs to the upper one
        self.bounds = [(self.segs[i].lo_px + self.segs[i + 1].hi_px) / 2 for i in range(len(self.segs) - 1)]
        self.misfit_px = max(s.misfit_px for s in self.segs)

    def seg_of(self, row):
        for i, b in enumerate(self.bounds):
            if row > b:
                return i
        return len(self.segs) - 1

    def value(self, row, seg=None):
        s = self.segs[self.seg_of(row) if seg is None else seg]
        return float(s.value(row))

    def per_px(self, row):
        return abs(self.segs[self.seg_of(row)].b)


def calibrate(img, y_segments, x_labels):
    black = mask_for(img, "black")
    ycols, xrows = find_axes(black)
    yr, _ = y_ticks(black, ycols, xrows)
    xc = x_ticks(black, ycols, xrows)
    ya = YAxis(yr, y_segments)
    # a broken axis: the segments meet where the axis line is interrupted
    for i in range(len(ya.bounds)):
        lo_row, hi_row = int(ya.segs[i + 1].hi_px), int(ya.segs[i].lo_px)
        band = black[lo_row:hi_row, ycols[0]:ycols[1] + 1].mean(axis=1)
        gap = np.flatnonzero(band < 0.5) + lo_row
        if len(gap):
            ya.bounds[i] = float(gap.mean())
    if len(xc) != len(x_labels):
        raise ValueError(f"found {len(xc)} x ticks at columns {[round(c) for c in xc]}, expected {len(x_labels)}")
    xa = Linear(list(zip(sorted(xc), x_labels)))
    return black, ycols, xrows, xa, ya


# ----------------------------------------------------------------------------
# markers
# ----------------------------------------------------------------------------

def line_width(mask):
    """The most common thickness of the drawn lines: the mode of short horizontal dark runs."""
    lens = []
    for r in range(0, mask.shape[0], 7):
        lens += [e - s for s, e in _runs(mask[r]) if 4 <= e - s <= 60]
    if not lens:
        return 8
    v, c = np.unique(lens, return_counts=True)
    return int(v[np.argmax(c)])


def _shape_level(shape, n):
    """A 'radius' function over a (2n+1)^2 grid whose level sets are the marker's outline:
    circle (distance), square (Chebyshev distance), triangle with its apex up (distance in the
    triangle's own norm, so the level r is the triangle of inradius r, centroid at the origin)."""
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(float)
    if shape == "circle":
        return np.hypot(xx, yy)
    if shape == "square":
        return np.maximum(np.abs(xx), np.abs(yy))
    if shape == "triangle":
        # outward normals: the base (down, +y in image rows) and the two sides
        s3 = np.sqrt(3) / 2
        return np.max(np.stack([yy, -0.5 * yy + s3 * xx, -0.5 * yy - s3 * xx]), axis=0)
    raise ValueError(shape)


class _Correlator:
    """Correlates one mask with several kernels, transforming the mask once."""

    def __init__(self, mask, kmax):
        from scipy import fft as sfft

        self.fft = sfft
        self.H, self.W = mask.shape
        self.shp = (sfft.next_fast_len(self.H + kmax), sfft.next_fast_len(self.W + kmax))
        self.F = sfft.rfft2(mask.astype(float), self.shp)

    def __call__(self, ker):
        k = ker[::-1, ::-1]
        full = self.fft.irfft2(self.F * self.fft.rfft2(k, self.shp), self.shp)
        r, c = (k.shape[0] - 1) // 2, (k.shape[1] - 1) // 2
        return full[r:r + self.H, c:c + self.W]


def _score_map(corr, shape, R, t, corr_ring=None):
    n = int(2 * R + t) + 2
    lev = _shape_level(shape, n)
    ring = (np.abs(lev - R) <= max(1.0, t / 2 - 2)).astype(float)
    inner = (lev <= R - t / 2 - 3).astype(float)
    return (corr_ring or corr)(ring) / ring.sum(), corr(inner) / max(inner.sum(), 1)


def open_markers(mask, shape, size, box, exclude, thr=0.8, under_grey=None, outline=None, max_inner=0.75):
    """Open markers of one shape, found by matching their outline (a ring, a square or a triangle)
    to the series' mask. Lines and error bars cross the outline but cover little of it; the inside
    must be mostly empty. size: rough outer width of the marker in pixels; outline: the outline's
    thickness, when it is not that of the series' lines."""
    t = outline or line_width(mask)
    if shape == "triangle":
        # outer width of an equilateral triangle of inradius r with outline t: 2*sqrt(3)*(r + t/2)
        R0 = size / (2 * np.sqrt(3)) - t / 2
    else:
        R0 = size / 2 - t / 2
    # the outline's mid-line radius: the middle of the radii at which the outlines match best
    scored = []
    kmax = 2 * (int(2 * (R0 + 4) + t) + 2) + 1
    corr = _Correlator(mask, kmax)
    # grey series are drawn over the black ones: where a grey marker or line crosses a black outline,
    # the outline counts as present
    corr_ring = _Correlator(mask | under_grey, kmax) if under_grey is not None else corr
    for R in np.arange(R0 - 4, R0 + 4.5, 2.0 if t >= 10 else 1.0):
        ring, inner = _score_map(corr, shape, R, t, corr_ring)
        own = _score_map(corr, shape, R, t)[0] if corr_ring is not corr else ring
        # (the stem and the joining lines run into the marker, so its inside is not empty; at least
        # most of the outline must be in the series' own colour)
        sc = np.where((inner < max_inner) & (own >= 0.55), ring, 0)
        if outline:
            # a thin outline: just outside it the page is mostly empty (inside a thick line it is not)
            n = int(2 * R + t) + 12
            lev = _shape_level(shape, n)
            band = ((lev >= R + t / 2 + 3) & (lev <= R + t / 2 + 8)).astype(float)
            sc = np.where(corr(band) / band.sum() < 0.5, sc, 0)
        scored.append((float(np.sort(sc.ravel())[-50:].mean()), float(R), sc))
    top = max(s[0] for s in scored)
    good = [s for s in scored if s[0] >= top - 0.01]
    _, R, sc = good[len(good) // 2]
    H, W = mask.shape
    # each patch of high score is one marker; its centre is the centre of the patch's best part
    lab, n = ndi.label(sc >= thr)
    out = []
    for i, sl in enumerate(ndi.find_objects(lab)):
        patch = np.where(lab[sl] == i + 1, sc[sl], 0)
        best_rows, best_cols = np.nonzero(patch >= patch.max() - 0.02)
        cr = float(best_rows.mean() + sl[0].start)
        cc = float(best_cols.mean() + sl[1].start)
        r, c = int(round(cr)), int(round(cc))
        if not (box[0] < c < box[2] and box[1] < r < box[3]):
            continue
        if any(e[0] <= c <= e[2] and e[1] <= r <= e[3] for e in exclude):
            continue
        if shape == "triangle":
            top, bot = cr - 2 * R - t, cr + R + t / 2
            bbox_mid = (top + bot) / 2
        else:
            top, bot = cr - R - t / 2, cr + R + t / 2
            bbox_mid = cr
        out.append({"cc": float(cc), "cr": float(cr), "top": int(np.floor(top)), "bot": int(np.ceil(bot)),
                    "centroid_r": float(cr), "bbox_mid": float(bbox_mid), "score": float(patch.max()), "R": float(R),
                    "t": t})
    # two overlapping outlines can make a third, false match between them: of two matches closer than
    # most of a radius, keep the better one
    keep = []
    for m in sorted(out, key=lambda m: -m["score"]):
        if all(np.hypot(m["cc"] - k["cc"], m["cr"] - k["cr"]) >= 1.1 * R for k in keep):
            keep.append(m)
    return sorted(keep, key=lambda m: m["cc"])


def _joined(line_mask, a, b, gap_r):
    """The fraction of the straight path between two marker centres, outside both markers, that is drawn."""
    n = int(np.hypot(b["cc"] - a["cc"], b["cr"] - a["cr"]) / 2) + 2
    H, W = line_mask.shape
    hits = tot = 0
    for s in np.linspace(0, 1, n):
        c = a["cc"] + s * (b["cc"] - a["cc"])
        r = a["cr"] + s * (b["cr"] - a["cr"])
        if np.hypot(c - a["cc"], r - a["cr"]) <= gap_r or np.hypot(c - b["cc"], r - b["cr"]) <= gap_r:
            continue
        tot += 1
        ri, ci = int(round(r)), int(round(c))
        if line_mask[max(0, ri - 3):min(H, ri + 4), max(0, ci - 3):min(W, ci + 4)].any():
            hits += 1
    return 1.0 if tot == 0 else hits / tot


def chain(ms, line_mask, min_frac):
    """The markers of one series are joined in order of force by its line. Of the candidate matches,
    keep the longest chain, in order of x, in which each marker is joined to the next by a drawn path
    (a false match off the line is not joined to its neighbours)."""
    if len(ms) < 2:
        return ms
    gap = max(m["R"] + m["t"] / 2 for m in ms)
    n = len(ms)
    best = [(1, ms[i]["score"], -1) for i in range(n)]
    for j in range(n):
        for i in range(j):
            if ms[j]["cc"] - ms[i]["cc"] < 1:
                continue
            cand = (best[i][0] + 1, best[i][1] + ms[j]["score"], i)
            if cand[:2] > best[j][:2] and _joined(line_mask, ms[i], ms[j], gap) >= min_frac:
                best[j] = cand
    j = max(range(n), key=lambda k: best[k][:2])
    out = []
    while j >= 0:
        out.append(ms[j])
        j = best[j][2]
    return out[::-1]


def filled_markers(mask, size, box, exclude):
    lab, n = ndi.label(ndi.binary_opening(mask, iterations=2))
    out = []
    for i, sl in enumerate(ndi.find_objects(lab)):
        sub = lab[sl] == i + 1
        h, w = sub.shape
        if not (0.6 * size <= max(h, w) <= 1.5 * size) or not (0.75 <= w / h <= 1.33):
            continue
        r0, r1, c0, c1 = sl[0].start, sl[0].stop - 1, sl[1].start, sl[1].stop - 1
        cr, cc = (r0 + r1) / 2, (c0 + c1) / 2
        if not (box[0] < cc < box[2] and box[1] < cr < box[3]):
            continue
        if any(e[0] <= cc <= e[2] and e[1] <= cr <= e[3] for e in exclude):
            continue
        out.append({"r0": r0, "r1": r1, "c0": c0, "c1": c1, "cc": cc, "cr": cr, "centroid_r": cr,
                    "top": r0, "bot": r1, "filled": True})
    return sorted(out, key=lambda m: m["cc"])


def _outer_edge(mask, col, row, step, limit=40):
    """From a row inside the marker's outline (or its hole edge), walk outward to the outline's outer edge."""
    r = row
    k = 0
    while 0 <= r + step < mask.shape[0] and mask[r + step, col] and k < limit:
        r += step
        k += 1
    return r


def _stem(mask, col, start, step, half=3, gap=3, bridge=None, max_bridge=60):
    """Walk along a vertical stem from `start` in direction `step`; return the last row dark in `mask`.
    Where something else is drawn over the stem (dark in `bridge`), walk on for up to max_bridge rows,
    keeping the stem only if it shows again beyond."""
    r, last, miss, bridged = start, start - step, 0, 0
    H = mask.shape[0]
    while 0 <= r < H:
        sl = slice(max(0, col - half), col + half + 1)
        if mask[r, sl].any():
            last, miss, bridged = r, 0, 0
        elif bridge is not None and bridge[r, sl].any() and bridged < max_bridge:
            bridged += 1
        else:
            miss += 1
            if miss > gap:
                break
        r += step
    return last


def _run_through(mask, row, col):
    if not mask[row, col]:
        return 0
    a = b = col
    while a - 1 >= 0 and mask[row, a - 1]:
        a -= 1
    while b + 1 < mask.shape[1] and mask[row, b + 1]:
        b += 1
    return b - a + 1


def _extents(mask, row, col):
    """How far the dark run through (row, col) reaches to the left and to the right of col."""
    if not mask[row, col]:
        return 0, 0
    a = b = col
    while a - 1 >= 0 and mask[row, a - 1]:
        a -= 1
    while b + 1 < mask.shape[1] and mask[row, b + 1]:
        b += 1
    return col - a, b - col


NO_CAP = ("no cap found at the stem's end (it may run on hidden under another series): the end is widened by "
          "60 px outward")


def error_bar_end(mask, col, edge, step, stem_w, inside_other, walk=None):
    """The far end of an error bar leaving the marker's outer edge at `edge` in direction `step`
    (-1 up, +1 down): the first cap along the stem, a band of rows where the dark run reaches well
    out on both sides of the stem. Returns (row of the cap's centre or None, cap thickness, note)."""
    # the stem is followed through anything drawn over it (walk); its cap must be in its own colour
    end = _stem(mask, col, edge + step, step, bridge=walk)
    if (end - edge) * step < 6:
        return None, 0, "hidden"
    reach = 1.0 * stem_w
    band = []
    # start a few rows beyond the outline, whose own edge is wide where the stem leaves it
    r = edge + 4 * step
    while (r - end) * step <= 0:
        if inside_other(r, col):
            if band:
                break
            return float(r - step), 0, "the bar runs into a neighbouring marker; its end is read where it meets it"
        lft, rgt = _extents(mask, r, col)
        if lft >= reach and rgt >= reach:
            band.append(r)
        elif band:
            break
        r += step
    if not band:
        return float(end), 0, NO_CAP
    return (min(band) + max(band)) / 2, len(band), ""


def stem_width(mask, col, edge, step):
    """The stem's width: the narrowest dark run across it just outside the marker (a line crossing it
    only widens it)."""
    ws = []
    for k in range(4, 40):
        r = edge + step * k
        if 0 <= r < mask.shape[0]:
            lft, rgt = _extents(mask, r, int(round(col)))
            if lft or rgt:
                ws.append(lft + rgt + 1)
    return float(np.percentile(ws, 20)) if len(ws) >= 5 else 0.0


# ----------------------------------------------------------------------------
# a panel
# ----------------------------------------------------------------------------

def read_panel(image, at, y_segments, x_labels, colour, shape, size, exclude=(), drop_x_below=None,
               bars=True, thr=0.95, line_frac=None, outline=None, max_inner=0.75):
    black, ycols, xrows, xa, ya = calibrate(image, y_segments, x_labels)
    H, W = black.shape
    mask = mask_for(image, colour)
    box = (ycols[1] + 2, 0, W, xrows[0] - 2)
    ex = [(e[0] * W, e[1] * H, e[2] * W, e[3] * H) for e in exclude]
    if shape == "diamond":
        ms = filled_markers(mask, size, box, ex)
    else:
        grey = (gray(image) < 235) & ~mask if colour == "black" else None
        # markers are clipped at the x axis: below it, count the outline as present
        below = np.zeros_like(mask)
        below[xrows[0]:, :] = True
        grey = below if grey is None else (grey | below)
        ms = open_markers(mask, shape, size, box, ex, thr=thr, under_grey=grey, outline=outline, max_inner=max_inner)
        if line_frac:
            ms = chain(ms, mask | grey, line_frac)
    # grey series are drawn over the black ones: a black stem is followed through them
    walk = mask | ((gray(image) < 235) & ~mask) if colour == "black" else mask
    cal_note = f"y ticks misfit {ya.misfit_px:.1f} px, x ticks misfit {xa.misfit_px:.1f} px"
    pts = []
    for m in ms:
        col = int(round(m["cc"]))
        top, bot = m["top"], m["bot"]
        if shape == "triangle":
            # the plotted point is the triangle's centroid, where the joining lines meet (seen on the
            # overlays; the bounding box's centre lies higher, at half the inradius); 3 px are added
            # to the interval for it
            row = m["centroid_r"]
            amb = 3.0
        else:
            row = m["cr"]  # the outline's centre is the marker's centre
            amb = 0.0
        x = float(xa.value(m["cc"]))
        if drop_x_below is not None and x < drop_x_below:
            continue
        seg = ya.seg_of(row)
        y = ya.value(row)
        dpx = 2.0 + ya.misfit_px + amb
        lo, hi = ya.value(row + dpx, seg), ya.value(row - dpx, seg)
        rec = {"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [float(m["cc"]), float(row)],
               "_top": top, "_bot": bot, "_seg": seg, "_dpx": dpx}
        notes = [cal_note]
        if bars:
            others = [o for o in ms if o is not m]

            def inside_other(r, c, others=others):
                for o in others:
                    if shape == "circle":
                        if np.hypot(r - o["cr"], c - o["cc"]) <= o["R"] + o["t"] / 2:
                            return True
                    elif o["top"] <= r <= o["bot"] and abs(c - o["cc"]) <= (o["bot"] - o["top"]) / 2:
                        return True
                return False

            ws = [w for w in (stem_width(mask, m["cc"], top, -1), stem_width(mask, m["cc"], bot, +1)) if w > 0]
            sw = max(min(ws) if ws else 0.0, 3.0)
            up, up_th, up_note = error_bar_end(mask, col, top, -1, sw, inside_other, walk)
            dn, dn_th, dn_note = error_bar_end(mask, col, bot, +1, sw, inside_other, walk)
            if up is None and dn is None:
                notes.append("error bar hidden inside the marker: the SEM is at most the marker")
                up, dn = float(top), float(bot)
                up_th = dn_th = 0
            elif up is None:
                notes.append("upper end hidden in the marker: taken as the mirror of the lower end")
                up = row - (dn - row)
                up_th = dn_th
            elif dn is None:
                notes.append("lower end hidden in the marker: taken as the mirror of the upper end")
                dn = row + (row - up)
                dn_th = up_th
            for n in (up_note, dn_note):
                if n and n != "hidden":
                    notes.append(n)
            if ya.seg_of(up) != seg or ya.seg_of(dn) != seg:
                notes.append("the error bar crosses the axis break; its ends are read on their own segments")
            w_up = up_th / 2 + 1.5 + ya.misfit_px + (60 if up_note == NO_CAP else 0)
            w_dn = dn_th / 2 + 1.5 + ya.misfit_px + (60 if dn_note == NO_CAP else 0)
            rec.update({"bar_hi": ya.value(up), "bar_lo": ya.value(dn),
                        "bar_hi_outer": ya.value(up - w_up), "bar_lo_outer": ya.value(dn + w_dn),
                        "px_lo": float(up), "px_hi": float(dn)})
        rec["note"] = "; ".join(notes)
        pts.append(rec)
    if not at:
        return [{k: v for k, v in p.items() if not k.startswith("_")} for p in pts]
    return _interpolate(pts, at, xa, ya, cal_note)


def _interpolate(pts, at, xa, ya, cal_note):
    """Read the line joining the markers at the given forces (the polyline drawn between marker centres)."""
    out = []
    xs = [p["px"][0] for p in pts]
    for x in at:
        col = float(xa.px(x))
        i = next((k for k in range(len(xs) - 1) if xs[k] <= col <= xs[k + 1]), None)
        if i is None:
            out.append({"x": x, "y": None, "note": "outside the markers' range"})
            continue
        a, b = pts[i], pts[i + 1]
        if a["_seg"] != b["_seg"]:
            out.append({"x": x, "y": None, "note": "the joining line crosses the axis break"})
            continue
        t = (col - xs[i]) / (xs[i + 1] - xs[i])
        row = a["px"][1] + t * (b["px"][1] - a["px"][1])
        slope = (b["px"][1] - a["px"][1]) / (xs[i + 1] - xs[i])
        # the larger centre uncertainty of the two ends, and a 2-px uncertainty in the column times the slope
        dpx = max(a["_dpx"], b["_dpx"]) + 2.0 * abs(slope) + xa.misfit_px * abs(slope)
        seg = a["_seg"]
        y = ya.value(row, seg)
        lo, hi = ya.value(row + dpx, seg), ya.value(row - dpx, seg)
        out.append({"x": x, "y": y, "lo": min(lo, hi), "hi": max(lo, hi), "px": [col, row],
                    "note": f"line between markers at {a['x']:.1f} and {b['x']:.1f} pN; {cal_note}"})
    return out


def debug(image, y_segments, x_labels):
    black = mask_for(image, "black")
    ycols, xrows = find_axes(black)
    yr, ylen = y_ticks(black, ycols, xrows)
    xc = x_ticks(black, ycols, xrows)
    return {"ycols": ycols, "xrows": xrows, "y_ticks": [round(r, 1) for r in yr], "tick_len": ylen,
            "x_ticks": [round(c, 1) for c in xc]}
