"""Shared reading code for the plotted panels of shyer2013 (Figs. 2, 3, 4B, 6C, S3, S6).

Each reading file holds a CONFIG and calls one of the readers below. Everything is found in the
rendered crop:

* the plot box: the longest dark, unsaturated lines (the spines);
* the axes: the inward tick marks on the bottom spine (x) and on the left or right spine (y),
  matched in order to the printed tick labels given in CONFIG; a label printed at a spine (the
  MATLAB axes put 0, and sometimes the top value, at the box corner) is matched to that spine;
  value = a + b * pixel is fitted through them and its largest misfit (px) is carried into every
  interval;
* markers: a colour mask (CONFIG 'color'); filled markers are what survives a morphological opening
  of the mask with a disc (lines and error bars are thinner), open markers are the enclosed holes of
  the mask (merged when a line through the marker splits the hole); a marker's position is its
  bounding-box centre (MATLAB centres a marker, triangles included, on its bounding box);
* error bars: walked along the marker's column in the colour mask from the marker's edge, outward,
  bridging small gaps, stopping where another marker of the panel begins;
* bars (bar charts): the columns of the bar-fill colour; a bar's top is the topmost fill row in its
  central columns; its error bar is walked upward (and downward inside the bar where visible) in the
  error-bar ink mask;
* lines (the dotted stress-free lines, the fitted 'Numerics' curves): the colour mask in a narrow
  column band at each requested x, its centre row and its thickness.
"""
import numpy as np
from scipy import ndimage as ndi


# ---------------------------------------------------------------- masks
def _rgb(image):
    return np.asarray(image, dtype=float)[..., :3]


def dark_mask(image, cfg):
    a = _rgb(image)
    g = a.mean(axis=2)
    chroma = a.max(axis=2) - a.min(axis=2)
    return (g < cfg.get("dark", 170)) & (chroma < cfg.get("dark_chroma", 80))


COLORS = {
    # name: test on r, g, b arrays (0..255)
    "red": lambda r, g, b: (r > 170) & (g < 140) & (b < 140) & (r - g > 70),
    "blue": lambda r, g, b: (b > 120) & (r < 130) & (b - r > 50) & (b - g > 30),
    "purple": lambda r, g, b: (r > 90) & (b > 90) & (g < 90) & (abs(r - b) < 80),
    "green": lambda r, g, b: (g > 110) & (r < 120) & (g - r > 40) & (g - b > 15),
    "cyan": lambda r, g, b: (b > 170) & (g > 170) & (r < 190) & (b - r > 25) & (g - r > 25),
    "blue2": lambda r, g, b: (b > 150) & (b - r > 25) & (b - g > 25),
    "green2": lambda r, g, b: (g > 90) & (g - r > 25) & (g - b > 10),
    "lightblue": lambda r, g, b: (b - r > 12) & (b > 190) & (g < b - 5),
    "pink": lambda r, g, b: (r > 225) & (r - g > 40) & (r - g < 130) & (abs(g - b) < 30),
    "olive": lambda r, g, b: (g > 90) & (r < 140) & (b < 120) & (g - b > 20),
    "dark": None,
}


def color_mask(image, name, cfg=None):
    if name == "dark":
        return dark_mask(image, cfg or {})
    a = _rgb(image)
    return COLORS[name](a[..., 0], a[..., 1], a[..., 2])


# ---------------------------------------------------------------- axes
def _runs(v):
    out, start = [], None
    for i, b in enumerate(list(v) + [False]):
        if b and start is None:
            start = i
        elif not b and start is not None:
            out.append((start, i))
            start = None
    return out


def _groups(xs):
    xs = list(xs)
    if not xs:
        return []
    out, cur = [], [xs[0]]
    for x in xs[1:]:
        if x - cur[-1] <= 2:
            cur.append(x)
        else:
            out.append(cur)
            cur = [x]
    out.append(cur)
    return [(c[0], c[-1]) for c in out]


def _longest(v):
    return max([e - s for s, e in _runs(v)] or [0])


def find_box(dark, cfg):
    H, W = dark.shape
    fr = cfg.get("spine_frac", 0.45)
    rows = [r for r in range(H) if _longest(dark[r]) > fr * W]
    cols = [c for c in range(W) if _longest(dark[:, c]) > fr * H]
    hg, vg = _groups(rows), _groups(cols)
    if len(hg) < 1 or len(vg) < 1:
        raise ValueError(f"spines not found: rows {hg}, cols {vg}")
    bottom = hg[-1]
    top = hg[0] if len(hg) > 1 else None
    left = vg[0]
    right = vg[-1] if len(vg) > 1 else None
    return {"top": top, "bottom": bottom, "left": left, "right": right}


def _tick_runs(dark, spine, along, side, span, mn, mx):
    lo, hi = span
    found = []
    for p in range(lo, hi):
        if along == "row":
            col = dark[:, p]
            seq = col[:spine[0]][::-1] if side < 0 else col[spine[1] + 1:]
        else:
            row = dark[p, :]
            seq = row[spine[1] + 1:] if side > 0 else row[:spine[0]][::-1]
        k = 0
        while k < 3 and k < len(seq) and not seq[k]:
            k += 1
        n = 0
        while k + n < len(seq) and seq[k + n]:
            n += 1
        found.append(n if mn <= n <= mx else 0)
    found = np.array(found)
    return [lo + (s + e - 1) / 2 + 0.5 for s, e in _runs(found > 0) if e - s <= 25]


def _fit(pix, vals):
    p, v = np.array(pix, float), np.array(vals, float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs(p - (v - a) / b)))
    return a, b, max(mis, 0.5)


def calibrate(image, cfg):
    """Returns dict with x (a, b, misfit), y (a, b, misfit) and the box."""
    dark = dark_mask(image, cfg)
    box = find_box(dark, cfg)
    H, W = dark.shape
    mn, mx = cfg.get("tick_len", (6, 45))
    left_in = box["left"][1] + 4
    right_in = (box["right"][0] - 4) if box["right"] else W - 2
    top_in = (box["top"][1] + 4) if box["top"] else 2
    bot_in = box["bottom"][0] - 4
    # x ticks: inward (upward) from the bottom spine
    xl = cfg["x_labels"]
    if xl.get("spine", "bottom") == "bottom":
        xt = _tick_runs(dark, box["bottom"], "row", -1, (left_in, right_in), mn, mx)
    else:  # the mirrored ticks hanging from the top spine
        xt = _tick_runs(dark, box["top"], "row", +1, (left_in, right_in), mn, mx)
    xpix = xt[xl.get("skip", 0):xl.get("skip", 0) + len(xl["values"])]
    if len(xpix) != len(xl["values"]):
        raise ValueError(f"x ticks found at {xt}, labels {xl['values']}")
    if "at_left" in xl or "at_right" in xl:     # labels printed at the box corners
        xpix, xvals = list(xpix), list(xl["values"])
        if "at_left" in xl:
            xpix.append((box["left"][0] + box["left"][1]) / 2 + 0.5)
            xvals.append(xl["at_left"])
        if "at_right" in xl and box["right"]:
            xpix.append((box["right"][0] + box["right"][1]) / 2 + 0.5)
            xvals.append(xl["at_right"])
        xa, xb, xm = _fit(xpix, xvals)
    elif len(xpix) == 1:
        # one labelled position (one category): no x scale; one box width is taken as one x unit, so
        # a marker is matched to the tick within x_tol box widths
        xb = 1.0 / (right_in - left_in)
        xa, xm = xl["values"][0] - xb * xpix[0], 0.5
    else:
        xa, xb, xm = _fit(xpix, xl["values"])
    # y ticks: inward from the chosen spine
    yl = cfg["y_labels"]
    tick_ink = dark
    if yl.get("tick_color"):  # a coloured second axis (e.g. the purple ratio axis)
        tick_ink = color_mask(image, yl["tick_color"], cfg)
    if yl.get("axis", "left") == "left":
        yt = _tick_runs(tick_ink, box["left"], "col", +1, (top_in, bot_in), mn, mx)
    else:
        yt = _tick_runs(tick_ink, box["right"], "col", -1, (top_in, bot_in), mn, mx)
    yt = sorted(yt, reverse=True)  # bottom first
    ypix = list(yt[yl.get("skip", 0):yl.get("skip", 0) + len(yl["values"])])
    yvals = list(yl["values"])
    if len(ypix) != len(yvals):
        raise ValueError(f"y ticks found at {yt}, labels {yvals}")
    if "at_bottom" in yl:
        ypix.append((box["bottom"][0] + box["bottom"][1]) / 2 + 0.5)
        yvals.append(yl["at_bottom"])
    if "at_top" in yl and box["top"]:
        ypix.append((box["top"][0] + box["top"][1]) / 2 + 0.5)
        yvals.append(yl["at_top"])
    ya, yb, ym = _fit(ypix, yvals)
    return {"x": (xa, xb, xm), "y": (ya, yb, ym), "box": box, "xticks": xpix, "yticks": ypix}


# ---------------------------------------------------------------- markers
def _disk(r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def _conv_rings(mask, cfg):
    """Open markers in a blurred raster: peaks of (ink fraction on a ring) - (ink fraction inside it),
    by correlation with a circular or square ring template of the marker's size."""
    from scipy.signal import fftconvolve
    r_in, r_out = cfg.get("ring_r", (11, 17))
    yy, xx = np.mgrid[-r_out:r_out + 1, -r_out:r_out + 1]
    rr = np.maximum(abs(xx), abs(yy)) if cfg.get("ring_shape") == "square" else np.sqrt(xx * xx + yy * yy)
    ring = ((rr >= r_in) & (rr <= r_out)).astype(float)
    inner = (rr <= 0.5 * r_in).astype(float)
    m = mask.astype(float)
    fr = fftconvolve(m, ring[::-1, ::-1], mode="same") / ring.sum()
    fi = fftconvolve(m, inner[::-1, ::-1], mode="same") / inner.sum()
    score = np.where(fi < cfg.get("inner_max", 0.35), fr - fi, 0)
    ok = score > cfg.get("ring_thr", 0.45)
    peak = ndi.maximum_filter(score, size=int(1.5 * r_out)) == score
    lab, n = ndi.label(ok & peak)
    out = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        c, r = xs.mean() + 0.5, ys.mean() + 0.5
        out.append((c, r, "open", (c - r_out, r - r_out, c + r_out, r + r_out)))
    # one marker, one point
    out.sort()
    merged = []
    for o in out:
        if merged and abs(o[0] - merged[-1][0]) < r_out and abs(o[1] - merged[-1][1]) < r_out:
            continue
        merged.append(o)
    return merged


def find_markers(mask, cfg, box):
    """Filled and open markers of one colour: list of (col, row, kind, bbox)."""
    out = []
    r_open = cfg.get("r_open", 8)
    filled = ndi.binary_opening(mask, structure=_disk(r_open))
    lab, n = ndi.label(filled)
    for k, sl in enumerate(ndi.find_objects(lab), start=1):
        rr, cc = sl
        h, w = rr.stop - rr.start, cc.stop - cc.start
        if h > 1.4 * w and cfg.get("tall") in ("lower", "upper"):
            # two markers of one colour drawn over each other in a column: keep one marker's height
            # at the named end of the blob
            rr = slice(rr.stop - w, rr.stop) if cfg["tall"] == "lower" else slice(rr.start, rr.start + w)
            h = w
        if min(h, w) < cfg.get("min_filled", 14) or max(h, w) > cfg.get("max_marker", 40) + 10:
            continue
        if cfg.get("shape") == "tri_down":
            # the opening rounds off the lower tip by about r_open; the centre is taken half-way between
            # the bounding-box centre (h/2) and the circumcentre (h/3 below the flat top)
            bot = rr.stop + r_open
            out.append(((cc.start + cc.stop) / 2, rr.start + 5 * (bot - rr.start) / 12, "filled",
                        (cc.start, rr.start, cc.stop, bot)))
            continue
        out.append(((cc.start + cc.stop) / 2, (rr.start + rr.stop) / 2, "filled", (cc.start, rr.start, cc.stop, rr.stop)))
    if cfg.get("ring_conv"):
        out += _conv_rings(mask, cfg)
        c0, c1 = box["left"][1], (box["right"][0] if box["right"] else 10 ** 9)
        r0 = box["top"][1] if box["top"] else -1
        return [m for m in out if c0 < m[0] < c1 and r0 < m[1] < box["bottom"][0] + cfg.get("below", 0)]
    closed = ndi.binary_closing(mask, structure=_disk(cfg.get("close", 1)))
    holes = ndi.binary_fill_holes(closed) & ~closed
    lab, n = ndi.label(holes)
    objs = []
    for k, sl in enumerate(ndi.find_objects(lab), start=1):
        rr, cc = sl
        area = int((lab[sl] == k).sum())
        if area < cfg.get("min_hole", 15) or max(rr.stop - rr.start, cc.stop - cc.start) > cfg.get("max_hole", 40):
            continue
        objs.append([cc.start, rr.start, cc.stop, rr.stop])
    # merge hole pieces split by a line through the marker
    merged = []
    for o in sorted(objs):
        for m in merged:
            if o[0] < m[2] + 6 and m[0] < o[2] + 6 and o[1] < m[3] + 8 and m[1] < o[3] + 8:
                m[:] = [min(m[0], o[0]), min(m[1], o[1]), max(m[2], o[2]), max(m[3], o[3])]
                break
        else:
            merged.append(list(o))
    ring = cfg.get("ring", 4)  # the ring's line width: the marker's outer box is the hole box plus it
    big = cfg.get("max_marker", 40)
    merged = [m for m in merged if m[2] - m[0] <= big and m[3] - m[1] <= big]  # letters merged: not markers
    for m in merged:
        bb = (m[0] - ring, m[1] - ring, m[2] + ring, m[3] + ring)
        if cfg.get("shape") == "tri_down":
            out.append(((m[0] + m[2]) / 2, m[1] + 5 * (m[3] - m[1]) / 12, "open", bb))
            continue
        out.append(((m[0] + m[2]) / 2, (m[1] + m[3]) / 2, "open", bb))
    c0, c1 = box["left"][1], (box["right"][0] if box["right"] else 10 ** 9)
    r0 = box["top"][1] if box["top"] else -1
    r1 = box["bottom"][0]
    return [m for m in out if c0 < m[0] < c1 and r0 < m[1] < r1 + cfg.get("below", 0)]


def ring_search(mask, col, cfg, box, marks):
    """Best ring-template match in the column band at `col`: returns (col, row, ring fraction) or None.
    A ring whose inside is mostly ink (a filled marker drawn over it) is not accepted."""
    r_in, r_out = cfg.get("ring_r", (11, 15))
    yy, xx = np.mgrid[-r_out:r_out + 1, -r_out:r_out + 1]
    rr = np.sqrt(xx * xx + yy * yy)
    ring = (rr >= r_in) & (rr <= r_out)
    inner = rr <= 0.5 * r_in
    top = (box["top"][1] + r_out) if box["top"] else r_out
    bot = box["bottom"][0] - 2
    best = None
    for dc in range(-4, 5):
        c = int(round(col)) + dc
        if c - r_out < 0 or c + r_out + 1 > mask.shape[1]:
            continue
        for r in range(top, bot - r_out):
            win = mask[r - r_out:r + r_out + 1, c - r_out:c + r_out + 1]
            f = win[ring].mean()
            if f < cfg.get("ring_thr", 0.6) or win[inner].mean() > 0.5:
                continue
            if best is None or f > best[2]:
                best = (c, r, float(f))
    if best is None:
        return None
    for m in marks:  # a match on a filled marker's edge is not a ring
        if m[2] == "filled" and abs(m[0] - best[0]) < 10 and abs(m[1] - best[1]) < 10:
            return None
    # refine: rows within the same score plateau
    return best


def _walk(mask, col, start, step, stop_rows, gap=4, band=3):
    c0, c1 = int(round(col)) - band, int(round(col)) + band + 1
    r, last, miss = start, None, 0
    H = mask.shape[0]
    while 0 <= r < H:
        if r in stop_rows:
            return last, True
        if mask[r, c0:c1].any():
            last, miss = r, 0
        else:
            miss += 1
            if miss > gap:
                break
        r += step
    return last, False


def read_markers(image, at, cfg):
    cal = calibrate(image, cfg)
    xa, xb, xm = cal["x"]
    ya, yb, ym = cal["y"]
    mask = color_mask(image, cfg["color"], cfg)
    marks = find_markers(mask, cfg, cal["box"])
    kind = cfg["kind"]
    tol = cfg.get("x_tol", 0.15)
    out = []
    if not at:
        # every marker of this kind and colour, x from the calibration; legend samples are excluded by
        # the layout boxes in CONFIG 'exclude' ([c0, r0, c1, r1] in crop pixels)
        def free(m):
            return not any(a0 <= m[0] <= a1 and b0 <= m[1] <= b1 for a0, b0, a1, b1 in cfg.get("exclude", []))
        sel = sorted([m for m in marks if m[2] == kind and free(m)])
        at = [xa + xb * m[0] for m in sel]
        tol = 1e-9
        marks = sel + [m for m in marks if m not in sel]
    for xv in at:
        col = (xv - xa) / xb
        cands = [m for m in marks if m[2] == kind and abs(xa + xb * m[0] - xv) < tol]
        fallback = False
        if not cands and cfg.get("fallback_kind") and xv in cfg.get("fallback_at", []):
            # an open marker so small or blurred that its hole closed reads as a filled one
            cands = [m for m in marks if m[2] == cfg["fallback_kind"] and abs(xa + xb * m[0] - xv) < tol]
            fallback = bool(cands)
        if cfg.get("pick") == "lowest":
            cands.sort(key=lambda m: -m[1])
        elif cfg.get("pick") == "highest":
            cands.sort(key=lambda m: m[1])
        else:
            cands.sort(key=lambda m: abs(m[0] - col))
        if not cands and kind == "open" and cfg.get("ring_search", True):
            hit = ring_search(mask, col, cfg, cal["box"], marks)
            if hit is not None:
                rc, rr, frac = hit
                R = cfg.get("ring_r", (11, 15))[1]
                cands = [(rc, rr, "open*", (rc - R, rr - R, rc + R, rr + R))]
        if not cands:
            out.append({"x": xv, "y": None, "note": f"no {kind} {cfg['color']} marker found within {tol} of x "
                                                     "(hidden behind another marker or not drawn)"})
            continue
        c, r, how, bb = cands[0]
        e = cfg.get("centre_px", 3.0) * (2 if how == "open*" else 1) + ym
        if cfg.get("shape") == "tri_down":
            e += (bb[3] - bb[1]) / 12   # half the spread between the two centre conventions
        y = ya + yb * r
        lo, hi = sorted([ya + yb * (r - e), ya + yb * (r + e)])
        row = {"x": xv, "y": float(y), "lo": float(lo), "hi": float(hi), "px": [float(c), float(r)],
               "note": f"{kind} {cfg['color']} marker at column {c:.0f} (x there {xa + xb * c:.2f}); "
                       f"y misfit {ym:.1f} px, x misfit {xm:.1f} px"}
        if fallback:
            row["note"] += (f"; no {kind} marker here: the {cfg['fallback_kind']} {cfg['color']} marker picked "
                            f"by rule '{cfg.get('pick', 'nearest')}' (its hole is closed in the raster)")
        if how == "open*":
            row["note"] += ("; ring partly covered by other ink (no closed hole): centre from the best ring "
                            "template match, interval doubled")
        if cfg.get("bars"):
            others_up, others_dn = set(), set()
            for m in marks:
                if m is cands[0] or abs(m[0] - c) > 25:
                    continue
                rows = set(range(int(m[3][1]) - 2, int(m[3][3]) + 3))
                (others_up if m[1] < r else others_dn).update(rows)
            # the bar may be in another ink than the marker (cfg bar_color)
            bmask = color_mask(image, cfg.get("bar_color", cfg["color"]), cfg) | mask
            up, bl_up = _walk(bmask, c, int(bb[1]) - 1, -1, others_up, gap=cfg.get("gap", 4))
            dn, bl_dn = _walk(bmask, c, int(bb[3]), +1, others_dn, gap=cfg.get("gap", 4))
            lw = cfg.get("bar_lw", 4)
            notes = []
            top = (up + 0.5 + lw / 2) if up is not None else None
            bot = (dn + 0.5 - lw / 2) if dn is not None else None
            if up is not None and up >= bb[1] - 3:
                top = None
            if dn is not None and dn <= bb[3] + 2:
                bot = None
            hid_t = top is None and not bl_up
            hid_b = bot is None and not bl_dn
            if hid_t:
                top = bb[1]
            if hid_b:
                bot = bb[3]
            if top is None and bot is not None:
                top = 2 * r - bot
                notes.append("upper end runs into another marker: mirror of the lower end")
            if bot is None and top is not None:
                bot = 2 * r - top
                notes.append("lower end runs into another marker or below the axis: mirror of the upper end")
            if hid_t or hid_b:
                notes.append("bar hidden in the marker at the " + " and ".join(
                    [s for s, h in (("top", hid_t), ("bottom", hid_b)) if h]) + ": at most the marker edge")
            pad = lw + ym
            vt, vb = ya + yb * top, ya + yb * bot
            row.update(bar_lo=float(min(vt, vb)), bar_hi=float(max(vt, vb)),
                       bar_lo_outer=float(min(ya + yb * (top - pad), ya + yb * (bot + pad))),
                       bar_hi_outer=float(max(ya + yb * (top - pad), ya + yb * (bot + pad))),
                       px_lo=float(top), px_hi=float(bot))
            if notes:
                row["note"] += "; " + "; ".join(notes)
        out.append(row)
    return out


# ---------------------------------------------------------------- bars
def read_bars(image, at, cfg):
    """Bar charts on a categorical or day axis. Bars are the columns of the fill colour; bar k is
    paired with at[k] (left to right). The value is the bar's top edge; error bars in cfg bar_color."""
    cal = calibrate(image, cfg)
    ya, yb, ym = cal["y"]
    xa, xb, xm = cal["x"]
    box = cal["box"]
    fill = color_mask(image, cfg["color"], cfg)
    fill[: (box["top"][1] + 2) if box["top"] else 0] = False
    fill[box["bottom"][0] - 1:] = False
    colsum = fill.sum(axis=0)
    bars = [(s, e) for s, e in _runs(colsum > cfg.get("min_fill", 20)) if e - s >= cfg.get("min_width", 25)]
    if len(bars) != len(at):
        raise ValueError(f"found {len(bars)} bars at columns {bars}, expected {len(at)}")
    emask = color_mask(image, cfg.get("bar_color", "dark"), cfg)
    out = []
    for (s, e), xv in zip(bars, at):
        c = (s + e) / 2
        mid = slice(int(s + 0.3 * (e - s)), int(e - 0.3 * (e - s)))
        rows = np.nonzero(fill[:, mid].sum(axis=1) > 0.5 * (mid.stop - mid.start))[0]
        top = rows.min() - cfg.get("edge_px", 0.0)
        y = ya + yb * top
        e_px = cfg.get("top_px", 3.0) + ym
        lo, hi = sorted([ya + yb * (top - e_px), ya + yb * (top + e_px)])
        row = {"x": xv, "y": float(y), "lo": float(lo), "hi": float(hi), "px": [float(c), float(top)],
               "note": f"bar columns {s}-{e}, top edge row {top:.0f}; y misfit {ym:.1f} px"}
        if cfg.get("bars", True):
            # error-bar column: the ink column nearest the bar centre above the bar
            band = int(cfg.get("band", 4))
            up, _ = _walk(emask, c, int(top) - 2, -1, set(), gap=cfg.get("gap", 3), band=band)
            lw = cfg.get("bar_lw", 4)
            if up is None or up > top - 4:
                row["note"] += "; no error bar above the bar (hidden or absent): reported as at most the top edge"
                t = top
            else:
                t = up + 0.5 + lw / 2
            # the lower end is inside the bar, drawn in the same ink only if it contrasts; mirror it
            b = 2 * top - t
            row["note"] += "; lower end taken as the mirror of the upper (hidden in the bar)"
            pad = lw + ym
            row.update(bar_lo=float(ya + yb * b), bar_hi=float(ya + yb * t),
                       bar_lo_outer=float(ya + yb * (b + pad)), bar_hi_outer=float(ya + yb * (t - pad)),
                       px_lo=float(t), px_hi=float(b))
        out.append(row)
    return out


# ---------------------------------------------------------------- lines
def read_line(image, at, cfg):
    cal = calibrate(image, cfg)
    xa, xb, xm = cal["x"]
    ya, yb, ym = cal["y"]
    mask = color_mask(image, cfg["color"], cfg)
    box = cal["box"]
    mask[: (box["top"][1] + 2) if box["top"] else 0] = False
    mask[box["bottom"][0] - 8:] = False   # the spine's tinted edge
    rlo, rhi = 0, mask.shape[0]
    out = []
    half = cfg.get("half_band", 12)
    for xv in at:
        c = int(round((xv - xa) / xb))
        sub = mask[rlo:rhi, max(c - half, 0):c + half + 1]
        rows = np.nonzero(sub.any(axis=1))[0]
        if len(rows) == 0:
            out.append({"x": xv, "y": None, "note": "no line ink near this x"})
            continue
        runs = _runs(sub.any(axis=1))
        s, e = max(runs, key=lambda t: t[1] - t[0]) if cfg.get("longest") else runs[cfg.get("run", 0)]
        s, e = s + rlo, e + rlo
        r = (s + e) / 2
        y = ya + yb * r
        e_px = (e - s) / 2 + ym + 1
        lo, hi = sorted([ya + yb * (r - e_px), ya + yb * (r + e_px)])
        out.append({"x": xv, "y": float(y), "lo": float(lo), "hi": float(hi), "px": [float(c), float(r)],
                    "note": f"line ink rows {s}-{e} in columns {c - half}-{c + half}; y misfit {ym:.1f} px"})
    return out


# ---------------------------------------------------------------- spreadsheet-style panels (Figs. 2, 3)
# Thick gray axes; the value axis has gray ticks protruding to the left of a thick gray spine; the
# tick labels are matched in order (bottom first). Bars are light-cyan fills inside a gray outline.
def gray_axes(image, cfg):
    a = _rgb(image)
    g = a.mean(axis=2)
    ch = a.max(axis=2) - a.min(axis=2)
    gm = (ch < 30) & (g > 100) & (g < 190)
    H, W = gm.shape
    vlen = np.array([_longest(gm[:, c]) for c in range(W)])
    cols = [c for c in range(int(W * cfg.get("spine_search", 0.5))) if vlen[c] > 0.5 * vlen.max()]
    # the left spine: the first long vertical gray band at least 10 px wide (thin gray lines are the
    # anti-aliased edges of the black panel frame)
    sp = [gr for gr in _groups(cols) if gr[1] - gr[0] >= 10][0]
    hlen = np.array([_longest(gm[r]) for r in range(H)])
    axis_rows = [r for r in range(H) if hlen[r] > 0.5 * W]
    ax = [gr for gr in _groups(axis_rows) if gr[1] - gr[0] >= 10][-1]   # the category axis band
    probe = sp[0] - cfg.get("tick_probe", 15)
    trows = [r for r in range(H) if gm[r, probe] and not (ax[0] - 3 <= r <= ax[1] + 3)]
    ticks = sorted([(s + e) / 2 + 0.5 for s, e in _groups(trows) if e - s >= 6], reverse=True)
    yl = cfg["y_labels"]
    if len(ticks) != len(yl["values"]):
        raise ValueError(f"ticks at rows {ticks}, labels {yl['values']}")
    ya, yb, ym = _fit(ticks, yl["values"])
    return {"gm": gm, "g": g, "spine": sp, "axis": ax, "y": (ya, yb, ym), "ticks": ticks}


def read_gray_bars(image, at, cfg):
    ax = gray_axes(image, cfg)
    ya, yb, ym = ax["y"]
    gm, g = ax["gm"], ax["g"]
    fill = color_mask(image, "cyan", cfg)
    fill[:, : ax["spine"][1] + 1] = False
    fill[ax["axis"][0]:] = False
    colsum = fill.sum(axis=0)
    bars = [(s, e) for s, e in _runs(colsum > 20) if e - s >= 25]
    if len(bars) != len(at):
        raise ValueError(f"found {len(bars)} bars at columns {bars}, expected {len(at)}")
    zero_note = f"axis band rows {ax['axis'][0]}-{ax['axis'][1]} (0 there would be row {(0 - ya) / yb:.0f})"
    out = []
    for (s, e), xv in zip(bars, at):
        c = int((s + e) / 2)
        mid = slice(int(s + 0.3 * (e - s)), int(e - 0.3 * (e - s)) + 1)
        # the fill's top edge, from the side quarters of the bar (the error bar is drawn in the middle)
        # (and a coloured marker may sit over part of it): the 20th percentile of the per-column first
        # fill rows, so columns where something is drawn over the fill do not pull the edge down
        firsts = []
        for cc in range(s + 3, e - 3):
            col = fill[:, cc]
            for r0 in np.nonzero(col)[0]:
                if col[r0:r0 + 12].all():          # a solid run of fill, not stray tinted pixels
                    firsts.append(r0)
                    break
        ftop = int(np.percentile(firsts, 5))
        # outline stroke width: the gray run just left of the fill, half way down the bar
        ws = []
        for rr in np.linspace(ftop + 20, ax["axis"][0] - 20, 9).astype(int):
            k = s - 1
            while k > 0 and gm[rr, k]:
                k -= 1
            ws.append(s - 1 - k)
            k = e
            while k < gm.shape[1] - 1 and gm[rr, k]:
                k += 1
            ws.append(k - e)
        w = int(np.median([v for v in ws if v > 5] or [0]))
        val_row = ftop - w / 2                      # the centre of the outline's top stroke
        # ink above the fill in the central columns (outline and any error bar drawn over it)
        ink = gm[:, mid].mean(axis=1) > 0.3        # gray ink only: a coloured marker over the bar is not a bar
        r = ftop - 1
        while r > 0 and ink[r]:
            r -= 1
        top_ink = r + 1
        y = ya + yb * val_row
        e_px = w / 4 + ym + 1
        lo, hi = sorted([ya + yb * (val_row - e_px), ya + yb * (val_row + e_px)])
        row = {"x": xv, "y": float(y), "lo": float(lo), "hi": float(hi), "px": [float(c), float(val_row)],
               "note": f"bar columns {s}-{e}; top stroke rows {top_ink}-{ftop} (stroke width {w} px), value at "
                       f"the stroke centre; y misfit {ym:.1f} px; {zero_note}"}
        if cfg.get("bars", True):
            if top_ink < ftop - w - 3:
                t = top_ink
                row["note"] += "; error bar rises above the outline: upper end at the top of the ink"
            else:
                t = ftop - w
                row["note"] += "; error bar hidden in the outline: reported as at most the outline stroke"
            # the lower end: gray ink continuing down the bar's centre column into the fill
            r2 = ftop
            while r2 < ax["axis"][0] and gm[r2, c - 3:c + 4].any():
                r2 += 1
            if r2 > ftop + 3 and t != ftop - w:
                b = r2
                row["note"] += f"; lower end read where the bar's gray stub ends in the fill (row {r2})"
            else:
                b = 2 * val_row - t
                row["note"] += "; lower end taken as the mirror of the upper (inside the bar)"
            pad = 2 + ym
            row.update(bar_lo=float(ya + yb * b), bar_hi=float(ya + yb * t),
                       bar_lo_outer=float(ya + yb * (b + pad)), bar_hi_outer=float(ya + yb * (t - pad)),
                       px_lo=float(t), px_hi=float(b))
        out.append(row)
    return out


def read_gray_markers(image, at, cfg):
    """Filled markers of one colour on a gray-axis panel, paired left to right with `at`."""
    ax = gray_axes(image, cfg)
    ya, yb, ym = ax["y"]
    mask = color_mask(image, cfg["color"], cfg)
    mask[:, : ax["spine"][1] + 1] = False
    mask[ax["axis"][0]:] = False
    if cfg.get("max_col_frac"):
        mask[:, int(mask.shape[1] * cfg["max_col_frac"]):] = False
    op = ndi.binary_opening(mask, structure=_disk(cfg.get("r_open", 16)))
    lab, n = ndi.label(op)
    marks = []
    for sl in ndi.find_objects(lab):
        rr, cc = sl
        if min(rr.stop - rr.start, cc.stop - cc.start) < cfg.get("min_size", 20):
            continue
        marks.append(((cc.start + cc.stop) / 2, (rr.start + rr.stop) / 2, rr.stop - rr.start))
    marks.sort()
    if len(marks) != len(at):
        raise ValueError(f"found {len(marks)} markers {marks}, expected {len(at)}")
    out = []
    for (c, r, h), xv in zip(marks, at):
        y = ya + yb * r
        e_px = cfg.get("centre_px", 4.0) + ym
        lo, hi = sorted([ya + yb * (r - e_px), ya + yb * (r + e_px)])
        out.append({"x": xv, "y": float(y), "lo": float(lo), "hi": float(hi), "px": [float(c), float(r)],
                    "note": f"{cfg['color']} marker {h} px tall at column {c:.0f}, centre of what survives an "
                            f"opening that removes the thick line; y misfit {ym:.1f} px; no error bars drawn"})
    return out


def read_markers_deskewed(image, at, cfg):
    """read_markers on a figure whose scan is slightly rotated: straightened first by the shared
    helper boxgraph.digitize.deskew (rotation about the crop centre; the reported pixel positions are
    in the straightened crop, a few pixels from the original at most)."""
    from boxgraph import digitize as D
    angle = D.find_skew(np.asarray(image)[..., :3].astype(np.uint8), dark=cfg.get("dark", 170))
    img = D.deskew(np.asarray(image)[..., :3].astype(np.uint8), min_deg=0.05)
    out = read_markers(img, at, cfg)
    for r in out:
        r["note"] = r.get("note", "") + f"; crop straightened by {angle:.2f} deg before reading"
    return out


def load(name):
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("shyer2013_" + name, Path(__file__).with_name("_shyer.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
