"""Shared reading code for the figures of panzetta2019 (Excel charts pasted as raster images).

Each reading file here names one panel, one series (by its colour in the image) and the
printed axis labels, and calls `read_spec`. Everything else is found in the image:

  axes    the spines are the leftmost long dark vertical line and the lowest long dark
          horizontal line of the crop. These charts have no tick marks, so each axis is
          calibrated from its printed labels: the labels are the blocks of dark text just
          left of the vertical spine (one band of rows per label) and just below the
          horizontal spine (one group of columns per label). Excel centres each label on its
          value, so the label's centre is the value's pixel. The label centres are matched,
          in pixel order, to the printed labels the stub gives (the only paper values used);
          a least-squares line (linear or log10) of pixel against value is the calibration,
          and its largest residual (at least one pixel) is the misfit.
  series  pixels within a colour tolerance of the series' colour and nearer to it than to
          any other colour of the panel, inside the plot box. Per column, the centre and the
          extent of those pixels. At a position x: the columns within +-2 px; if none, the
          nearest columns on either side within `gap` px, interpolated linearly (markers are
          spaced, and other series may hide some); otherwise no value.

Intervals (95%): half the extent of the marker or line (the extent of all the series' pixels
in those columns, so a steep part or stacked markers widen it), half the jump across an
interpolated gap, the y misfit, one pixel, and the local slope times the x misfit.
"""
from itertools import combinations

import numpy as np


def gray(img):
    return img.astype(float).mean(axis=2)


def sat(img):
    f = img.astype(float)
    return f.max(axis=2) - f.min(axis=2)


def _groups(idx, gap=1):
    idx = np.asarray(sorted(idx))
    if len(idx) == 0:
        return []
    cut = np.where(np.diff(idx) > gap)[0] + 1
    return [g for g in np.split(idx, cut) if len(g)]


def _longest(v, gap=3):
    best, bs = 0, 0
    for g in _groups(np.where(v)[0], gap=gap):
        n = int(g[-1] - g[0] + 1)
        if n > best:
            best, bs = n, int(g[0])
    return best, bs


# ------------------------------------------------------------------ axes

def spines(img, thr=170, frac=0.4):
    m = (gray(img) < thr) & (sat(img) < 60)
    H, W = m.shape
    vc = {}
    for c in range(W):
        n, s = _longest(m[:, c], gap=80)   # a marker drawn over the spine interrupts it
        # ...but a spine is solid: rotated title text bridged by the gap is not
        if n >= frac * H and m[s:s + n, c].sum() >= 0.9 * n:
            vc[c] = (n, s)
    hr = {}
    for r in range(H):
        n, s = _longest(m[r])
        if n >= frac * W:
            hr[r] = (n, s)
    if not vc or not hr:
        raise ValueError("axis spines not found")
    g = _groups(list(vc), gap=2)[0]
    n, s = max(vc[c] for c in g)
    left = {"c0": int(min(g)), "c1": int(max(g)), "r0": s, "r1": s + n}
    g = _groups(list(hr), gap=2)[-1]
    n, s = max(hr[r] for r in g)
    bottom = {"r0": int(min(g)), "r1": int(max(g)), "c0": s, "c1": s + n}
    return {"left": left, "bottom": bottom}


def _block(present, start, step, gap, limit):
    """From `start`, moving by `step`, the first stretch of present indices, ending at a gap > `gap`."""
    i, first, last, miss = start, None, None, 0
    while 0 <= i < limit:
        if present[i]:
            if first is None:
                first = i
            last, miss = i, 0
        elif first is not None:
            miss += 1
            if miss > gap:
                break
        i += step
    if first is None:
        return None
    return (min(first, last), max(first, last))


def y_label_centres(img, sp, thr=130, col_gap=30, min_h=12, above=120, below=70, smax=80):
    m = (gray(img) < thr) & (sat(img) < smax)
    H, W = m.shape
    r0 = max(sp["left"]["r0"] - above, 0)
    r1 = min(sp["bottom"]["r0"] + below, H)
    present = m[r0:r1].any(axis=0)
    start = sp["left"]["c0"] - 4
    while True:
        blk = _block(present, start, -1, col_gap, W)
        if blk is None:
            raise ValueError("no y labels found")
        if blk[1] - blk[0] + 1 >= 20:      # narrower: the fringe of the spine or of a marker on it
            break
        start = blk[0] - 1
    rows = m[r0:r1, blk[0]:blk[1] + 1].any(axis=1)
    out = []
    for g in _groups(np.where(rows)[0], gap=4):
        if g[-1] - g[0] + 1 >= min_h:
            out.append(r0 + (g[0] + g[-1] + 1) / 2.0)
    return out


def x_label_centres(img, sp, thr=130, row_gap=8, col_gap=30, min_w=8, smax=80):
    m = (gray(img) < thr) & (sat(img) < smax)
    H, W = m.shape
    c_right = sp["left"]["c1"] + 20
    present = m[:, c_right:].any(axis=1)
    blk = _block(present, sp["bottom"]["r1"] + 4, 1, row_gap, H)
    if blk is None:
        raise ValueError("no x labels found")
    cols = m[blk[0]:blk[1] + 1].any(axis=0)
    out = []
    for g in _groups(np.where(cols)[0], gap=col_gap):
        centre = (g[0] + g[-1] + 1) / 2.0
        # the first x label is centred on the vertical spine; a group further left is a y label
        if g[-1] - g[0] + 1 >= min_w and centre >= sp["left"]["c0"] - 30:
            out.append(centre)
    return out


def fit_axis(pix, labels, scale):
    vals = np.array([np.log10(v) if scale == "log10" else v for v in labels], float)
    pix = sorted(pix)
    n = len(vals)
    if len(pix) < n:
        raise ValueError(f"found {len(pix)} labels in the image for {n} printed labels")
    best = None
    for sub in ([pix] if len(pix) == n else combinations(pix, n)):
        p = np.array(sub)
        b, a = np.polyfit(vals, p, 1)
        res = float(np.max(np.abs(p - (a + b * vals))))
        if best is None or res < best[0]:
            best = (res, a, b, list(p))
    res, a, b, used = best
    return {"a": a, "b": b, "misfit": max(res, 1.0), "scale": scale, "marks": used}


def to_px(ax, v):
    u = np.log10(v) if ax["scale"] == "log10" else v
    return ax["a"] + ax["b"] * u


def to_val(ax, p):
    u = (p - ax["a"]) / ax["b"]
    return float(10 ** u) if ax["scale"] == "log10" else float(u)


def calibrate(img, spec):
    sp = spines(img, spec.get("spine_thr", 170), spec.get("spine_frac", 0.4))
    # label_sat: the largest colour saturation of label text (a low value keeps coloured markers on
    # a spine out of the labels; a compressed raster's black text can carry colour noise)
    smax = spec.get("label_sat", 80)
    xa = fit_axis(x_label_centres(img, sp, col_gap=spec.get("x_col_gap", 30), smax=smax),
                  spec["x"]["labels"], spec["x"].get("scale", "linear"))
    # y_below < 0 stops the y labels above the lowest one, where it meets the x axis' first label
    ya = fit_axis(y_label_centres(img, sp, below=spec.get("y_below", 70), smax=smax), spec["y"]["labels"],
                  spec["y"].get("scale", "linear"))
    box = (sp["left"]["c1"] + 1, sp["left"]["r0"], sp["bottom"]["c1"], sp["bottom"]["r0"])
    return {"x": xa, "y": ya, "box": box, "spines": sp}


# ------------------------------------------------------------------ series

def colour_mask(img, colors, others=(), tol=70):
    f = img.astype(float)
    m = np.zeros(img.shape[:2], bool)
    for color in colors:
        d = np.sqrt(((f - np.array(color, float)) ** 2).sum(axis=2))
        mc = d < tol
        for o in others:
            mc &= d <= np.sqrt(((f - np.array(o, float)) ** 2).sum(axis=2))
        m |= mc
    return m


def _columns(mask):
    cols = {}
    for c in np.where(mask.any(axis=0))[0]:
        rows = np.where(mask[:, c])[0]
        cols[int(c)] = (float(rows.min()), float(rows.max() + 1))
    return cols


def _trace(mask, min_run=2, max_jump=25):
    """For a line: per column the runs of the mask; the line is followed from the longest stretch of
    columns holding exactly one run, keeping in each column the run nearest the previous centre
    (within max_jump px, plus 2 px per column missed). Pixels of the same colour off
    the line (another line's antialiased edge, a label) are not followed."""
    runs = {}
    for c in np.where(mask.any(axis=0))[0]:
        rs = [(float(g[0]), float(g[-1] + 1)) for g in _groups(np.where(mask[:, c])[0], gap=1)
              if g[-1] - g[0] + 1 >= min_run]
        if rs:
            runs[int(c)] = rs
    single = [c for c, rs in runs.items() if len(rs) == 1]
    if not single:
        return {}
    best = max(_groups(single, gap=1), key=len)
    start = int(best[len(best) // 2])
    out = {start: runs[start][0]}
    lo, hi = min(runs), max(runs)
    for d in (1, -1):
        prev, miss, c = 0.5 * sum(out[start]), 0, start + d
        while lo <= c <= hi:
            rs = runs.get(c, [])
            if rs:
                r = min(rs, key=lambda t: abs(0.5 * (t[0] + t[1]) - prev))
                if abs(0.5 * (r[0] + r[1]) - prev) <= max_jump + 2 * miss + 0.5 * (r[1] - r[0]):
                    out[c] = r
                    prev, miss = 0.5 * (r[0] + r[1]), 0
                else:
                    miss += 1
            else:
                miss += 1
            if miss > 150:                       # an arrow drawn across the line hides it
                break
            c += d
    return out


def read_curve(img, spec, at):
    cal = calibrate(img, spec)
    xa, ya = cal["x"], cal["y"]
    c0, r0, c1, r1 = cal["box"]
    pad = spec.get("inset", 6)
    colors = spec.get("colors") or [spec["color"]]
    others = [o for o in spec.get("others", ()) if tuple(o) not in {tuple(c) for c in colors}]
    m = colour_mask(img, colors, others, spec.get("tol", 70))
    keep = np.zeros_like(m)
    keep[int(r0):int(r1) - pad, int(c0) + pad:int(c1) + spec.get("right_extra", 0)] = True
    for (a, b, c, d) in spec.get("blank", []):
        keep[b:d, a:c] = False
    m &= keep
    if spec.get("min_area"):
        # markers are solid blobs; the antialiased rim of another series' marker is a thin ring of
        # mixed colour, smaller than any marker
        from scipy import ndimage
        lab, n = ndimage.label(m)
        if n:
            area = ndimage.sum(m, lab, index=np.arange(1, n + 1))
            m &= np.isin(lab, np.arange(1, n + 1)[area >= spec["min_area"]])
    # drop specks smaller than min_px pixels per column
    cols = {c: v for c, v in _columns(m).items() if m[:, c].sum() >= spec.get("min_px", 3)}
    if spec.get("trace"):
        cols = _trace(m, spec.get("min_run", 2), spec.get("max_jump", 25))
    gap = spec.get("gap", 60)
    out = []
    for x in at:
        col = float(to_px(xa, x))
        near = [c for c in cols if abs(c + 0.5 - col) <= 2]
        extra, how = 0.0, ""
        if near:
            top = min(cols[c][0] for c in near)
            bot = max(cols[c][1] for c in near)
            cen = 0.5 * (top + bot)
            ext = bot - top
        else:
            left = [c for c in cols if col - gap <= c + 0.5 < col]
            right = [c for c in cols if col < c + 0.5 <= col + gap]
            if not left or not right:
                out.append({"x": float(x), "y": None,
                            "note": f"no pixel of this series within {gap} px on both sides of this x"})
                continue
            cl_, cr_ = max(left), min(right)
            yl, yr = 0.5 * sum(cols[cl_]), 0.5 * sum(cols[cr_])
            w = (col - (cl_ + 0.5)) / (cr_ - cl_)
            cen = (1 - w) * yl + w * yr
            ext = max(cols[cl_][1] - cols[cl_][0], cols[cr_][1] - cols[cr_][0])
            extra = 0.5 * abs(yr - yl)
            how = f"; interpolated across a gap of {cr_ - cl_} columns"
        half = 0.5 * ext + extra + ya["misfit"] + 1.0
        side = sorted(c for c in cols if abs(c + 0.5 - col) <= 40)
        if len(side) > 2:
            ys_ = np.array([0.5 * sum(cols[c]) for c in side])
            slope = abs(float(np.polyfit(np.array(side, float), ys_, 1)[0]))
            half += slope * xa["misfit"]
        y = to_val(ya, cen)
        a1, a2 = to_val(ya, cen - half), to_val(ya, cen + half)
        out.append({"x": float(x), "y": y, "lo": min(a1, a2), "hi": max(a1, a2), "px": [col, cen],
                    "px_lo": cen - half, "px_hi": cen + half,
                    "note": f"extent {ext:.0f} px; x misfit {xa['misfit']:.1f} px ({len(xa['marks'])} labels), "
                            f"y misfit {ya['misfit']:.1f} px ({len(ya['marks'])} labels)" + how})
    return out


def read_spec(image, at, spec):
    return read_curve(image, spec, at)
