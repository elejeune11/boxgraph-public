"""Shared reading code for the figures of savin2011 (vector art, rendered at 600-1200 dpi).

Calibration, all from the image (labels are matched to ticks by match_ticks, which takes the straight
line that puts the most printed labels on tick candidates, so a stray mark or a hidden tick is ignored):
  * the frame: the lowest long dark row (x axis) and the leftmost long dark column (y axis) of the
    crop, as in boxgraph.digitize.find_axes;
  * the ticks: short dark runs standing perpendicular to an axis line, inside or outside the frame
    (whichever side has more), grouped into marks up to `tick_w` px wide; the longest marks are the
    labelled ones (minor ticks of a log axis are shorter). They are matched in order to the printed
    labels the panel's spec lists (`sel` picks a slice of the detected marks when some carry no
    label); a straight line (in log10 for a log axis) is fitted and its largest misfit, in pixels,
    is added to every interval.
Points: pixels of the series' colour (within `tol`), restricted to the plot box; thin lines (fit
curves, error bars) are removed by an opening with a square of side `open` px, so the markers are
what remains (an open circle is filled first when `hollow`). Each marker is read at the centre of
its bounding box. Its 95% interval is that centre +- (misfit + 2 px), widened by `extra_px`.
Error bars: in the bar colour, along the marker's centre column (+-`band` px), from the marker's edge
outward, bridging gaps up to `gap` px (other symbols drawn over the bar); each end is read at the
last bar pixel; its outer interval adds misfit + 3 px. A bar not reaching beyond the marker is
reported as at most the marker (its edge), and says so.
Categorical x axes (embryonic stage) snap each point to the nearest stage tick, since the symbols
are shifted sideways only to show the error bars.
"""

import numpy as np
from scipy import ndimage

from boxgraph.digitize import Axis, color_mask


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _longest(v, gap=3):
    best = (0, 0, 0)
    rs = _runs(v)
    merged = []
    for a, b in rs:
        if merged and a - merged[-1][1] <= gap:
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    for a, b in merged:
        if b - a > best[0]:
            best = (b - a, a, b)
    return best


def dark_mask(img, thr=110):
    """Black ink (frames, ticks): every channel dark, so saturated colours are not taken for it."""
    return img.max(axis=2) < thr


def frame(img, spec):
    """Rows of the x axis line, columns of the y axis line, and the plot box (c0, r0, c1, r1)."""
    d = dark_mask(img, spec.get("dark", 110))
    H, W = d.shape
    region = spec.get("frame_region")  # optional [c0, r0, c1, r1] to look for the frame in
    c0, r0, c1, r1 = region if region else (0, 0, W, H)
    sub = d[r0:r1, c0:c1]
    h, w = sub.shape
    rows = [(r, *_longest(sub[r])) for r in range(h)]
    long_rows = [x for x in rows if x[1] >= 0.45 * w]
    cols = [(c, *_longest(sub[:, c])) for c in range(w)]
    long_cols = [x for x in cols if x[1] >= 0.45 * h]
    xr = max(r for r, *_ in long_rows)
    x_rows = sorted(r for r, *_ in long_rows if xr - r <= 12)
    yc = min(c for c, *_ in long_cols)
    y_cols = sorted(c for c, *_ in long_cols if c - yc <= 12)
    _, xc0, xc1 = max((x for x in long_rows if x[0] in x_rows), key=lambda x: x[1])[1:]
    _, yr0, yr1 = max((x for x in long_cols if x[0] in y_cols), key=lambda x: x[1])[1:]
    top_rows = [r for r, *_ in long_rows if r < x_rows[0] - 20]
    right_cols = [c for c, *_ in long_cols if c > y_cols[-1] + 20]
    box_top = (max(r for r in top_rows if r < h / 2) + 1) if any(r < h / 2 for r in top_rows) else yr0
    box_right = min(c for c in right_cols if c > w / 2) if any(c > w / 2 for c in right_cols) else xc1
    return dict(xa=(x_rows[0] + r0, x_rows[-1] + r0), ya=(y_cols[0] + c0, y_cols[-1] + c0),
                xspan=(xc0 + c0, xc1 + c0), yspan=(yr0 + r0, yr1 + r0),
                box=(y_cols[-1] + 1 + c0, box_top + r0, box_right + c0, x_rows[0] + r0), dark=d)


def _tick_groups(lengths, cap, tick_w):
    pos = sorted(p for p, n in lengths.items() if 4 <= n <= cap)
    groups, cur = [], []
    for p in pos + [None]:
        if cur and (p is None or p != cur[-1] + 1):
            if len(cur) <= tick_w:
                groups.append(((cur[0] + cur[-1]) / 2 + 0.5, max(lengths[q] for q in cur)))
            cur = []
        if p is not None:
            cur.append(p)
    return groups


def _run_from(line):
    k = 0
    while k < 3 and k < len(line) and not line[k]:
        k += 1
    n = 0
    while k + n < len(line) and line[k + n]:
        n += 1
    return n


def ticks(fr, spec):
    """Major tick positions along x (columns) and y (rows)."""
    d = fr["dark"]
    tw = spec.get("tick_w", 24)
    (ra0, ra1), (ca0, ca1) = fr["xa"], fr["ya"]
    xc0, xc1 = fr["xspan"]
    yr0, yr1 = fr["yspan"]
    capx = spec.get("tick_cap", 0.08 * (yr1 - yr0))
    capy = spec.get("tick_cap", 0.08 * (xc1 - xc0))
    m = 6  # stay clear of the corners
    out = {}
    for name, (outside, inside) in {
        "x": ({c: _run_from(d[ra1 + 1:, c]) for c in range(xc0 + m, xc1 - m)},
              {c: _run_from(d[:ra0, c][::-1]) for c in range(xc0 + m, xc1 - m)}),
        "y": ({r: _run_from(d[r, :ca0][::-1]) for r in range(yr0 + m, yr1 - m)},
              {r: _run_from(d[r, ca1 + 1:]) for r in range(yr0 + m, yr1 - m)}),
    }.items():
        cap = capx if name == "x" else capy
        side = spec.get(name, {}).get("side")
        go, gi = _tick_groups(outside, cap, tw), _tick_groups(inside, cap, tw)
        g = go if side == "out" else gi if side == "in" else (go if len(go) >= len(gi) else gi)
        if not g:
            out[name] = []
            continue
        longest = max(n for _, n in g)
        frac = spec.get(name, {}).get("major_frac", 0.0)  # every mark is a candidate; match_ticks sorts them out
        out[name] = sorted(c for c, n in g if n >= frac * longest)
    # the axis line itself may stand at a labelled value (ticks at the frame corners are not found)
    return out


def calibrate(img, spec):
    fr = frame(img, spec)
    tk = ticks(fr, spec)
    axes = {}
    for name in ("x", "y"):
        s = spec[name]
        pos = list(tk[name])
        if name == "y":
            pos = pos[::-1]  # bottom (largest row) first, as labels are listed from the axis origin
        anchor = None
        if s.get("origin_at_axis"):  # the axis line carries the first label (corner tick not separable)
            anchor = (fr["xa"][0] + fr["xa"][1]) / 2 + 0.5 if name == "y" else (fr["ya"][0] + fr["ya"][1]) / 2 + 0.5
            pos = [anchor] + pos
        if "sel" in s:
            pos = pos[s["sel"][0]:s["sel"][1]]
        axes[name] = Axis(s.get("scale", "linear"),
                          match_ticks(pos, s["labels"], s.get("scale", "linear"), name, anchor, s.get("min_match")))
    return fr, axes["x"], axes["y"]


def match_ticks(cands, labels, scale, name="axis", anchor=None, min_match=None):
    """Match printed labels to tick candidates: the straight-line map (in log10 for a log axis) that puts
    the most labels within 6 px of a candidate, ties going to the smallest misfit. Candidates that are
    not ticks (a line or symbol touching the axis) and ticks hidden under symbols are thereby ignored.
    Returns the matched (pixel, label) pairs; at least three are needed (two when only two are printed)."""
    import math
    u = [math.log10(v) if scale == "log10" else float(v) for v in labels]
    c = sorted(cands)
    ca, ua = np.array(c, float), np.array(u, float)
    best = (0, 0.0, [])
    for i in range(len(c)):
        for j in range(i + 1, len(c)):
            for a in range(len(u)):
                for b in range(len(u)):
                    if a == b:
                        continue
                    k = (c[j] - c[i]) / (u[b] - u[a])
                    if (k > 0) != (name == "x"):  # columns grow with x; rows fall as y grows
                        continue
                    if abs(k) * float(np.min(np.abs(np.diff(ua)))) < 15:  # labels at least 15 px apart
                        continue
                    p = c[i] + k * (ua - u[a])
                    if anchor is not None and abs(p[0] - anchor) > 6:  # the first label is on the axis line
                        continue
                    d = np.abs(ca[None, :] - p[:, None])
                    near = d.argmin(axis=1)
                    dist = d[np.arange(len(ua)), near]
                    ok = dist <= 6
                    if len(set(near[ok].tolist())) < int(ok.sum()):  # one tick per label
                        continue
                    n, err = int(ok.sum()), float(dist[ok].sum())
                    if n > best[0] or (n == best[0] and err < best[1]):
                        best = (n, err, [(float(ca[near[q]]), labels[q]) for q in np.flatnonzero(ok)])
    need = min_match or (3 if len(labels) > 2 else 2)
    if best[0] < need:
        raise ValueError(f"{name} axis: only {best[0]} of the labels {labels} match the tick candidates "
                         f"{[round(p) for p in c]}")
    return best[2]


def _bar_end(mask, col, start, step, band, gap, limit):
    H = mask.shape[0]
    c0, c1 = max(0, int(round(col)) - band), int(round(col)) + band + 1
    r, last, miss = start, None, 0
    cl, cr = int(round(col)) - band - 6, int(round(col)) + band + 6
    W = mask.shape[1]
    while 0 <= r < H and (limit is None or (step < 0 and r >= limit[0]) or (step > 0 and r <= limit[1])):
        # a bar row is a narrow run: a line of the same colour crossing the column (a fit curve, an x
        # error bar) also covers the pixels either side of it and is not counted
        wide = 0 <= cl and cr < W and mask[r, cl] and mask[r, cr]
        if mask[r, c0:c1].any() and not wide:
            last, miss = r, 0
        else:
            miss += 1
            if miss > gap:
                break
        r += step
    return last


def _bar_through(bar, ink, col, start, step, band, gap):
    """Follow a bar from `start` in direction `step`, crossing other symbols drawn over it (ink of
    another colour) when the bar's colour resumes beyond them. Returns (end, far): the last bar pixel,
    and, when the bar stops against other ink, the far side of that ink (else None)."""
    H = bar.shape[0]
    c0, c1 = max(0, int(round(col)) - band), int(round(col)) + band + 1
    end = None
    r = start
    while True:
        e = _bar_end(bar, col, r, step, band, gap, None)
        if e is not None:
            end = e
            r = e + step
        # cross other ink
        q = r
        while 0 <= q < H and ink[q, c0:c1].any() and not bar[q, c0:c1].any():
            q += step
        if abs(q - r) > 4 and 0 <= q < H and bar[q, c0:c1].any():
            r = q  # the bar resumes beyond the other symbol
            continue
        far = q if abs(q - r) > 4 else None
        return end, far


def points(img, spec):
    """Read one series of markers, with vertical error bars when spec['bars'] is set."""
    fr, xa, ya = calibrate(img, spec)
    c0, r0, c1, r1 = fr["box"]
    pad = spec.get("pad", 3)
    mask = color_mask(img, spec["color"], spec.get("tol"))
    keep = np.zeros_like(mask)
    keep[r0 + pad:r1 - pad, c0 + pad:c1 - pad] = True
    for (a, b, c, e) in spec.get("exclude", []):  # legends, insets
        keep[b:e, a:c] = False
    if "region" in spec:
        a, b, c, e = spec["region"]
        reg = np.zeros_like(keep)
        reg[b:e, a:c] = True
        keep &= reg
    mask &= keep
    if spec.get("hollow"):  # an open symbol: bridge where other ink crosses its ring, then fill it
        cl = spec.get("close", 17)
        m = ndimage.binary_fill_holes(ndimage.binary_closing(mask, structure=np.ones((cl, cl), bool)))
    else:
        m = mask
    k = spec.get("open", 15)
    yy, xx = np.mgrid[:k, :k]
    disk = np.hypot(yy - (k - 1) / 2, xx - (k - 1) / 2) <= k / 2
    blobs = ndimage.binary_opening(m, structure=disk)
    lab, n = ndimage.label(blobs)
    misfit = max(xa.residual_px, ya.residual_px)
    bar_mask = color_mask(img, spec.get("bar_color", spec["color"]), spec.get("bar_tol", spec.get("tol"))) & keep
    out = []
    snap = spec.get("snap")
    ink = img.astype(float).min(axis=2) < 200  # any ink, of any colour
    objs = [sl for sl in ndimage.find_objects(lab)
            if spec.get("min_area", 60) <= (lab[sl] > 0).sum() <= spec.get("max_area", 10 ** 9)]
    # the marker size, from the series' own markers: a smaller box is a marker partly hidden
    hs = sorted(sl[0].stop - sl[0].start for sl in objs)
    ws = sorted(sl[1].stop - sl[1].start for sl in objs)
    size_h = hs[len(hs) // 2] if hs else 0
    size_w = ws[len(ws) // 2] if ws else 0
    if spec.get("size"):
        size_h = size_w = spec["size"]
    fused = spec.get("fused", 1.6)
    for sl in objs:
        rr, cc = sl
        if size_h and ((rr.stop - rr.start) > fused * size_h or (cc.stop - cc.start) > fused * size_w):
            continue  # several markers run together (or a marker fused with a line): not readable as one
        col = (cc.start + cc.stop - 1) / 2
        row = (rr.start + rr.stop - 1) / 2
        x = xa.to_value(col)
        if snap:
            x = min(snap, key=lambda s: abs(s - x))
        hidden_px = max(0.0, (size_h - (rr.stop - rr.start)) / 2)
        hidden_px_w = max(0.0, (size_w - (cc.stop - cc.start)) / 2)
        fitted = ""
        if (hidden_px > 2 or hidden_px_w > 2) and size_h > 20:
            # a symbol partly hidden (by another symbol or a line drawn over it): fit a template of the
            # series' own size and shape to what is visible
            from scipy.signal import fftconvolve
            R = size_h / 2
            k = int(np.ceil(R)) + 2
            yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
            shape = spec.get("shape", "disk")
            if spec.get("hollow"):
                dist = np.hypot(yy, xx)
                ann = ((dist >= 0.7 * R) & (dist <= R)).astype(float)
            else:
                inside = {"disk": np.hypot(yy, xx) <= R, "square": np.maximum(abs(yy), abs(xx)) <= R,
                          "diamond": abs(yy) + abs(xx) <= R,
                          "triangle": (abs(yy) <= R) & (abs(xx) <= (yy + R) * 0.577)}[shape]
                ann = np.where(inside, 1.0, -1.0) * (np.hypot(yy, xx) <= R + 2)  # inside counts, a ring outside costs
            w0, w1 = int(max(0, col - 2 * R)), int(min(mask.shape[1], col + 2 * R))
            h0, h1 = int(max(0, row - 2 * R)), int(min(mask.shape[0], row + 2 * R))
            win = mask[h0:h1, w0:w1].astype(float)
            score = fftconvolve(win, ann[::-1, ::-1], mode="same")
            # the visible piece belongs to this marker: its centre lies within R of the piece's centre
            gr, gc = np.mgrid[h0:h1, w0:w1]
            score[(abs(gr - row) > R) | (abs(gc - col) > R)] = -np.inf
            pr, pc = np.unravel_index(np.argmax(score), score.shape)
            row, col = float(h0 + pr), float(w0 + pc)
            x = xa.to_value(col)
            if snap:
                x = min(snap, key=lambda s: abs(s - x))
            rr = slice(int(round(row - R)), int(round(row + R)) + 1)
            cc = slice(int(round(col - R)), int(round(col + R)) + 1)
            hidden_px, hidden_px_w = 4.0, 0.0  # a fitted centre: +-4 px
            fitted = f"; partly hidden: centre fitted to the visible part ({shape} of {size_h} px), +-4 px"
        e = misfit + 2 + spec.get("extra_px", 0) + (hidden_px if hidden_px > 2 else 0)
        y = ya.to_value(row)
        y1, y2 = ya.to_value(row + e), ya.to_value(row - e)
        rec = {"x": float(x), "y": float(y), "lo": float(min(y1, y2)), "hi": float(max(y1, y2)),
               "px": [float(col), float(row)], "note": f"marker {cc.stop - cc.start}x{rr.stop - rr.start} px"}
        if fitted:
            rec["note"] += fitted
        elif hidden_px > 2 or hidden_px_w > 2:
            rec["note"] += (f"; partly hidden by other symbols ({size_w}x{size_h} px unhidden), interval "
                            f"widened by {hidden_px:.0f} px")
            if hidden_px_w > 2 and hidden_px <= 2:
                rec["note"] += " (hidden sideways only: the row is unaffected)"
        if spec.get("bars"):
            band, gap = spec.get("band", 3), spec.get("gap", 6)
            up, up_far = _bar_through(bar_mask, ink, col, rr.start - 1, -1, band, gap)
            dn, dn_far = _bar_through(bar_mask, ink, col, rr.stop, 1, band, gap)
            top = up if up is not None else rr.start
            bot = dn if dn is not None else rr.stop - 1
            hidden = []
            half = max(rr.stop - rr.start, size_h) / 2  # the marker's own half height
            if up is None or row - up <= half + 6:
                top, hidden = row - half, hidden + ["upper in the marker"]
            if dn is None or dn - row <= half + 6:
                bot, hidden = row + half, hidden + ["lower in the marker"]
            o = misfit + 3
            # an end that stops against other ink (another symbol drawn over the bar) may go on under it:
            # its outer interval reaches the far side of that ink
            top_o, bot_o = top - o, bot + o
            if up_far is not None:
                top_o = min(top_o, up_far - o)
                hidden.append("upper under other ink")
            if dn_far is not None:
                bot_o = max(bot_o, dn_far + o)
                hidden.append("lower under other ink")
            vt, vb = ya.to_value(top), ya.to_value(bot)
            vto, vbo = ya.to_value(top_o), ya.to_value(bot_o)
            rec.update(bar_hi=float(max(vt, vb)), bar_lo=float(min(vt, vb)),
                       bar_hi_outer=float(max(vto, vbo)), bar_lo_outer=float(min(vto, vbo)),
                       px_lo=float(top), px_hi=float(bot))
            if hidden:
                rec["note"] += ("; bar ends hidden: " + ", ".join(hidden) +
                                " (in the marker: reported as at most the marker; under other ink: outer "
                                "interval reaches the far side of that ink)")
        out.append(rec)
    out.sort(key=lambda r: (r["x"], r["y"]))
    if spec.get("only_x"):  # the stages a table also gives, so the two can be compared point by point
        out = [r for r in out if r["x"] in spec["only_x"]]
    if spec.get("one_per_x"):
        seen = {}
        for r in out:
            seen.setdefault(r["x"], []).append(r)
        dup = [x for x, v in seen.items() if len(v) > 1]
        if dup:
            raise ValueError(f"several markers at x = {dup}")
    exp = spec.get("expect")
    if exp is not None and len(out) != exp:
        raise ValueError(f"{len(out)} markers found, {exp} expected: {[(round(r['x'], 3), round(r['y'], 3)) for r in out]}")
    for r in out:
        r["note"] += f"; calibration misfit {misfit:.1f} px"
    return out


def bars(img, spec):
    """A bar chart: bars of one colour, each read at its top edge (the median top over its middle half),
    with a black error bar along its centre column, read from its cap above the bar to its lower end
    inside the bar. x is the bar's ordinal, left to right (1, 2, ...), as the categories are printed
    in that order; only the y axis is calibrated (`y` labels; the x spec is not used)."""
    s = spec["y"]
    label_px = 0.0
    if "label_box" in s:
        # a raster panel without tick marks: each printed label's line of text is centred on its value;
        # the centre row of each text line in the label column is matched to the labels (bottom first),
        # and a quarter of the text height is added to every interval for that assumption
        a, b, c, e = s["label_box"]
        rows = dark_mask(img, s.get("dark", 110))[b:e, a:c].any(axis=1)
        lines = [(b + r0_, b + r1_) for r0_, r1_ in _runs(rows) if r1_ - r0_ >= 8]
        pos = [(r0_ + r1_ - 1) / 2 for r0_, r1_ in lines][::-1]
        label_px = float(np.median([r1_ - r0_ for r0_, r1_ in lines])) / 4 if lines else 0.0
        c0, r0, c1, r1 = spec["plot"]
        fr = None
    else:
        fr = frame(img, spec)
        tk = ticks(fr, spec)
        pos = list(tk["y"])[::-1]
        if s.get("origin_at_axis"):
            pos = [(fr["xa"][0] + fr["xa"][1]) / 2 + 0.5] + pos
    if "label_box" in s:  # text lines, one per label, in order
        if len(pos) != len(s["labels"]):
            raise ValueError(f"y axis: {len(pos)} label lines found at {[round(p) for p in pos]}, "
                             f"{len(s['labels'])} labels")
        ya = Axis(s.get("scale", "linear"), list(zip(pos, s["labels"])))
    else:
        ya = Axis(s.get("scale", "linear"), match_ticks(pos, s["labels"], s.get("scale", "linear"), "y"))
    if fr is not None:
        c0, r0, c1, r1 = fr["box"]
    mask = color_mask(img, spec["color"], spec.get("tol"))
    keep = np.zeros_like(mask)
    keep[r0 + 2:r1 - 1, c0 + 2:c1 - 2] = True
    mask &= keep
    black = (img.max(axis=2) < 110) & keep  # black ink only (a saturated red or blue is dark on average)
    lab, n = ndimage.label(mask)
    out = []
    objs = [sl for sl in ndimage.find_objects(lab) if (lab[sl] > 0).sum() >= spec.get("min_area", 200)]
    objs.sort(key=lambda sl: sl[1].start)
    misfit = ya.residual_px + label_px
    band, gap = spec.get("band", 3), spec.get("gap", 3)
    for i, (rr, cc) in enumerate(objs):
        w = cc.stop - cc.start
        mid = range(cc.start + w // 4, cc.stop - w // 4)
        tops = [np.flatnonzero(mask[:, c])[0] for c in mid if mask[:, c].any()]
        top = float(np.median(tops))
        col = (cc.start + cc.stop - 1) / 2
        # the error bar's column: the black column nearest the bar's centre, just above the bar
        row_above = int(top) - 3
        cols = [c for c in range(cc.start, cc.stop) if black[row_above, c]]
        bc = min(cols, key=lambda c: abs(c - col)) if cols else col
        e = misfit + 2
        y = ya.to_value(top)
        rec = {"x": float(i + 1), "y": float(y), "lo": float(ya.to_value(top + e)), "hi": float(ya.to_value(top - e)),
               "px": [float(col), float(top)], "note": f"bar {w} px wide, top edge; calibration misfit {misfit:.1f} px"}
        if spec.get("bars", True):
            up = _bar_end(black, bc, int(top), -1, band, gap, None)
            dn = _bar_end(black, bc, int(top), 1, band, gap, None)
            if up is not None and dn is not None and up < top - 3:
                o = misfit + 3
                rec.update(bar_hi=float(ya.to_value(up)), bar_lo=float(ya.to_value(dn)),
                           bar_hi_outer=float(ya.to_value(up - o)), bar_lo_outer=float(ya.to_value(dn + o)),
                           px_lo=float(up), px_hi=float(dn))
            else:
                rec["note"] += "; no error bar found above the bar"
        out.append(rec)
    exp = spec.get("expect")
    if exp is not None and len(out) != exp:
        raise ValueError(f"{len(out)} bars found, {exp} expected")
    return out


def read_id(image, at, rid):
    """Read the panel whose spec is SPECS[rid] in _specs.py."""
    import importlib.util
    from pathlib import Path
    s = importlib.util.spec_from_file_location("savin2011_specs", Path(__file__).with_name("_specs.py"))
    mod = importlib.util.module_from_spec(s)
    s.loader.exec_module(mod)
    spec = mod.SPECS[rid]
    kind = spec.get("kind", "points")
    if kind == "points":
        return points(image, spec)
    if kind == "curve":
        return curve(image, at, spec)
    if kind == "bars":
        return bars(image, spec)
    raise ValueError(f"unknown kind {kind!r}")
