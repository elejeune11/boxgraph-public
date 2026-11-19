CONFIG = {'bar_dark': 150,
 'bar_lw': 8,
 'bars': True,
 'dark': 110,
 'edge': 1.15,
 'exclude': [[400, 1780, 1000, 2040]],
 'kind': 'open',
 'r': 34,
 'thr_open': 0.7,
 'x_labels': {'values': [0, 5, 10, 15, 20, 25, 30, 35, 40], 'which': 'all'},
 'x_ticks_out': True,
 'y_axis': 'left',
 'y_labels': {'reverse': True, 'values': [0.5, 1, 1.5, 2, 2.5, 3, 3.5], 'which': 'all'},
 'y_ticks_out': True}

# ---- reading code (shared by this record's marker readings; only CONFIG above differs) ----
# Everything is found in the image: axis spines and tick marks (matched to the printed tick labels in
# CONFIG), the markers (filled discs or open rings, by template matching on the dark-ink mask) and the
# vertical error bars (walked along the marker's column in the bar-ink mask).
import numpy as np
from scipy import ndimage as ndi


def _gray(image):
    return np.asarray(image, dtype=float)[..., :3].mean(axis=2)


def _runs(v):
    out, start = [], None
    for i, b in enumerate(list(v) + [False]):
        if b and start is None:
            start = i
        elif not b and start is not None:
            out.append((start, i))
            start = None
    return out


def _spines(dark):
    """Rows and columns of the plot box: the longest dark lines."""
    H, W = dark.shape
    rowlen = np.array([max([e - s for s, e in _runs(dark[r])] or [0]) for r in range(H)])
    collen = np.array([max([e - s for s, e in _runs(dark[:, c])] or [0]) for c in range(W)])
    hrows = [r for r in range(H) if rowlen[r] > 0.5 * W]
    vcols = [c for c in range(W) if collen[c] > 0.5 * H]
    groups = lambda xs: [(g[0], g[-1]) for g in np.split(np.array(xs), np.where(np.diff(xs) > 1)[0] + 1)]
    return groups(hrows), groups(vcols)


def _ticks_on(dark, line, along, side, span, min_len=12, max_len=80):
    """Tick marks on one spine: short dark runs leaving the spine on one side.
    line = (first, last) pixel of the spine; along = 'row' (a horizontal spine) or 'col'."""
    found = []
    lo, hi = span
    for p in range(lo, hi):
        if along == "row":  # horizontal spine: ticks are vertical runs in column p
            col = dark[:, p]
            seq = col[line[1] + 1:] if side > 0 else col[:line[0]][::-1]
        else:
            row = dark[p, :]
            seq = row[line[1] + 1:] if side > 0 else row[:line[0]][::-1]
        k = 0
        while k < 2 and k < len(seq) and not seq[k]:  # a tick may sit a pixel off the spine
            k += 1
        n = 0
        while k + n < len(seq) and seq[k + n]:
            n += 1
        found.append(n if min_len <= n <= max_len else 0)
    found = np.array(found)
    ticks = []
    for s, e in _runs(found > 0):
        if e - s <= 20:
            ticks.append((lo + (s + e - 1) / 2 + 0.5, int(found[s:e].max())))
    return ticks


def _axis(ticks, labels):
    """Fit value = a + b * pixel through the labelled (major) ticks; labels map tick order to values."""
    if not ticks:
        raise ValueError("no tick marks found")
    longest = max(n for _, n in ticks)
    major = sorted(p for p, n in ticks if n >= 0.75 * longest)
    minor = sorted(p for p, n in ticks if n < 0.75 * longest)
    sel = major if labels["which"] == "major" else sorted(major + minor)
    if labels.get("reverse"):
        sel = sel[::-1]
    vals = labels["values"]
    if len(sel) < len(vals):
        raise ValueError(f"found {len(sel)} ticks, need {len(vals)}")
    sel = sel[labels.get("skip", 0):labels.get("skip", 0) + len(vals)]
    p, v = np.array(sel), np.array(vals, dtype=float)
    b, a = np.polyfit(p, v, 1)
    misfit = float(np.max(np.abs(p - (v - a) / b)))
    return a, b, max(misfit, 0.5), sel


def _disk(r):
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return (x * x + y * y <= r * r).astype(float)


def _ring(ri, ro):
    y, x = np.mgrid[-ro:ro + 1, -ro:ro + 1]
    rr = x * x + y * y
    return ((rr <= ro * ro) & (rr >= ri * ri)).astype(float)


def _corr(mask, k):
    from scipy.signal import fftconvolve
    return fftconvolve(mask.astype(float), k[::-1, ::-1], mode="same") / k.sum()


def _markers(dark, cfg, box):
    R = cfg["r"]
    if cfg["kind"] == "filled":
        score = _corr(dark, _disk(int(0.8 * R)))
        ok = score > cfg.get("thr", 0.93)
    elif cfg["kind"] == "filled_upper_half":
        # a filled disc whose lower half is covered by an open marker drawn over it: the upper half-disc
        k = _disk(int(0.8 * R))
        k[int(0.8 * R) + 1:, :] = 0
        score = _corr(dark, k)
        ok = score > cfg.get("thr", 0.97)
    else:
        ri, ro = cfg.get("ring", (0.6, 0.95))
        ring = _corr(dark, _ring(int(ri * R), int(ro * R)))
        inner = _corr(dark, _disk(int(0.35 * R)))
        score = ring - inner
        ok = (score > cfg.get("thr", 0.45)) & (inner < cfg.get("inner_max", 0.2))
    c0, r0, c1, r1 = box
    inside = np.zeros_like(ok)
    inside[int(r0) + 3:int(r1) - 3, int(c0) + 3:int(c1) - 3] = True
    for (a0, b0, a1, b1) in cfg.get("exclude", []):  # legend, inset: layout of the image, not data
        inside[b0:b1, a0:a1] = False
    ok &= inside
    peak = ndi.maximum_filter(np.where(ok, score, -1), size=int(1.2 * R)) == score
    lab, n = ndi.label(ok & peak)
    pts = []
    for k in range(1, n + 1):
        rr, cc = np.nonzero(lab == k)
        r, c = rr.mean(), cc.mean()
        # refine: score-weighted centroid in a small window
        w0, w1 = int(r) - 4, int(r) + 5
        v0, v1 = int(c) - 4, int(c) + 5
        win = np.clip(score[w0:w1, v0:v1] - score[w0:w1, v0:v1].max() * 0.98, 0, None)
        if win.sum() > 0:
            yy, xx = np.mgrid[w0:w1, v0:v1]
            r, c = (yy * win).sum() / win.sum(), (xx * win).sum() / win.sum()
        pts.append((c + 0.5, r + 0.5, float(score[int(r), int(c)])))
    if cfg["kind"] == "open":  # an open marker is a closed ring: ink in every direction from its centre
        def closed(c, r):
            n = 0
            for k in range(24):
                a = 2 * np.pi * k / 24
                hit = False
                for rad in range(int(0.65 * R), R + 1):
                    x, y = int(c + rad * np.cos(a)), int(r + rad * np.sin(a))
                    if 0 <= y < dark.shape[0] and 0 <= x < dark.shape[1] and dark[y, x]:
                        hit = True
                        break
                n += hit
            return n >= cfg.get("closed_min", 23)
        pts = [p for p in pts if any(closed(p[0] - 0.5 + dc, p[1] - 0.5 + dr)
                                     for dc in (-4, 0, 4) for dr in (-6, -3, 0, 3, 6))]
    pts.sort()
    merged = []
    for p in pts:  # one marker, one point
        if merged and abs(p[0] - merged[-1][0]) < R and abs(p[1] - merged[-1][1]) < R:
            if p[2] > merged[-1][2]:
                merged[-1] = p
            continue
        merged.append(p)
    return merged


def _walk(barmask, col, start, step, stop_rows, gap=4, band=3):
    """From row `start`, follow the bar ink along column `col` (within +-band) while it continues
    (bridging gaps of `gap` rows). Returns the last ink row, or None if there is no ink. Stops with
    'blocked' if the walk enters another marker (rows in stop_rows)."""
    c0, c1 = int(col) - band, int(col) + band + 1
    r, last, miss = start, None, 0
    H = barmask.shape[0]
    while 0 <= r < H:
        if r in stop_rows:
            return last, True
        if barmask[r, c0:c1].any():
            last, miss = r, 0
        else:
            miss += 1
            if miss > gap:
                break
        r += step
    return last, False


def read(image, at):
    cfg = CONFIG
    g = _gray(image)
    dark = g < cfg["dark"]
    hs, vs = _spines(dark)
    xrow = hs[-1]                      # the x axis: lowest long horizontal line
    ycol_left, ycol_right = vs[0], vs[-1]
    box = (ycol_left[1] + 1, hs[0][1] + 1 if len(hs) > 1 else 0, ycol_right[0], xrow[0])
    xt = _ticks_on(dark, xrow, "row", +1 if cfg["x_ticks_out"] else -1, (ycol_left[1] + 1, ycol_right[0]))
    xa, xb, xmis, xsel = _axis(xt, cfg["x_labels"])
    spine = ycol_right if cfg["y_axis"] == "right" else ycol_left
    side = +1 if cfg["y_axis"] == "right" else -1
    if not cfg["y_ticks_out"]:
        side = -side
    yt = _ticks_on(dark, spine, "col", side, (int(box[1]) + 2, xrow[0] - 4))
    ya, yb, ymis, ysel = _axis(yt, cfg["y_labels"])
    R = cfg["r"]
    def kind_cfg(kind):
        k = {key: v for key, v in cfg.items() if key != "thr"}
        k["kind"] = kind
        if cfg.get("thr_" + kind) is not None:
            k["thr"] = cfg["thr_" + kind]
        return k

    def find(kind):
        pts = [(c, r, s, "") for c, r, s in _markers(dark, kind_cfg(kind), box)]
        if kind == "filled" and cfg.get("half_filled"):
            ring_pts = _markers(dark, kind_cfg("open"), box)
            for c, r, s in _markers(dark, kind_cfg("filled_upper_half"), box):
                # only where an open marker sits just below and no full disc was found
                if any(abs(c - a) < R and abs(r - b) < R for a, b, _, _ in pts):
                    continue
                if not any(abs(c - a) < 0.5 * R and 0.5 * R < b - r < 2.2 * R for a, b, _ in ring_pts):
                    continue
                pts.append((c, r, s, "lower half covered by the open marker drawn over it; centre from the "
                                     "upper half-disc, so the centre is less certain"))
        return sorted(pts)

    pts = find(cfg["kind"])
    barmask = g < cfg["bar_dark"]
    # every marker of either kind, so a bar walk stops when it reaches another marker
    others = [(c, r, kind) for kind in ("filled", "open") for c, r, _, _ in find(kind)]
    out = []
    for c, r, s, extra in pts:
        x = xa + xb * c
        y = ya + yb * r
        e = cfg.get("centre_px", 3.0) * (3 if extra else 1) + ymis   # centre location and calibration, px
        lo, hi = sorted([ya + yb * (r - e), ya + yb * (r + e)])
        row = {"x": round(float(x), 4), "y": float(y), "lo": float(lo), "hi": float(hi), "px": [float(c), float(r)],
               "note": f"{cfg['kind']} marker, score {s:.2f}; x from the marker centre "
                       f"(x misfit {xmis:.1f} px, y misfit {ymis:.1f} px)" + (f"; {extra}" if extra else "")}
        if cfg.get("bars"):
            blockers_up = set()
            blockers_dn = set()
            for oc, orow, _ in others:
                if abs(oc - c) < R and abs(orow - r) > 0.5 * R:   # another marker in this column
                    rows = set(range(int(orow - 0.9 * R), int(orow + 0.9 * R) + 1))
                    (blockers_up if orow < r else blockers_dn).update(rows)
            edge = int(cfg.get("edge", 1.0) * R)
            up, bl_up = _walk(barmask, c, int(r) - edge, -1, blockers_up)
            dn, bl_dn = _walk(barmask, c, int(r) + edge, +1, blockers_dn)
            lw = cfg.get("bar_lw", 6)
            # bar ends: the outer edge of the cap, less half its line width; a bar hidden in the marker
            # (no ink outside it) is at most the marker
            top = (up + 0.5 + lw / 2) if (up is not None and not bl_up) else None
            bot = (dn + 0.5 - lw / 2) if (dn is not None and not bl_dn) else None
            hidden_top = up is None and not bl_up
            hidden_bot = dn is None and not bl_dn
            if hidden_top:
                top = r - R
            if hidden_bot:
                bot = r + R
            notes = []
            if top is None and bot is not None:
                top = 2 * r - bot
                notes.append("upper end runs into another marker: taken as the mirror of the lower end")
            if bot is None and top is not None:
                bot = 2 * r - top
                notes.append("lower end runs into another marker: taken as the mirror of the upper end")
            if top is None and bot is None:
                top, bot = r - R, r + R
                notes.append("both ends run into other markers: reported as at most the marker")
            if hidden_top or hidden_bot:
                notes.append("bar hidden in the marker at the " + ("top" if hidden_top else "")
                             + (" and " if hidden_top and hidden_bot else "") + ("bottom" if hidden_bot else "")
                             + ": that end is at most the marker edge")
            pad = lw + ymis
            v_top, v_bot = ya + yb * top, ya + yb * bot
            row.update(bar_lo=float(min(v_top, v_bot)), bar_hi=float(max(v_top, v_bot)),
                       bar_lo_outer=float(min(ya + yb * (top - pad), ya + yb * (bot + pad))),
                       bar_hi_outer=float(max(ya + yb * (top - pad), ya + yb * (bot + pad))),
                       px_lo=float(top), px_hi=float(bot))
            # keep the interval covering the bar is not wanted: lo/hi stay the centre's precision
            if notes:
                row["note"] += "; " + "; ".join(notes)
        out.append(row)
    return out
