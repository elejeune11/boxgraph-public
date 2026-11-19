"""Shared reading code for Fig. 5 (PDF p. 6) and Fig. 8 (PDF p. 8): coloured curves on linear axes.

Everything is found in the rendered crop:
- black = all channels below 60 (the axes, ticks and digits are black; the grey branches of
  Fig. 5 are (102, 102, 102) and are not black).
- y axis: the column with the longest black run; x axis: the row with the longest black run;
  axis line width lw: the neighbouring columns of the y axis with at least half that run.
- x ticks: short black runs (at most 3 lw wide) standing on the x axis (black 1.5-4 lw above it),
  more than 10 lw right of the y axis. Their spacing is the median gap; they sit on a regular
  grid from the y axis (x = 0); the caller gives the x step per tick, matched to the printed
  labels (0, 0.2, 0.4, ... under every second tick in both figures: 0.1 per tick). The x scale
  is the least-squares line through the y axis and the ticks; its largest residual is the x misfit.
- y ticks: short black runs left of the y axis (1.5-4 lw), above the x axis, kept on the regular
  grid that holds the most of them. The ticks with digits to their left are the labelled ones,
  matched from the top with the values the caller gives (those printed). The y scale is fitted
  through them; the misfit is the largest distance of any tick from its regular grid (in y units)
  or of a labelled tick from the fit, whichever is larger.
- curves: the pixels within 30 of the curve's exact colour in every channel (the figures use flat
  colours); connected parts are labelled and the caller says which parts are the curve.
Value at x: the middle of the curve's run in each of the 7 columns around x, median over them.
Interval: 2 px + a quarter of the run length (steep curves are less sharply located), in y units,
plus the y misfit, plus the local slope times the x misfit.
"""
import numpy as np
from scipy import ndimage as ndi


def _groups(idx):
    out = []
    for c in idx:
        if out and c - out[-1][-1] <= 1:
            out[-1].append(int(c))
        else:
            out.append([int(c)])
    return out


def _longest(v):
    best = cur = 0
    for b in v:
        cur = cur + 1 if b else 0
        best = max(best, cur)
    return best


def _grid(t, sp, tol=0.1):
    t = np.array(sorted(t))

    def on(r):
        q = (t - r) / sp
        return int(np.sum(np.abs(q - np.round(q)) < tol))
    ref = max(t, key=on)
    q = (t - ref) / sp
    return t[np.abs(q - np.round(q)) < tol]


def calibrate(image, y_labels, x_step):
    img = np.asarray(image).astype(int)
    blk = img.max(axis=2) < 60
    H, W = blk.shape
    colrun = np.array([_longest(blk[:, c]) for c in range(W)])
    rowrun = np.array([_longest(blk[r, :]) for r in range(H)])
    c_axis = int(np.argmax(colrun))
    r_axis = int(np.argmax(rowrun))
    near = np.where(colrun[max(c_axis - 15, 0): c_axis + 16] >= 0.5 * colrun[c_axis])[0]
    lw = max(2, len(near))
    a, b = int(1.5 * lw), 4 * lw

    above = blk[r_axis - b: r_axis - a, :].mean(0) > 0.5
    cols = np.where(above)[0]
    cols = cols[cols > c_axis + 10 * lw]
    cand = [float(np.mean(g)) for g in _groups(cols) if len(g) <= 3 * lw]
    sp = float(np.median(np.diff(cand)))
    xt = np.array(cand)
    k = np.round((xt - c_axis) / sp)
    ok = np.abs((xt - c_axis) / sp - k) < 0.1
    xt, k = xt[ok], k[ok]
    xv = np.concatenate([[0.0], k * x_step])
    xc = np.concatenate([[c_axis], xt])
    cpu, c0 = np.polyfit(xv, xc, 1)
    xmis = float(np.max(np.abs(c0 + cpu * xv - xc)) / cpu)

    left = blk[:, c_axis - b: c_axis - a].mean(1) > 0.5
    rows = np.where(left)[0]
    rows = rows[rows < r_axis - 3 * lw]
    yt = [float(np.mean(g)) for g in _groups(rows) if len(g) <= 3 * lw]
    ysp = float(np.median(np.diff(yt)))
    yt = _grid(yt, ysp)
    lab = []
    for t in yt:
        win = blk[max(int(t - ysp / 3), 0): int(t + ysp / 3), max(int(c_axis - 1.25 * ysp), 0): int(c_axis - 0.25 * ysp)]
        if win.sum() > 4 * lw * lw:
            lab.append(t)
    assert len(lab) == len(y_labels), (lab, list(yt))
    slope, icpt = np.polyfit(np.array(lab), np.array(y_labels, dtype=float), 1)
    kk = np.round((yt - yt[0]) / ysp)
    gsp, g0 = np.polyfit(kk, yt, 1)
    ymis = max(float(np.max(np.abs(g0 + gsp * kk - yt))) * abs(slope),
               float(np.max(np.abs(icpt + slope * np.array(lab) - np.array(y_labels)))))
    return dict(img=img, c_axis=c_axis, r_axis=r_axis, lw=lw, c0=float(c0), cpu=float(cpu), xmis=xmis,
                a=float(icpt), b=float(slope), ymis=ymis, nxt=len(xt), nyt=len(yt), nlab=len(lab))


def colour_parts(cal, rgb, tol=30):
    m = np.abs(cal["img"] - np.array(rgb)).max(axis=2) < tol
    lab, n = ndi.label(m)
    sizes = ndi.sum(m, lab, range(1, n + 1)) if n else np.array([])
    order = list(np.argsort(-sizes) + 1)
    return m, lab, order, sizes


def note(cal, what):
    return (f"{what}; x: y axis + {cal['nxt']} ticks, 1 unit = {cal['cpu']:.0f} px, misfit {cal['xmis']:.4f}; "
            f"y: {cal['nlab']} labelled of {cal['nyt']} ticks, misfit {cal['ymis']:.3f}")


def _centre(mask, c):
    r = np.where(mask[:, c])[0]
    if len(r) == 0:
        return None
    g = max(_groups(r), key=len)
    return (g[0] + g[-1]) / 2.0, len(g)


def read_mask(cal, mask, at, what):
    out = []
    for x in at:
        col = cal["c0"] + cal["cpu"] * x
        ci = int(round(col))
        got = [g for g in (_centre(mask, c) for c in range(ci - 3, ci + 4)) if g is not None]
        if len(got) < 5:
            out.append({"x": float(x), "y": None, "note": f"{what}: the curve is not in this column"})
            continue
        row = float(np.median([g[0] for g in got]))
        ln = float(np.median([g[1] for g in got]))
        y = cal["a"] + cal["b"] * row
        dc = 12
        s1, s2 = _centre(mask, ci - dc), _centre(mask, ci + dc)
        slope = 0.0 if s1 is None or s2 is None else abs(s2[0] - s1[0]) / (2 * dc) * cal["cpu"] * abs(cal["b"])
        half_px = 2.0 + 0.25 * ln
        dy = abs(cal["b"]) * half_px + cal["ymis"] + slope * cal["xmis"]
        out.append({"x": float(x), "y": float(y), "lo": float(y - dy), "hi": float(y + dy), "px": [float(col), row],
                    "px_lo": row - half_px, "px_hi": row + half_px, "note": note(cal, what)})
    return out
