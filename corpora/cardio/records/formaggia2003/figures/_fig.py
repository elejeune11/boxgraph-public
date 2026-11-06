"""Shared reading code for the boxed line plots of this paper (Figs. 6-8, 11-13). Each figure is an
embedded low-resolution raster (black on white); a reading renders one panel at 900 dpi, where
one raster pixel is about 6 px.

Calibration, all from the image:
- ink is darker than halfway between the paper (99th percentile) and the darkest pixel;
- the plot box: the left and right borders are the columns (in the left and right thirds) with
  the most ink, the top and bottom borders the rows (upper and lower halves) with the most ink;
- tick marks point inwards from the borders. On the border the reading names, every short run
  of ink (6-60 px long, at most 25 px wide) leaving it is a candidate. The printed labels are
  evenly spaced in value, so the matched ticks are those best fitting one evenly spaced comb of
  as many teeth as labels (pairs of candidates fix the comb; a candidate within 3% of the spacing
  matches a tooth). At least all but one label must be matched;
- where a printed label sits at a corner of the box (e.g. x = 0 under the left border), the
  border's centre is that mark too;
- a straight line is fitted to the marks of each axis; its largest misfit (px) widens every
  interval; a misfit over 8 px raises an error.

Curves: several black curves (dotted, dashed, dash-dot) that coincide over long stretches. At x,
the ink in a window of +-W px (bridging the gaps of dotted and dashed lines) is split into tracks
where rows of ink are more than GAP px apart. A reading names rules (x0, x1, rank, n): the first
rule whose range holds x and whose n (None: any) equals the number of tracks found gives the
track to take (0 = top, -1 = bottom). The value is the centre of that track's ink in the centre
columns (+-2 px) if any, else in the window; the interval is half the track's extent plus one
raster pixel plus the calibration misfit (plus the local slope times the x misfit). Where curves
coincide they form one track and the reading is of all of them: the interval covers it.
"""

import numpy as np

W = 9
GAP = 10
BLUR = 6.0
STEEP = 90


def ink_mask(image):
    g = image[..., :3].astype(float).mean(axis=2)
    thr = (np.percentile(g, 99) + g.min()) / 2.0
    return g < thr


def _runs(v):
    d = np.diff(np.concatenate([[0], np.asarray(v, int), [0]]))
    return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


def _band(s, lo, hi):
    seg = s[lo:hi]
    k = int(np.argmax(seg))
    idx = [i for i in range(max(k - 15, 0), min(k + 16, len(seg))) if seg[i] > 0.85 * seg[k]]
    return lo + min(idx), lo + max(idx) + 1


def plot_box(ink):
    H, Wd = ink.shape
    cs = ink.sum(axis=0)
    rs = ink.sum(axis=1)
    l0, l1 = _band(cs, 0, Wd // 3)
    r0, r1 = _band(cs, 2 * Wd // 3, Wd)
    t0, t1 = _band(rs, 0, H // 2)
    b0, b1 = _band(rs, H // 2, H)
    return dict(l0=l0, l1=l1, r0=r0, r1=r1, t0=t0, t1=t1, b0=b0, b1=b1,
                lc=(l0 + l1 - 1) / 2.0, rc=(r0 + r1 - 1) / 2.0, tc=(t0 + t1 - 1) / 2.0, bc=(b0 + b1 - 1) / 2.0)


def tick_candidates(ink, bx, side, min_len=6, max_len=60):
    """(position, length, (a, b) span, start) of short runs of ink leaving a border inwards."""
    if side in ("bottom", "top"):
        span = range(bx["l1"] + 3, bx["r0"] - 3)
        start, step = (bx["b0"] - 1, -1) if side == "bottom" else (bx["t1"], 1)
        get = lambda r, c: ink[r, c]  # noqa: E731
    else:
        span = range(bx["t1"] + 3, bx["b0"] - 3)
        start, step = (bx["l1"], 1) if side == "left" else (bx["r0"] - 1, -1)
        get = lambda r, c: ink[c, r]  # noqa: E731  (r: column, c: row)
    lens = []
    for p in span:
        n = 0
        while n < 200 and get(start + step * n, p):
            n += 1
        lens.append(n)
    lens = np.array(lens)
    out = []
    for a, b in _runs((lens >= min_len) & (lens <= max_len)):
        if b - a > 25:
            continue
        out.append((span[0] + (a + b - 1) / 2.0, int(lens[a:b].max()), (span[0] + a, span[0] + b), start, step))
    return out


def match_labels(P, vals):
    """Match printed labels (in position order) to candidate positions P: the linear map through
    some pair of candidates that puts the most labels on a candidate (within 3% of the smallest
    label spacing), least total offset on ties. Returns [(label index, position)]."""
    P = sorted(P)
    n = len(vals)
    best = (0, 1e9, [])
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            for a in range(n):
                for b in range(a + 1, n):
                    s = (P[j] - P[i]) / (vals[b] - vals[a])        # px per unit of label value
                    gaps = [abs(vals[t + 1] - vals[t]) * abs(s) for t in range(n - 1)]
                    if min(gaps) < 40:
                        continue
                    tol = 0.03 * min(gaps)
                    got, res = [], 0.0
                    for t in range(n):
                        q = P[i] + (vals[t] - vals[a]) * s
                        k = min(P, key=lambda p: abs(p - q))
                        if abs(k - q) <= tol:
                            got.append((t, k))
                            res += abs(k - q)
                    if len(got) > best[0] or (len(got) == best[0] and res < best[1]):
                        best = (len(got), res, got)
    return best[2]


def _fit(marks):
    p = np.array([m[0] for m in marks], float)
    v = np.array([m[1] for m in marks], float)
    b, a = np.polyfit(p, v, 1)
    mis = float(np.max(np.abs((v - (a + b * p)) / b)))
    if mis > 8.0:
        raise RuntimeError(f"calibration misfit {mis:.1f} px: {marks}")
    return a, b, max(mis, 0.5)


def calibrate(image, cfg):
    ink = ink_mask(image)
    bx = plot_box(ink)
    cal = dict(ink=ink, bx=bx, cands=[])
    for axis, labels, side in (("x", cfg["X"], cfg.get("x_side", "bottom")),
                               ("y", cfg["Y"], cfg.get("y_side", "left"))):
        cands = tick_candidates(ink, bx, side)
        cal["cands"] += cands
        P = [c[0] for c in cands]
        # labels printed at a corner of the box: that border's centre is the mark
        corners = [(bx[k], v) for k, v in cfg.get(axis.upper() + "c", {}).items()]
        # in position order: x grows to the right; rows grow downwards, so y labels largest first
        vals = sorted(labels) if axis == "x" else sorted(labels, reverse=True)
        if len(corners) >= 2:
            # the corners fix the scale: each tick label takes the candidate nearest its predicted place
            (p1, v1), (p2, v2) = corners[:2]
            s = (p2 - p1) / (v2 - v1)
            gap = min(abs(vals[t + 1] - vals[t]) * abs(s) for t in range(len(vals) - 1)) if len(vals) > 1 else abs(p2 - p1)
            got = []
            for t, v in enumerate(vals):
                q = p1 + (v - v1) * s
                if P:
                    k = min(P, key=lambda p: abs(p - q))
                    if abs(k - q) <= 0.06 * gap:
                        got.append((t, k))
            need = max(1, len(vals) - 1)
        else:
            got = match_labels(P, vals)
            need = max(2, len(vals) - 1)
        if len(got) < need:
            raise RuntimeError(f"{axis}: matched {got} of {vals} among {sorted(P)}")
        marks = [(p, vals[t]) for t, p in got] + corners
        a, b, mis = _fit(marks)
        cal[axis] = (a, b, mis, marks)
    return cal


def interior(cal, legend=None, margin=8):
    """Ink inside the box: the borders (with `margin` px more, for the uneven edges of the
    scanned lines), the tick marks and the legend region removed."""
    bx = cal["bx"]
    m = cal["ink"].copy()
    m[:, : bx["l1"] + 1 + margin] = False
    m[:, bx["r0"] - margin:] = False
    m[: bx["t1"] + 1 + margin, :] = False
    m[bx["b0"] - margin:, :] = False
    for pos, ln, (a, b), start, step in cal["cands"]:
        # remove the tick marks themselves (2 px beyond each side)
        lo, hi = sorted((start, start + step * (ln + 2)))
        if start in (bx["b0"] - 1, bx["t1"]):
            m[lo:hi + 1, a - 2:b + 2] = False
        else:
            m[a - 2:b + 2, lo:hi + 1] = False
    if legend is not None:
        c0, r0, c1, r1 = legend
        m[r0:r1, c0:c1] = False
    return m


def tracks(m, c):
    win = m[:, max(c - W, 0): c + W + 1].any(axis=1)
    out = []
    for a, b in _runs(win):
        if out and a - out[-1][1] <= GAP:
            out[-1] = (out[-1][0], b)
        else:
            out.append((a, b))
    return out


def read_tracks(image, at, cfg):
    cal = calibrate(image, cfg)
    xa, xb, xmis, _ = cal["x"]
    ya, yb, ymis, _ = cal["y"]
    m = interior(cal, cfg.get("legend"))
    out = []
    for x in at:
        x = float(x)
        col = (x - xa) / xb
        c = int(round(col))
        tr = tracks(m, c)
        rule = next((r for r in cfg["rules"] if r[0] - 1e-9 <= x <= r[1] + 1e-9
                     and (r[3] is None or r[3] == len(tr))), None)
        if rule is None:
            out.append({"x": x, "y": None, "note": f"{len(tr)} tracks of ink here; no rule takes one"})
            continue
        rank = rule[2]
        if not tr or not (-len(tr) <= rank < len(tr)):
            out.append({"x": x, "y": None, "note": f"no track {rank} among {len(tr)}"})
            continue
        a, b = tr[rank]
        nar = m[a:b, max(c - 2, 0): c + 3].any(axis=1)
        rows = np.flatnonzero(nar)
        narrow = len(rows) > 0
        a2, b2 = (a + rows.min(), a + rows.max() + 1) if narrow else (a, b)
        if b2 - a2 > STEEP:
            out.append({"x": x, "y": None, "note": f"track {b2 - a2} px tall: a near-vertical stretch"})
            continue
        row = (a2 + b2 - 1) / 2.0
        sl = 0.0
        nb = []
        for k in (c - 2 * W, c + 2 * W):
            tk = [t for t in tracks(m, k) if t[0] - 30 <= row <= t[1] + 30]
            if len(tk) == 1:
                nb.append((tk[0][0] + tk[0][1]) / 2.0)
        if len(nb) == 2:
            sl = abs(nb[1] - nb[0]) / (4.0 * W)
        e = (b - a) / 2.0 + BLUR + ymis + sl * xmis
        y, lo, hi = ya + yb * row, ya + yb * (row + e), ya + yb * (row - e)
        out.append({"x": x, "y": float(y), "lo": float(min(lo, hi)), "hi": float(max(lo, hi)),
                    "px": [float(col), float(row)], "px_lo": float(row - e), "px_hi": float(row + e),
                    "note": f"track {rank} of {len(tr)}, {b - a} px tall in the window"
                            f"{'' if narrow else ' (no ink in the centre columns)'}"})
    return out


def load(name):
    import importlib.util
    import os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    spec = importlib.util.spec_from_file_location(os.path.splitext(name)[0], p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
