"""Shared reading code for Fig. 6 (p. 6): R_a vs R_c points of six dogs, and the waterfall lines.

Everything is found in the image: the frame, its inward tick marks (matched to the printed labels
0, 20, ..., 140 on x and 0, 20, ..., 100 on y), the markers and their shapes, the rings that mark
the waterfall model's calculated points, and the lines that join those points.
"""

import numpy as np
from scipy import ndimage

X_LABELS = [20, 40, 60, 80, 100, 120]   # inner x tick labels as printed
Y_LABELS = [20, 40, 60, 80]             # inner y tick labels as printed


def _dark(image):
    g = image.astype(float).mean(axis=2)
    paper, ink = np.percentile(g, 60), np.percentile(g, 0.5)
    return g < (paper + ink) / 2


def _longest(v):
    best, bs, start = 0, 0, None
    for i, x in enumerate(list(v) + [False]):
        if x and start is None:
            start = i
        elif not x and start is not None:
            if i - start > best:
                best, bs = i - start, start
            start = None
    return best, bs


def frame(d):
    """Rows/columns of the four frame lines (inner edges)."""
    H, W = d.shape
    long_rows = [r for r in range(H) if _longest(d[r])[0] > 0.6 * W]
    long_cols = [c for c in range(W) if _longest(d[:, c])[0] > 0.5 * H]
    top = [r for r in long_rows if r < H / 2]
    bot = [r for r in long_rows if r > H / 2]
    left = [c for c in long_cols if c < W / 2]
    right = [c for c in long_cols if c > W / 2]
    return {"top": (min(top), max(top)), "bottom": (min(bot), max(bot)),
            "left": (min(left), max(left)), "right": (min(right), max(right))}


def _groups(pos):
    out, cur = [], []
    for p in sorted(pos) + [None]:
        if cur and (p is None or p > cur[-1] + 1):
            out.append((cur[0] + cur[-1]) / 2 + 0.5)
            cur = []
        if p is not None:
            cur.append(p)
    return out


def _ticks_h(d, fr, side):
    """Columns of tick marks pointing inward from the top or bottom frame line."""
    c0, c1 = fr["left"][1] + 20, fr["right"][0] - 20
    if side == "bottom":
        band = d[fr["bottom"][0] - 14:fr["bottom"][0] - 3, c0:c1]
    else:
        band = d[fr["top"][1] + 4:fr["top"][1] + 15, c0:c1]
    full = band.all(axis=0)
    return [c + c0 for c in _groups(np.nonzero(full)[0])]


def _ticks_v(d, fr, side):
    r0, r1 = fr["top"][1] + 20, fr["bottom"][0] - 20
    if side == "left":
        band = d[r0:r1, fr["left"][1] + 4:fr["left"][1] + 15]
    else:
        band = d[r0:r1, fr["right"][0] - 14:fr["right"][0] - 3]
    full = band.all(axis=1)
    return [r + r0 for r in _groups(np.nonzero(full)[0])]


def _match(ticks, labels, spacing_guess):
    """Keep tick candidates that fall on an evenly spaced grid matching the labels in order."""
    ticks = sorted(ticks)
    best = None
    for t0 in ticks[:1]:   # the first candidate is the first labelled tick
        for t1 in ticks:
            if t1 <= t0:
                continue
            step = t1 - t0
            if abs(step - spacing_guess) > 0.2 * spacing_guess:
                continue
            pairs = []
            for k, lab in enumerate(labels):
                target = t0 + (k - 0) * step
                near = [t for t in ticks if abs(t - target) < 0.05 * step]
                if near:
                    pairs.append((min(near, key=lambda t: abs(t - target)), lab))
            if best is None or len(pairs) > len(best):
                best = pairs
    return best


def _fit(pairs):
    p = np.array([a for a, _ in pairs], float)
    v = np.array([b for _, b in pairs], float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs(p - (v - a) / b)))
    return a, b, mis


def calibrate(d, x_labels=X_LABELS, x_step=1 / 7, y_labels=Y_LABELS, y_step=1 / 5,
              x_sides=("bottom",), y_sides=("left",)):
    """Axis fits from the inward tick marks. The first label lies one tick step from the frame
    corner (frame = 0 on both axes in Figs. 5 and 6); later ticks follow at the same step."""
    fr = frame(d)
    W = fr["right"][0] - fr["left"][1]
    H = fr["bottom"][0] - fr["top"][1]
    xs = []
    for side in x_sides:   # by default the labelled axis; Fig. 6's top ticks are drawn up to 10 px off
        t = _ticks_h(d, fr, side)
        first = [c for c in t if abs(c - (fr["left"][1] + W * x_step)) < W / 40]
        if not first:
            continue
        cand = [c for c in t if c >= first[0] - 2]
        xs += _match(cand, x_labels, W * x_step)
    ys = []
    for side in y_sides:
        t = _ticks_v(d, fr, side)
        first = [r for r in t if abs(r - (fr["bottom"][0] - H * y_step)) < H / 40]
        if not first:
            continue
        cand = sorted([r for r in t if r <= first[0] + 2], reverse=True)
        pr = _match([-r for r in cand], y_labels, H * y_step)
        ys += [(-r, lab) for r, lab in pr]
    ax, bx, mx = _fit(xs)
    ay, by, my = _fit(ys)
    return {"frame": fr, "x": (ax, bx, mx), "y": (ay, by, my), "x_marks": xs, "y_marks": ys}


def _ring_around(d, r, c):
    """True if a circle of ink surrounds (r, c) at a radius larger than a marker."""
    H, W = d.shape
    th = np.linspace(0, 2 * np.pi, 180, endpoint=False)
    for rad in range(30, 70, 2):
        rr = np.clip(np.round(r + rad * np.sin(th)).astype(int), 0, H - 1)
        cc = np.clip(np.round(c + rad * np.cos(th)).astype(int), 0, W - 1)
        hit = d[rr, cc] | d[np.clip(rr + 1, 0, H - 1), cc] | d[rr, np.clip(cc + 1, 0, W - 1)]
        if hit.mean() > 0.75:
            return rad
    return 0


def markers(image):
    """Every plotted marker inside the frame: kind, centre (row, col), size, encircled or not."""
    d = _dark(image)
    cal = calibrate(d)
    fr = cal["frame"]
    m = np.zeros_like(d)
    r0, r1 = fr["top"][1] + 8, fr["bottom"][0] - 8
    c0, c1 = fr["left"][1] + 8, fr["right"][0] - 3
    m[r0:r1, c0:c1] = d[r0:r1, c0:c1]
    lab, _ = ndimage.label(m)
    comps = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        sub = lab[sl] == i
        area = int(sub.sum())
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if area < 200 or h > 80 or w > 80:
            continue  # tick marks, specks, letters joined to lines, long lines
        comps.append({"sl": sl, "sub": sub, "area": area, "h": h, "w": w,
                      "bottom": sl[0].stop})
    # text of the legend: six or more components sharing one baseline
    base = {}
    for k in comps:
        base.setdefault(round(k["bottom"] / 6), []).append(k)
    text = set()
    for key, ks in base.items():
        near = ks + base.get(key - 1, []) + base.get(key + 1, [])
        if len(near) >= 6:
            text |= {id(k) for k in near}
    out = []
    for k in comps:
        if id(k) in text:
            continue
        parts = [k]
        if k["h"] > 1.6 * k["w"]:  # two touching markers one above the other: a marker's height from each end
            hm = int(np.median([q["h"] for q in comps if q["h"] < 1.3 * q["w"] and abs(q["w"] - k["w"]) <= 4]))
            parts = []
            for a, b in ((0, hm), (k["h"] - hm, k["h"])):
                sub = k["sub"][a:b]
                rows = np.nonzero(sub.any(axis=1))[0]
                cols = np.nonzero(sub.any(axis=0))[0]
                sl = (slice(k["sl"][0].start + a + rows[0], k["sl"][0].start + a + rows[-1] + 1),
                      slice(k["sl"][1].start + cols[0], k["sl"][1].start + cols[-1] + 1))
                s2 = sub[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]
                parts.append({"sl": sl, "sub": s2, "area": int(s2.sum()), "h": s2.shape[0], "w": s2.shape[1],
                              "split": True})
        for p in parts:
            filled = int(ndimage.binary_fill_holes(p["sub"]).sum())
            box = p["h"] * p["w"]
            hollow = filled > 1.3 * p["area"]
            ratio = filled / box
            fm = ndimage.binary_fill_holes(p["sub"])
            wt = fm[int(0.2 * p["h"])].sum()
            wb = fm[int(0.8 * p["h"]) - 1].sum()
            triangle = min(wt, wb) / max(wt, wb) < 0.6   # one end of a triangle is much narrower
            if hollow:
                if triangle:
                    kind = "open_triangle"
                elif ratio > 0.86:
                    kind = "open_square"
                else:
                    kind = "open_circle"
            else:
                if ratio > 0.86:
                    kind = "filled_square"
                elif triangle:
                    kind = "filled_triangle"
                else:
                    kind = "filled_circle"
            rows, cols = np.nonzero(p["sub"])
            rc = (p["sl"][0].start + p["h"] / 2, p["sl"][1].start + p["w"] / 2)       # box centre
            cen = (p["sl"][0].start + rows.mean() + 0.5, p["sl"][1].start + cols.mean() + 0.5)
            ring = _ring_around(d, rc[0], rc[1])
            out.append({"kind": kind, "row": rc[0], "col": rc[1], "cen": cen, "h": p["h"], "w": p["w"],
                        "area": p["area"], "ring": ring, "split": p.get("split", False)})
    return d, cal, out


def to_x(cal, col):
    a, b, _ = cal["x"]
    return a + b * col


def to_y(cal, row):
    a, b, _ = cal["y"]
    return a + b * row


def read_kind(image, kind):
    d, cal, ms = markers(image)
    _, bx, mx = cal["x"]
    _, by, my = cal["y"]
    out = []
    for m in sorted((m for m in ms if m["kind"] == kind and not m["ring"]), key=lambda m: m["col"]):
        # where the point is: the box centre; centroid offset, 2 px placement and the calibration misfit
        err = abs(m["cen"][0] - m["row"]) + 2.0 + my
        y = to_y(cal, m["row"])
        lo, hi = sorted([to_y(cal, m["row"] - err), to_y(cal, m["row"] + err)])
        note = (f"{kind} marker {m['h']}x{m['w']} px; x cal misfit {mx:.2f} px, y cal misfit {my:.2f} px; "
                f"1 px = {abs(bx):.4f} (x), {abs(by):.4f} (y)")
        if m["split"]:
            note += "; split from a touching marker"
        out.append({"x": to_x(cal, m["col"]), "y": y, "lo": lo, "hi": hi, "px": [m["col"], m["row"]],
                    "px_lo": m["row"] + err, "px_hi": m["row"] - err, "note": note})
    return out


def _trace(d, r, c, ang, start, step=2.0, gap=16):
    """Walk from (r, c) along angle `ang` (radians, image coordinates) from radius `start`,
    re-centering on the line, until no ink for `gap` px. Returns the last inked point."""
    H, W = d.shape
    dr, dc = np.sin(ang), np.cos(ang)
    pr, pc = -dc, dr
    pos = np.array([r + start * dr, c + start * dc])
    last, miss = pos.copy(), 0
    pts = []
    while 0 < pos[0] < H - 1 and 0 < pos[1] < W - 1 and miss < gap:
        offs = np.arange(-4, 5)
        rr = np.round(pos[0] + offs * pr).astype(int).clip(0, H - 1)
        cc = np.round(pos[1] + offs * pc).astype(int).clip(0, W - 1)
        ink = d[rr, cc]
        if ink.any():
            shift = offs[ink].mean()
            pos = pos + 0.5 * shift * np.array([pr, pc])
            last, miss = pos.copy(), 0
            pts.append(pos.copy())
        else:
            miss += step
        pos = pos + step * np.array([dr, dc])
    return last, pts


def read_waterfall(image, kind):
    """The waterfall line of the dog whose symbol `kind` is encircled: its two calculated points,
    the ring centre and the free end of the line."""
    d, cal, ms = markers(image)
    _, bx, mx = cal["x"]
    _, by, my = cal["y"]
    ring = [m for m in ms if m["kind"] == kind and m["ring"]]
    if len(ring) != 1:
        return [{"x": None, "y": None, "note": f"{len(ring)} encircled {kind} markers found"}]
    m = ring[0]
    r, c, rad = m["row"], m["col"], m["ring"]
    # the line leaves the ring where ink continues outward: look between 1.3 and 1.8 ring radii
    th = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    score = np.zeros_like(th)
    for k in np.linspace(1.3, 1.8, 6):
        rr = np.round(r + k * rad * np.sin(th)).astype(int).clip(0, d.shape[0] - 1)
        cc = np.round(c + k * rad * np.cos(th)).astype(int).clip(0, d.shape[1] - 1)
        score += d[rr, cc]
    # every direction with ink at most radii; the line is the one that can be followed farthest
    best = None
    for ang in th[score >= score.max() - 1]:
        e, pts = _trace(d, r, c, ang, 1.3 * rad, step=1.0)
        if best is None or len(pts) > len(best[1]):
            best = (e, pts)
    end = best[0]
    out = []
    note = f"x cal misfit {mx:.2f} px, y cal misfit {my:.2f} px"
    err_c = 3.0 + my                      # ring centre: ring and symbol box agree to a few px
    err_e = 4.0 + my                      # free end: line width and the end's ragged cut
    for (rr, cc, e, what) in ((r, c, err_c, f"centre of the ring round the {kind}"),
                              (end[0], end[1], err_e, "free end of the line")):
        lo, hi = sorted([to_y(cal, rr - e), to_y(cal, rr + e)])
        out.append({"x": to_x(cal, cc), "y": to_y(cal, rr), "lo": lo, "hi": hi, "px": [cc, rr],
                    "px_lo": rr + e, "px_hi": rr - e, "note": f"{what}; {note}"})
    return sorted(out, key=lambda o: o["x"])


def load():
    return None
