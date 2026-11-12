"""Shared reading code for the figures of mohammed2015 (histograms, Tukey box plots, scatter plots).

Everything is found in the rendered crop itself; the only typed-in numbers are the printed tick labels
that each reading file passes in (and the group order it reads the boxes in).

Coordinates: pixel (row i, column j) spans [j, j+1) x [i, i+1); a run of rows a..b-1 has its centre at
(a + b) / 2. Rows grow downward.

Calibration (y, and x for histograms and scatter plots):
  the axis line is the longest dark run (vertical for y, in the left part of the crop; horizontal for
  x, in the lower part); the tick marks are the dark runs in a thin strip just outside the axis line
  (left of the y axis, below the x axis); their count must equal the number of printed labels passed in,
  matched in order (top to bottom = high to low; left to right = low to high). A least-squares line maps
  pixel to value; the misfit is the largest residual at a tick, in value units.

Colours: black = all channels < 110; red = R > 120, R - G > 70, R - B > 60; blue = B > 100, R < 90,
B - R > 50; axis ink ('dark') = mean of the channels < 130.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage


# ----------------------------------------------------------------------------- masks
def masks(image):
    a = np.asarray(image, float)[..., :3]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return {
        "black": (r < 110) & (g < 110) & (b < 110),
        "red": (r > 120) & (r - g > 70) & (r - b > 60),
        "blue": (b > 100) & (r < 90) & (b - r > 50),
        # ink of any colour, for the axis lines and ticks (grey-tinted in the JPEG figures; bars sit on
        # the x axis line and tint it)
        "dark": (r + g + b) / 3 < 130,
    }


def soft_masks(image):
    """Tints, for bars only a few pixels tall: reddish (R - G > 20, R > 60: pink above, dark red where
    the bar blends into the black axis line) or grey (mean < 200, channels within 30)."""
    a = np.asarray(image, float)[..., :3]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return {"red": (r - g > 20) & (r > 60),
            "black": (a.mean(axis=2) < 200) & (np.abs(r - g) < 30) & (np.abs(g - b) < 30)}


def runs(v):
    """(start, stop) of the True runs of a 1-D boolean array."""
    v = np.asarray(v, bool).astype(np.int8)
    d = np.diff(np.concatenate([[0], v, [0]]))
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))


def _longest(v):
    rs = runs(v)
    return max(rs, key=lambda r: r[1] - r[0]) if rs else (0, 0)


# ----------------------------------------------------------------------------- calibration
class Cal:
    def __init__(self, pix, vals, label):
        pix, vals = np.asarray(pix, float), np.asarray(vals, float)
        self.b, self.a = np.polyfit(pix, vals, 1)
        self.misfit = float(np.max(np.abs(self.a + self.b * pix - vals))) if len(pix) > 2 else 0.0
        self.per_px = abs(self.b)
        self.ticks = list(zip(pix.tolist(), vals.tolist()))
        self.label = label

    def __call__(self, p):
        return float(self.a + self.b * p)

    def note(self):
        return (f"{self.label}: {len(self.ticks)} ticks, {self.per_px:.4g} per px, "
                f"misfit {self.misfit:.3g}")


def y_axis(dark, labels, left_frac=0.45, strip=(10, 3), min_len_frac=0.3):
    """The y axis: its column run (c0, c1), the row extent, and the calibration on its ticks."""
    h, w = dark.shape
    best = None
    for c in range(int(w * left_frac)):
        a, b = _longest(dark[:, c])
        if b - a >= min_len_frac * h and (best is None or b - a > best[2] - best[1] + 2):
            best = (c, a, b)
    if best is None:
        raise ValueError("no y axis line found")
    # the axis line: neighbouring columns with (nearly) the same long run
    c = best[0]
    L = best[2] - best[1]
    c0 = c
    while c0 - 1 >= 0 and _len(dark[:, c0 - 1]) >= 0.9 * L:
        c0 -= 1
    c1 = c
    while c1 + 1 < w and _len(dark[:, c1 + 1]) >= 0.9 * L:
        c1 += 1
    c1 += 1
    s = dark[:, max(c0 - strip[0], 0):c0 - strip[1]]
    tick_rows = s.mean(axis=1) > 0.6
    ticks = [(a + b) / 2 for a, b in runs(tick_rows)
             if b - a >= 2 and best[1] - 8 <= (a + b) / 2 <= best[2] + 8]  # along the axis line only
    vals = sorted((float(v) for v in labels), reverse=True)
    if len(ticks) != len(vals):
        raise ValueError(f"y axis: found {len(ticks)} ticks at rows {ticks}, expected {len(vals)} labels")
    return (c0, c1), (best[1], best[2]), Cal(ticks, vals, "y")


def _len(v):
    a, b = _longest(v)
    return b - a


def x_axis(dark, labels, ycols, low_frac=0.4, strip=(3, 10), min_len_frac=0.3, origin_tick=False):
    """The x axis: its row run (r0, r1) and the calibration on its ticks (labels may be None).
    With origin_tick, the first label's tick sits under the y axis line (the axes cross at it)."""
    h, w = dark.shape
    best = None
    for r in range(int(h * low_frac), h):
        a, b = _longest(dark[r, :])
        if b - a >= min_len_frac * w and (best is None or b - a > best[2] - best[1] + 2):
            best = (r, a, b)
    if best is None:
        raise ValueError("no x axis line found")
    r = best[0]
    L = best[2] - best[1]
    r0 = r
    while r0 - 1 >= 0 and _len(dark[r0 - 1, :]) >= 0.9 * L:
        r0 -= 1
    r1 = r
    while r1 + 1 < h and _len(dark[r1 + 1, :]) >= 0.9 * L:
        r1 += 1
    r1 += 1
    if labels is None:
        return (r0, r1), (best[1], best[2]), None
    s = dark[r1 + strip[0]:r1 + strip[1], :]
    cols = s.mean(axis=0) > 0.6
    if not origin_tick:
        cols[:ycols[1] + 2] = False  # not the y axis line itself
    ticks = [(a + b) / 2 for a, b in runs(cols)
             if b - a >= 2 and best[1] - 8 <= (a + b) / 2 <= best[2] + 8]  # along the axis line only
    vals = [float(v) for v in labels]
    if len(ticks) != len(vals):
        raise ValueError(f"x axis: found {len(ticks)} ticks at columns {ticks}, expected {len(vals)} labels")
    return (r0, r1), (best[1], best[2]), Cal(ticks, vals, "x")


# ----------------------------------------------------------------------------- histograms
def histogram(image, at, ylabels, xlabels, color, side):
    """Bars of one colour beside each x tick: side 'left' (bar ends at the tick) or 'right' (starts there).

    A bar's value is its top edge (first coloured row going up from the x axis line, over the middle half
    of the bar's columns; the colour thresholds sit near the middle of the JPEG edge). Interval: +-(the
    blur at the edge, at least 2.5 px, + 1.5 px) + y misfit, the blur being the rows of intermediate grey
    just above the edge. A bin with no coloured column run of at least 3 px
    above the axis line is read as 0, with an interval up to 3 px."""
    m = masks(image)
    dark = m["dark"]
    ycols, _, ycal = y_axis(dark, ylabels)
    xrows, _, xcal = x_axis(dark, xlabels, ycols)
    col = m[color]
    gray = np.asarray(image, float)[..., :3].mean(axis=2)
    ticks = [t for t, _ in xcal.ticks]
    pitch = float(np.median(np.diff(ticks)))
    top_axis = xrows[0]
    out = []
    for x in at:
        hit = [t for t, v in xcal.ticks if abs(v - float(x)) < 1e-9 * max(1.0, abs(float(x)))]
        if not hit:
            out.append({"x": x, "y": None, "note": "no printed tick label at this x"})
            continue
        t = hit[0]  # the tick matched to this printed label
        c0, c1 = (int(t - 0.5 * pitch), int(t)) if side == "left" else (int(t) + 1, int(t + 0.5 * pitch))
        c0 = max(c0, ycols[1] + 3)  # never the y axis line
        heights = []
        for c in range(c0, c1):
            k = 0
            r = top_axis - 1
            while r >= 0 and col[r, c]:
                k += 1
                r -= 1
            heights.append(k)
        heights = np.array(heights)
        bar = np.flatnonzero(heights >= 3)
        y0 = ycal(top_axis)  # the axis line's top edge, for reference only
        if len(bar) < 3:
            # a faint bar: a few rows tinted by the JPEG blend, too thin for the strict colour
            soft = soft_masks(image)[color]
            sh = []
            for c in range(c0, c1):
                k, r = 0, top_axis - 1
                while r >= 0 and soft[r, c]:
                    k += 1
                    r -= 1
                sh.append(k)
            sh = np.array(sh)
            fb = np.flatnonzero(sh >= 3)
            if len(fb) >= max(8, 0.15 * (c1 - c0)):  # wider than the ringing beside an axis line
                edge = float(np.median(top_axis - sh[fb]))
                lo, hi = sorted([ycal(edge - 4), ycal(top_axis)])
                out.append({"x": x, "y": ycal(edge), "lo": lo - ycal.misfit, "hi": hi + ycal.misfit,
                            "px": [float(c0 + (fb[0] + fb[-1] + 1) / 2), edge],
                            "note": f"faint {color} bar (only its JPEG tint above the axis line), columns "
                                    f"{c0 + fb[0]}-{c0 + fb[-1] + 1}, tinted top row {edge:.1f}; interval from "
                                    f"the axis line top to 4 px above the tint; {ycal.note()}"})
                continue
            hi = ycal(ycal_row(ycal, 0.0) - 3)
            out.append({"x": x, "y": 0.0, "lo": 0.0, "hi": max(hi, 0.0) + ycal.misfit,
                        "px": [float(t + (-0.25 if side == 'left' else 0.25) * pitch), float(ycal_row(ycal, 0.0))],
                        "note": f"no {color} bar visible: read as 0 (axis line top at {y0:.3g}); {ycal.note()}"})
            continue
        a, b = bar[0], bar[-1] + 1
        mid = bar[(bar >= a + (b - a) // 4) & (bar < b - (b - a) // 4)]
        if len(mid) == 0:
            mid = bar
        tops = top_axis - heights[mid]  # first coloured row
        edge = float(np.median(tops))
        cc = int(c0 + mid[len(mid) // 2])
        # blur: intermediate grey rows just above the edge
        e = int(edge)
        blur = 0
        for r in range(e - 1, max(e - 15, 0), -1):
            if 60 < gray[r, cc] < 235:
                blur += 1
            else:
                break
        hw = max(blur, 2.5) + 1.5  # at least the JPEG source's own pixel (about 2 render px) either side
        y = ycal(edge)
        lo, hi = sorted([ycal(edge - hw), ycal(edge + hw)])
        out.append({"x": x, "y": y, "lo": lo - ycal.misfit, "hi": hi + ycal.misfit,
                     "px": [float(c0 + (a + b) / 2), edge],
                     "note": f"{color} bar columns {c0 + a}-{c0 + b}, top edge row {edge:.1f}, blur {blur} px "
                             f"(+-{hw:.1f} px); {ycal.note()}"})
    return out


def ycal_row(cal, v):
    return (v - cal.a) / cal.b


# ----------------------------------------------------------------------------- box plots
def boxes(image, color, ylabels, min_height_frac=0.05):
    """Every box of one colour, left to right: the box's three wide lines (top, median, bottom) and its
    whisker ends. A box is a connected component of that colour with at least 3 groups of rows whose
    run through the component is >= 85% of the component's widest row run (the box edges)."""
    m = masks(image)
    dark = m["dark"]
    ycols, yrows, ycal = y_axis(dark, ylabels)
    xrows, _, _ = x_axis(dark, None, ycols)
    mask = m[color].copy()
    mask[:, :ycols[1] + 3] = False
    mask[xrows[0] - 2:, :] = False
    top_tick = min(t for t, _ in ycal.ticks)
    mask[:max(int(top_tick) - 20, 0), :] = False  # above the axis's top tick: legends, not data
    # group on a slightly dilated mask: a JPEG gap of a few pixels can cut the median line off the box
    lab, n = ndimage.label(ndimage.binary_dilation(mask, structure=np.ones((7, 7), bool)))
    found = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        comp = (lab[sl] == i) & mask[sl]
        hh = comp.shape[0]
        if hh < min_height_frac * mask.shape[0]:
            continue
        # rows as runs after closing horizontal JPEG gaps of up to 6 px
        closed = ndimage.binary_closing(comp, structure=np.ones((1, 7), bool)) | comp
        widths = np.array([_len(closed[r]) for r in range(hh)])
        W = widths.max()
        wide = widths >= 0.75 * W
        wide = ndimage.binary_closing(wide, structure=np.ones(5, bool)) | wide  # rejoin a split line
        groups = []
        for a, b in runs(wide):  # widen each line over its blurred rows (still >= 0.6 of the width)
            while a - 1 >= 0 and widths[a - 1] >= 0.6 * W:
                a -= 1
            while b < hh and widths[b] >= 0.6 * W:
                b += 1
            if not groups or a > groups[-1][1]:
                groups.append((a, b))
        if len(groups) < 2:
            continue
        # the box: two wide lines spanning the box's columns, joined by its two sides
        rw = int(np.argmax(widths))
        lft, rgt = _longest(closed[rw])
        ext = [_longest(closed[(a + b) // 2]) for a, b in groups]
        tol = max(15, 0.2 * W)  # a JPEG break can shorten one end of a line
        aligned = [i for i, (l, r) in enumerate(ext) if abs(l - lft) <= tol and abs(r - rgt) <= tol]
        best = None
        for ii, i in enumerate(aligned):
            for j in aligned[ii + 1:]:
                rows_between = range(groups[i][1], groups[j][0])
                if len(rows_between) == 0:
                    continue
                sides = []
                for lo_c, hi_c in ((max(lft - 5, 0), lft + 25), (max(rgt - 25, 0), rgt + 5)):
                    s = closed[groups[i][1]:groups[j][0], lo_c:hi_c].any(axis=1)
                    s = s.copy()
                    for ga, gb in runs(~s):  # bridge JPEG dropouts of up to 24 rows in a side
                        if gb - ga <= 24:
                            s[ga:gb] = True
                    sides.append(s)
                ok = float(np.mean(sides[0] & sides[1]))
                # a box is hollow: away from its sides, its centre line and its inner lines, little is marked
                inner_rows = [q for q in rows_between if not any(a <= q < b for a, b in groups)]
                cols = np.r_[lft + 30:(lft + rgt) // 2 - 15, (lft + rgt) // 2 + 15:rgt - 30]
                fill = closed[np.ix_(inner_rows, cols)].mean() if inner_rows and len(cols) else 0.0
                if ok >= 0.9 and fill < 0.2 and (best is None or groups[j][1] - groups[i][0] > best[2]):
                    best = (i, j, groups[j][1] - groups[i][0])
        if best is None:
            continue
        found.append((sl, comp, widths, W, groups, best))
    found.sort(key=lambda f: f[0][1].start)
    if found:  # boxes of one panel share a width: narrower hollow shapes are letters of the panel's text
        wmax = max(f[3] for f in found)
        found = [f for f in found if f[3] >= 0.6 * wmax]
    res = []
    for sl, comp, widths, W, groups, (i, j, _) in found:
        r_off, c_off = sl[0].start, sl[1].start
        top, bot = groups[i], groups[j]
        inner = groups[i + 1:j]
        note_g = ""
        if not inner:
            med = None
            note_g = "no median line inside the box (it coincides with an edge)"
        else:
            med = max(inner, key=lambda g: widths[g[0]:g[1]].mean())
            if len(inner) > 1:
                note_g = f"{len(inner)} wide lines inside the box: the widest taken as the median"
        # box columns: the widest run in the box's top edge
        trow = (top[0] + top[1]) // 2
        bc = _longest(comp[trow])
        # the whisker column: most marked pixels outside the box, within the box's columns
        outside = np.concatenate([comp[:top[0]], comp[bot[1]:]]).sum(axis=0).astype(float)
        sm = np.convolve(outside, np.ones(9) / 9, mode="same")
        cc = int(bc[0] + np.argmax(sm[bc[0]:bc[1]])) if sm[bc[0]:bc[1]].max() > 0 else (bc[0] + bc[1]) // 2
        thick = float(np.median([g[1] - g[0] for g in (top, med, bot) if g is not None]))
        feats = {}
        for name, g in (("q75", top), ("median", med), ("q25", bot)):
            feats[name] = None if g is None else (r_off + (g[0] + g[1]) / 2, (g[1] - g[0]) / 2, "")
        # whiskers: walk outward along the box centre column from each box edge
        for name, start, step in (("whisker_hi", top[0] - 1, -1), ("whisker_lo", bot[1], 1)):
            rows = []
            r = start
            band = comp[:, max(cc - 4, 0):cc + 5].any(axis=1)
            while 0 <= r < comp.shape[0]:
                if band[r]:
                    rows.append(r)
                elif not any(0 <= r + k * step < comp.shape[0] and band[r + k * step] for k in range(1, 7)):
                    break  # a gap longer than a JPEG dropout: the whisker has ended
                r += step
            if not rows:
                feats[name] = None
                continue
            # cap rows: many marked pixels across the box width (pixel count, so JPEG breaks in the cap
            # do not split it); a single outlier marker is narrower than 0.4 of the box width
            capw = np.array([comp[rr, max(cc - W // 2, 0):cc + W // 2 + 1].sum() for rr in rows])
            # rows still wide right at the box edge are the edge line's own blurred side, not a cap
            k0 = 0
            while k0 < len(rows) and capw[k0] >= 0.4 * W:
                k0 += 1
            rows, capw = rows[k0:], capw[k0:]
            if not rows:
                feats[name] = None
                continue
            cap = np.array(rows)[capw >= 0.4 * W]
            if len(cap):
                # the cap: the group of wide rows nearest the box end of the walk... the outermost group
                grs = runs(np.isin(np.array(rows), cap))
                ga, gb = grs[-1]
                cr = np.array(rows)[ga:gb]
                feats[name] = (r_off + (cr.min() + cr.max() + 1) / 2, (cr.max() + 1 - cr.min()) / 2,
                               f"whisker cap rows {r_off + cr.min()}-{r_off + cr.max()}"
                               + ("; rows beyond the cap belong to an outlier touching it" if gb < len(rows) else ""))
            else:
                end = rows[-1] + (0 if step < 0 else 1)
                feats[name] = (r_off + end, thick / 2, "no cap found: the end of the whisker line")
        res.append({"col": c_off + cc, "W": W, "feats": feats, "note": note_g})
    return res, ycal


def _len_through(row, c):
    for a, b in runs(row):
        if a <= c < b:
            return b - a
    return 0


def read_boxes(image, at, color_ranks, stat, ylabels):
    """Read statistic `stat` (median, q25, q75, whisker_lo, whisker_hi) of the boxes: at[i] -> (colour,
    rank of the box among that colour's boxes, left to right). Interval +-(half the line thickness +
    1 px) + misfit."""
    cache = {}
    out = []
    for x in at:
        key = str(int(round(float(x))))
        color, rank = color_ranks[key]
        if color not in cache:
            cache[color] = boxes(image, color, ylabels)
        bl, ycal = cache[color]
        if rank >= len(bl):
            out.append({"x": x, "y": None, "note": f"only {len(bl)} {color} boxes found"})
            continue
        bx = bl[rank]
        f = bx["feats"].get(stat)
        if f is None:
            out.append({"x": x, "y": None, "note": f"no {stat} found for {color} box {rank + 1}"})
            continue
        row, half, note = f
        y = ycal(row)
        a, b = sorted([ycal(row - half - 1), ycal(row + half + 1)])
        out.append({"x": x, "y": y, "lo": a - ycal.misfit, "hi": b + ycal.misfit,
                    "px": [float(bx["col"]), float(row)],
                    "note": "; ".join(s for s in (f"{color} box {rank + 1}, {stat} at row {row:.1f}", note,
                                                  bx["note"], ycal.note()) if s)})
    return out


STAT_ORDER = {1: "whisker_lo", 2: "q25", 3: "median", 4: "q75", 5: "whisker_hi"}


def read_box_stats(image, at, color, rank, ylabels):
    """Every statistic of one box: at[i] = 1 lower whisker end, 2 Q1, 3 median, 4 Q3, 5 upper whisker end."""
    out = []
    for x in at:
        r = read_boxes(image, [1.0], {"1": (color, rank)}, STAT_ORDER[int(round(float(x)))], ylabels)[0]
        r["x"] = x
        out.append(r)
    return out


# ----------------------------------------------------------------------------- scatter plots
def scatter(image, xlabels, ylabels, color="black", cover=0.97):
    """Filled round markers of one colour, overlapping ones separated by fitting discs.

    The marker radius R is the median equivalent radius of the isolated components (those not much
    larger than the smallest common size). Each component is covered greedily by discs of radius R
    whose centres lie where a disc of radius 0.85 R fits inside the component (distance transform),
    each new disc the one covering most uncovered pixels, until `cover` of the component is covered.
    Thin things (axis lines, ticks, letters, the regression line) hold no such centre and are skipped.
    Interval: +-(1 px + misfit) for an isolated marker, +-(0.25 R + misfit) for one inside a cluster."""
    m = masks(image)
    dark = m["dark"]
    ycols, _, ycal = y_axis(dark, ylabels)
    xrows, _, xcal = x_axis(dark, xlabels, ycols, origin_tick=True)
    mask = m[color].copy()
    mask = ndimage.binary_closing(mask, structure=np.ones((5, 5), bool))  # heal the regression line crossing
    mask[:, :ycols[1] + 2] = False
    mask[xrows[0] - 1:, :] = False
    dist = ndimage.distance_transform_edt(mask)
    lab, n = ndimage.label(mask)
    objs = ndimage.find_objects(lab)
    # marker radius from compact components (max distance ~ equivalent radius)
    cand = []
    for i, sl in enumerate(objs, start=1):
        comp = lab[sl] == i
        area = comp.sum()
        dmax = dist[sl][comp].max()
        req = np.sqrt(area / np.pi)
        if dmax > 6 and dmax > 0.8 * req:
            cand.append(req)
    if not cand:
        raise ValueError("no round markers found")
    R = float(np.median(cand))
    pts = []
    for i, sl in enumerate(objs, start=1):
        comp = lab[sl] == i
        d = dist[sl] * comp
        if d.max() < 0.85 * R:
            continue
        cy, cx = np.nonzero(d >= 0.85 * R)
        uncovered = comp.copy()
        total = comp.sum()
        yy, xx = np.mgrid[0:comp.shape[0], 0:comp.shape[1]]
        centres = []
        step = max(1, int(R / 8))
        sel = (cy % step == 0) & (cx % step == 0)
        cy, cx = cy[sel], cx[sel]
        while uncovered.sum() > (1 - cover) * total and len(centres) < 50:
            best, bscore = None, 0
            for y0, x0 in zip(cy, cx):
                y_lo, y_hi = max(int(y0 - R), 0), int(y0 + R) + 1
                x_lo, x_hi = max(int(x0 - R), 0), int(x0 + R) + 1
                sub = uncovered[y_lo:y_hi, x_lo:x_hi]
                disk = (yy[y_lo:y_hi, x_lo:x_hi] - y0) ** 2 + (xx[y_lo:y_hi, x_lo:x_hi] - x0) ** 2 <= R * R
                s = int((sub & disk).sum())
                if s > bscore:
                    best, bscore = (y0, x0), s
            if best is None or bscore < 0.25 * np.pi * R * R:
                break
            centres.append(best)
            uncovered &= (yy - best[0]) ** 2 + (xx - best[1]) ** 2 > R * R
        single = len(centres) == 1
        for (y0, x0) in centres:
            if single:  # an isolated marker: its centroid
                rr, cc = np.nonzero(comp)
                y0, x0 = rr.mean(), cc.mean()
            row, coln = sl[0].start + y0 + 0.5, sl[1].start + x0 + 0.5
            hp = 1.0 if single else 0.25 * R
            pts.append({"row": row, "col": coln, "hp": hp, "n": len(centres)})
    pts.sort(key=lambda p: (p["col"], p["row"]))
    out = []
    for p in pts:
        x, y = xcal(p["col"]), ycal(p["row"])
        a, b = sorted([ycal(p["row"] - p["hp"]), ycal(p["row"] + p["hp"])])
        out.append({"x": x, "y": y, "lo": a - ycal.misfit, "hi": b + ycal.misfit,
                    "px": [p["col"], p["row"]],
                    "note": (f"marker radius {R:.1f} px; " + ("isolated marker" if p["n"] == 1 else
                             f"one of {p['n']} overlapping markers, separated by disc fitting")
                             + f"; x +-{p['hp'] * xcal.per_px + xcal.misfit:.3g}; {xcal.note()}; {ycal.note()}")})
    return out
