"""Shared reading code for the data plots of Kassab et al. 1993 (Figs. 6-11): black-and-white
scans of points of three trees, RCA (open squares), LAD (open triangles) and LCX (open circles),
against the order number, some with vertical error bars and with fitted lines drawn through them.

Everything below is taken from the rendered crop; the only values typed in are the printed axis
labels, given by each reading's own file.

Calibration
- The scan is straightened first (boxgraph.digitize.find_skew: the tilt of its longest line);
  overlay positions are turned back onto the crop as rendered (`to_original`).
- Ink is darker than 128 (grey 0-255).
- The axes are the longest vertical line (the y axis, at the left) and the longest horizontal line
  (the x axis, at the bottom).
- Tick marks are short runs of ink that stick out of the axis line on its outer side only (left
  of the local edge of the y axis, below the x axis); a marker sitting on the axis sticks out on
  both sides and is not a tick. A run longer than `y_major` px is a labelled tick.
- Linear y axis: the labelled ticks, top to bottom, are matched to the printed labels; a tick
  hidden under a marker is skipped (gaps are whole label steps, the shortest gap one step).
  A straight line is fitted; its largest misfit (px) widens every interval.
- Log y axis: the decades of these scans are unevenly spaced (by up to 15%), so the axis is
  calibrated piecewise: the labelled decade ticks (hidden ones skipped as above), then the
  unlabelled ticks at 2..9 x 10^k, each accepted once the interpolation through the ticks already
  accepted places it unambiguously (`_log_calibration`); values are interpolated linearly in
  log10 between neighbouring ticks. The misfit is the largest leave-one-out residual of a tick.
- When the lowest label sits on the x axis, half the axis line's thickness is added to the misfit.
- x: the order ticks, left to right, are matched to the orders (1..11, or 11..1 on the reversed
  axes of Figs. 10 and 11), the first order on the y axis; marker edges on the axis are dropped and
  hidden ticks skipped by their spacing (`_evenly`). Only used to place the search windows.

Points
- The marker shapes are cut out of the figure's own legend (`legend`: the crop box of each glyph),
  so their size and line weight are those of the plotted markers; the legend area is then blanked.
- Each glyph pixel is weighted by its distance from the outlines of the other two glyphs
  (`_distinctive`), so a square must show its corners, a circle its diagonal arcs, a triangle its
  apex and slanted sides.
- In a window around the column of order n each template is slid over the image; `hit` is the
  weighted fraction of its ink on ink (ink dilated by 2 px), the score is hit minus 0.35 x the
  fraction of its inner white that is ink. The best position is the point; its value is the
  centre of the glyph's bounding box. No value is returned (the marker is hidden or ambiguous) when:
  hit < 0.85 or score < 0.6 (`present`); another position more than a quarter glyph away scores
  within 0.06 of the best; or a better-scoring marker of another shape overlaps the best position
  and hit < 0.97.
- Interval: 4 px (template position) + the calibration misfit; for triangles also the difference
  between the bounding-box centre and the centroid (one sixth of the glyph height), since which of
  the two the plotting program put on the value is not known.

Error bars (when `bars` is set)
- The stem is the vertical run of ink through the marker's centre column, followed above the top
  and below the bottom of the marker (gaps up to 6 px bridged); each end is the last ink row of
  the stem (the cap). The bar end is read with +-(4 px + misfit); an end hidden in the marker is
  the mirror of the other.
- A bar is not reported when the marker sits on the y axis, or when a marker of another series
  lies in the same column along the bar or over the point (the stem may belong to it). When no
  stem sticks out of the marker the bar is reported as at most the marker (its edges).
"""

import numpy as np
from scipy import ndimage

INK = 128
SERIES = ("square", "triangle", "circle")


def _ink(image):
    """Ink mask of the straightened figure, and the tilt angle (degrees) it was turned by."""
    from PIL import Image

    from boxgraph.digitize import find_skew

    img = np.ascontiguousarray(image[..., :3])
    angle = find_skew(img)
    if abs(angle) >= 0.05:
        img = np.asarray(Image.fromarray(img).rotate(-angle, resample=Image.BICUBIC, fillcolor=(255, 255, 255)))
    else:
        angle = 0.0
    g = img.astype(float).mean(axis=2)
    return g < INK, angle


def to_original(cal, col, row):
    """A pixel of the straightened figure back on the crop as rendered (for the overlay)."""
    a = np.radians(cal["angle"])
    H, W = cal["ink"].shape
    cx, cy = W / 2.0, H / 2.0
    # PIL rotate(-angle) turned the image clockwise by angle (in screen coordinates); undo it
    dx, dy = col - cx, row - cy
    c = cx + dx * np.cos(a) + dy * np.sin(a)
    r = cy - dx * np.sin(a) + dy * np.cos(a)
    return float(c), float(r)


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def axes(ink):
    H, W = ink.shape
    cs = ink.sum(axis=0)
    rs = ink.sum(axis=1)
    ycols = [c for c in range(W) if cs[c] > 0.85 * cs.max()]
    xrows = [r for r in range(H) if rs[r] > 0.85 * rs.max()]
    yl, yr = min(ycols), max(ycols) + 1
    xt, xb = min(xrows), max(xrows) + 1
    return yl, yr, xt, xb


def _ticks_left(ink, yl, xt, xb, major):
    """Rows of tick marks left of the y axis: (centre row, length out of the axis)."""
    out = []
    H = ink.shape[0]
    left = np.full(H, -1)
    right = np.full(H, -1)
    for r in range(min(H, xt)):
        row = ink[r]
        # the run of ink holding the axis: start from the axis column nearest to ink
        cols = [c for c in range(yl - 2, yl + 12) if 0 <= c < row.size and row[c]]
        if not cols:
            continue
        c = cols[0]
        lo = c
        while lo > 0 and row[lo - 1]:
            lo -= 1
        hi = c
        while hi + 1 < row.size and row[hi + 1]:
            hi += 1
        left[r], right[r] = lo, hi
    ok = (left >= 0) & (right - left < 16)
    rr = np.flatnonzero(ok)
    p = np.polyfit(rr, left[rr], 1)
    q = np.polyfit(rr, right[rr], 1)
    edge = np.polyval(p, np.arange(H))
    redge = np.polyval(q, np.arange(H))
    lengths = np.where(left >= 0, edge - left, 0)
    rlen = np.where(right >= 0, right - redge, 0)
    for a, b in _runs(lengths >= major):
        # a tick sticks out on the left only; a marker sitting on the axis sticks out on both sides
        if b - a < 30 and b <= xb + 3 and rlen[a:b].max() < 6:
            out.append(((a + b - 1) / 2.0, int(lengths[a:b].max())))
    return out


def _ticks_below(ink, yl, yr, xb, major):
    out = []
    W = ink.shape[1]
    lengths = np.zeros(W, int)
    for c in range(W):
        n = 0
        r = xb
        while r < ink.shape[0] and ink[r, c]:
            n += 1
            r += 1
        lengths[c] = n
    for a, b in _runs(lengths >= major):
        if b - a < 30:
            out.append(((a + b - 1) / 2.0, int(lengths[a:b].max())))
    return out


def _fit(pix, val):
    pix = np.asarray(pix, float)
    val = np.asarray(val, float)
    b, a = np.polyfit(pix, val, 1)
    mis = float(np.max(np.abs((val - (a + b * pix)) / b)))
    return a, b, mis


def _evenly(cands, n):
    """Ticks for n evenly spaced positions, the first candidate being the first position: the
    candidates kept (dropping at most three, e.g. the edges of markers sitting on the axis), each
    with its index 0..n-1. Ticks hidden under markers are skipped, inside or at the end: gaps are
    whole numbers of steps, each within 6% of the step. Fewest dropped candidates first, then the
    fewest skipped ticks, then the most even set."""
    from itertools import combinations

    best = None
    for k in range(0, min(3, len(cands) - 3) + 1):
        for drop in combinations(range(1, len(cands)), k):
            pick = [c for i, c in enumerate(cands) if i not in drop]
            gaps = np.diff(pick)
            unit = float(np.median(gaps[gaps < 1.5 * gaps.min()]))
            steps = np.maximum(np.round(gaps / unit), 1)
            dev = float(np.max(np.abs(gaps / (steps * unit) - 1)))
            if dev > 0.06 or int(steps.sum()) > n - 1:
                continue
            key = (k, n - 1 - int(steps.sum()) + int((steps > 1).sum()), dev)
            if best is None or key < best[0]:
                best = (key, pick, [0] + np.cumsum(steps).astype(int).tolist())
        if best is not None:
            break
    return (best[1], best[2]) if best else None


def calibrate(image, cfg):
    ink, angle = _ink(image)
    yl, yr, xt, xb = axes(ink)
    ticks = _ticks_left(ink, yl, xt, xb, cfg.get("y_minor", 8))
    majors = [t[0] for t in ticks if t[1] >= cfg["y_major"]]
    if cfg.get("y_bottom_at_axis"):
        # the lowest label sits on the x axis, whose line hides its tick
        majors.append((xt + xb - 1) / 2.0)
    majors = sorted(majors)
    labels = cfg["y_labels"]  # top to bottom
    if cfg["y_log"]:
        rows, vals, ymis = _log_calibration(majors, [t[0] for t in ticks if t[1] < cfg["y_major"]], labels)
    else:
        # labelled ticks hidden under a marker are skipped: the shortest gap is one label step
        gaps = np.diff(majors)
        unit = float(np.min(gaps))
        steps = [int(round(g / unit)) for g in gaps]
        if any(abs(g / (s * unit) - 1) > 0.1 for g, s in zip(gaps, steps)) or sum(steps) != len(labels) - 1:
            raise RuntimeError(f"labelled y ticks {majors} do not match the labels {labels}")
        idx = np.concatenate([[0], np.cumsum(steps)]).astype(int)
        rows, vals = list(majors), [float(labels[i]) for i in idx]
        a_, b_, ymis = _fit(rows, vals)
    if cfg.get("y_bottom_at_axis"):
        # where in the thickness of the axis line the lowest label lies is not known
        ymis += (xb - xt) / 2.0
    xc = [t[0] for t in _ticks_below(ink, yl, yr, xb, cfg["x_major"]) if t[0] > yl + 20]
    if cfg.get("x_first_at_axis"):
        # the first order sits on the y axis, whose line hides its tick
        xc.append((yl + yr - 1) / 2.0)
    orders = cfg["x_orders"]  # left to right
    ev = _evenly(sorted(xc), len(orders))
    if ev is None:
        raise RuntimeError(f"expected {len(orders)} evenly spaced x ticks in {sorted(xc)}")
    xt_, xi = ev
    xa, xbb, xmis = _fit(xt_, [orders[i] for i in xi])
    return dict(ink=ink, angle=angle, yl=yl, yr=yr, xt=xt, xb=xb, yrows=rows, yvals=vals, ymis=ymis,
                xa=xa, xb_=xbb, xmis=xmis, xticks=xt_, log=cfg["y_log"])


def _interp(r, rows, vals):
    """Piecewise linear through the ticks, extended linearly beyond the end ones."""
    rows = np.asarray(rows, float)
    vals = np.asarray(vals, float)
    if r <= rows[0]:
        i = 0
    elif r >= rows[-1]:
        i = len(rows) - 2
    else:
        i = int(np.searchsorted(rows, r) - 1)
    t = (r - rows[i]) / (rows[i + 1] - rows[i])
    return float(vals[i] + t * (vals[i + 1] - vals[i]))


def _log_calibration(majors, minors, labels):
    """Rows and log10 values of the ticks of a log axis whose decades are unevenly spaced (a
    distorted scan): the labelled decade ticks, then the unlabelled ticks at 2..9 x 10^k, each
    accepted only once the interpolation through the ticks already accepted places its value
    unambiguously (nearer to it than a third of the distance to the next candidate value)."""
    top = np.log10(labels[0])
    bottom = np.log10(labels[-1])
    gaps = np.diff(majors)
    unit = float(np.min(gaps))  # the shortest gap is one decade
    dec = [top]
    for g in gaps:
        dec.append(dec[-1] - round(g / unit))
    if abs(dec[-1] - bottom) > 1e-9:
        raise RuntimeError(f"decade ticks {majors} do not span the labels {labels}: {dec}")
    rows = list(majors)
    vals = list(dec)
    cand_vals = sorted({np.log10(k) + d for d in range(int(bottom) - 1, int(top) + 1) for k in range(2, 10)
                        if bottom < np.log10(k) + d < top})
    left = sorted(minors)
    for _ in range(6):
        order = np.argsort(rows)
        R = [rows[i] for i in order]
        V = [vals[i] for i in order]
        added = False
        for m in list(left):
            v = _interp(m, R, V)
            k = int(np.argmin([abs(c - v) for c in cand_vals]))
            near = cand_vals[k]
            others = [abs(c - near) for c in cand_vals if c != near] + [abs(d - near) for d in dec]
            spacing = min(others)
            if abs(v - near) < spacing / 3 and all(abs(near - x) > 1e-9 for x in vals):
                rows.append(m)
                vals.append(near)
                left.remove(m)
                added = True
        if not added:
            break
    order = np.argsort(rows)
    R = [float(rows[i]) for i in order]
    V = [float(vals[i]) for i in order]
    # calibration uncertainty: how far each inner tick lies from the interpolation without it
    res = []
    for i in range(1, len(R) - 1):
        v = _interp(R[i], R[:i] + R[i + 1:], V[:i] + V[i + 1:])
        slope = (V[i + 1] - V[i - 1]) / (R[i + 1] - R[i - 1])
        res.append(abs((v - V[i]) / slope))
    return R, V, float(max(res)) if res else 0.0


def yval(cal, row):
    v = _interp(row, cal["yrows"], cal["yvals"])
    return float(10 ** v) if cal["log"] else float(v)


def xcol(cal, order):
    return (order - cal["xa"]) / cal["xb_"]


def template(ink, box):
    c0, r0, c1, r1 = box
    g = ink[r0:r1, c0:c1]
    rows = np.flatnonzero(g.any(axis=1))
    cols = np.flatnonzero(g.any(axis=0))
    g = g[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]
    # inner white: inside the filled outline, more than 4 px from the glyph's ink
    filled = ndimage.binary_fill_holes(g)
    dist = ndimage.distance_transform_edt(~g)
    inner = filled & ~g & (dist > 4)
    return g, inner


def _distinctive(tpls):
    """Weight each glyph's ink pixels by how far they lie from the outlines of the other glyphs
    centred on the same point (0.15 on a shared outline, 1 at 8 px or more), so that a square
    must show its corners, a circle its diagonal arcs and a triangle its apex and slanted sides."""
    out = {}
    for k, (g, inner) in tpls.items():
        h, w = g.shape
        dmin = np.full(g.shape, np.inf)
        for j, (gj, _) in tpls.items():
            if j == k:
                continue
            canvas = np.zeros((h + 2 * gj.shape[0], w + 2 * gj.shape[1]), bool)
            r0 = gj.shape[0] + (h - gj.shape[0]) // 2
            c0 = gj.shape[1] + (w - gj.shape[1]) // 2
            canvas[r0:r0 + gj.shape[0], c0:c0 + gj.shape[1]] = gj
            d = ndimage.distance_transform_edt(~canvas)[gj.shape[0]:gj.shape[0] + h, gj.shape[1]:gj.shape[1] + w]
            dmin = np.minimum(dmin, d)
        wgt = np.where(g, np.clip(dmin / 8.0, 0.15, 1.0), 0.0)
        out[k] = (wgt, inner)
    return out


def _score_map(inkd, ink, tpl, inner, r0, r1, c0, c1):
    h, w = tpl.shape
    from scipy.signal import fftconvolve

    tp = tpl.sum()
    ip = max(inner.sum(), 1)
    sub_d = inkd[r0:r1 + h, c0:c1 + w].astype(float)
    sub = ink[r0:r1 + h, c0:c1 + w].astype(float)
    hit = fftconvolve(sub_d, tpl[::-1, ::-1].astype(float), mode="valid") / tp
    fill = fftconvolve(sub, inner[::-1, ::-1].astype(float), mode="valid") / ip
    s = hit - 0.35 * fill
    k = np.unravel_index(np.argmax(s), s.shape)
    # the best score elsewhere, more than a quarter of the glyph away from the best position
    far = s.copy()
    far[max(k[0] - h // 4, 0):k[0] + h // 4 + 1, max(k[1] - w // 4, 0):k[1] + w // 4 + 1] = -9
    second = float(far.max()) if far.size else -9.0
    return (float(s[k]), r0 + k[0], c0 + k[1], float(hit[k]), float(fill[k]), second)


def present(m):
    """A marker is taken as found when at least 85% of its glyph's (weighted) ink lies on ink and its
    score (that fraction less 0.35 x the inner fill) is at least 0.6."""
    return m["hit"] >= 0.85 and m["score"] >= 0.6


def find_marker(cal, shape_tpl, order, half_window_cols):
    ink = cal["ink"]
    inkd = ndimage.binary_dilation(ink, iterations=2)
    tpl, inner = shape_tpl
    h, w = tpl.shape
    xc = xcol(cal, order)
    c0 = int(round(xc - half_window_cols - w / 2))
    c1 = int(round(xc + half_window_cols - w / 2))
    r0 = 0
    r1 = int(cal["xt"] - h / 2)
    c0 = max(c0, 0)
    r1 = min(r1, ink.shape[0] - h - 1)
    c1 = min(c1, ink.shape[1] - w - 1)
    s, r, c, hit, fill, second = _score_map(inkd, ink, tpl, inner, r0, r1, c0, c1)
    return dict(score=s, row=r + (h - 1) / 2.0, col=c + (w - 1) / 2.0, top=r, bottom=r + h - 1,
                left=c, right=c + w - 1, h=h, w=w, hit=hit, fill=fill, second=second)


def _stem_end(ink, col, start, step, stop, gap=6):
    """Last ink row walking from `start` in direction `step` along column col (+-1 px)."""
    r = start
    last = None
    miss = 0
    while 0 <= r < ink.shape[0] and r != stop:
        if ink[r, col - 1:col + 2].any():
            last = r
            miss = 0
        else:
            miss += 1
            if miss > gap:
                break
        r += step
    return last


def read_points(image, at, cfg, series):
    cal = calibrate(image, cfg)
    ink = cal["ink"]
    tpls = {k: template(ink, box) for k, box in cfg["legend"].items()}
    tpls = _distinctive(tpls)
    # the legend (glyphs and their names) is not data: blank it before searching for points
    ink = ink.copy()
    c0, r0, c1, r1 = cfg["legend_area"]
    ink[r0:r1, c0:c1] = False
    cal["ink"] = ink
    half = 0.5 / abs(cal["xb_"])  # px per half an order
    mis = cal["ymis"]
    out = []
    found_all = {}
    for x in at:
        order = float(x)
        found_all[order] = {k: find_marker(cal, tpls[k], order, 0.45 * half) for k in tpls}
    for x in at:
        order = float(x)
        m = found_all[order][series]
        if not present(m):
            out.append({"x": order, "y": None,
                        "note": f"order {x}: no {series} found (best score {m['score']:.2f}, hit {m['hit']:.2f}); hidden under another marker or absent"})
            continue
        rivals = [k for k, o in found_all[order].items()
                  if k != series and present(o) and o["score"] > m["score"]
                  and np.hypot(o["row"] - m["row"], o["col"] - m["col"]) < 0.6 * max(m["h"], m["w"])]
        if rivals and m["hit"] < 0.97:
            out.append({"x": order, "y": None,
                        "note": (f"order {x}: {series} not told apart: its best place (row {m['row']:.0f}, hit {m['hit']:.2f}) "
                                 f"overlaps a better-matching {', '.join(rivals)} and its own distinctive outline is not all inked")})
            continue
        if m["second"] >= m["score"] - 0.06:
            out.append({"x": order, "y": None,
                        "note": (f"order {x}: {series} position ambiguous: best score {m['score']:.2f} at row {m['row']:.0f}, "
                                 f"but {m['second']:.2f} more than a quarter marker away (overlapping markers)")})
            continue
        row = m["row"]
        e = 4.0 + mis
        lo_row, hi_row = row + e, row - e
        extra = ""
        if series == "triangle":
            d = m["h"] / 6.0
            lo_row = row + d + e  # centroid lies below the box centre for an upward triangle
            extra = f"; triangle: interval spans box centre and centroid (+{d:.0f} px)"
        y = yval(cal, row)
        pc, pr = to_original(cal, m["col"], row)
        rec = {"x": order, "y": y, "lo": yval(cal, lo_row), "hi": yval(cal, hi_row),
               "px": [pc, pr], "px_lo": pr - (row - hi_row), "px_hi": pr + (lo_row - row),
               "note": f"order {x}: {series} at col {m['col']:.0f}, row {row:.1f}, score {m['score']:.2f} (hit {m['hit']:.2f}, fill {m['fill']:.2f}){extra}"}
        if cfg.get("bars"):
            rec.update(_bar(cal, m, series, found_all[order], mis))
        out.append(rec)
    return out


def _bar(cal, m, series, others, mis):
    ink = cal["ink"]
    col = int(round(m["col"]))
    if abs(m["col"] - (cal["yl"] + cal["yr"]) / 2.0) < m["w"] / 2.0:
        return {"note_bar": "error bar not reported: the marker sits on the y axis, whose line hides the stem"}
    up = _stem_end(ink, col, m["top"] - 1, -1, -1)
    down = _stem_end(ink, col, m["bottom"] + 1, +1, int(cal["xt"]) - 2)
    res = {}
    # does the stem really leave the marker?
    up_out = up is not None and up < m["top"] - 6
    down_out = down is not None and down > m["bottom"] + 6
    # other markers in the same column between the point and the ends
    blockers = []
    for k, o in others.items():
        if k == series or not present(o):
            continue
        if abs(o["col"] - m["col"]) < m["w"]:
            blockers.append((k, o["top"], o["bottom"]))
    e = 4.0 + mis
    hi_r = up if up_out else None
    lo_r = down if down_out else None
    # a marker of another series anywhere along the stem (or over this marker), or just past an
    # end where the stem stopped: the stem may run on behind it, or belong to it
    span_top = (hi_r if hi_r is not None else m["top"]) - 12
    span_bot = (lo_r if lo_r is not None else m["bottom"]) + 12
    amb = [b for b in blockers if b[2] >= span_top and b[1] <= span_bot]
    if amb:
        res["note_bar"] = f"error bar not reported: {', '.join(b[0] for b in amb)} marker in the same column along the bar"
        return res
    if not up_out and not down_out:
        res.update({"bar_lo": yval(cal, m["bottom"]), "bar_hi": yval(cal, m["top"]),
                    "bar_lo_outer": yval(cal, m["bottom"] + e), "bar_hi_outer": yval(cal, m["top"] - e)})
        res["note_bar"] = "no stem outside the marker: bar at most the marker"
        return res
    notes = []
    if lo_r is None:
        lo_r = 2 * m["row"] - hi_r
        notes.append("lower end hidden in the marker: mirror of the upper")
    if hi_r is None:
        hi_r = 2 * m["row"] - lo_r
        notes.append("upper end hidden in the marker: mirror of the lower")
    if lo_r >= cal["xt"] - 3:
        notes.append("lower end reaches the x axis (may be cut by it)")
    if notes:
        res["note_bar"] = "; ".join(notes)
    res.update({"bar_lo": yval(cal, lo_r), "bar_hi": yval(cal, hi_r),
                "bar_lo_outer": yval(cal, lo_r + e), "bar_hi_outer": yval(cal, hi_r - e),
                "bar_px": [hi_r, lo_r]})
    return res


def read(image, at, cfg, series):
    out = read_points(image, at, cfg, series)
    for o in out:
        nb = o.pop("note_bar", None)
        o.pop("bar_px", None)
        if nb:
            o["note"] += "; " + nb
    return out
