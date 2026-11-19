"""Shared reading code for Fig. 4(d, e) (PDF p. 4): computed f_s and kappa_s R against s/R,
two blue curves per panel told apart by line weight (a thick line and a thin line), with red
parts of each curve over the bend region.

Calibration. The axes are two long black lines with arrows: the y axis is the column with the
longest vertical black run, the x axis the row with the longest horizontal black run. Ticks are
short black runs crossing an axis on both sides. x: the ticks are evenly spaced; the y axis is
s/R = 0 and the ticks labelled pi/2 and pi are the 4th and 8th from it, so tick k is k pi/8
(the misfit of all ticks to one line is returned). y: the x axis is level with the label 1 in (d)
and 0 in (e), so its row is that value; the ticks above and below it are assigned in order with
the step of the labelled ticks (0.05 in (d), labels every 0.1; 2.5 in (e), labels every 5).
The arrowheads (within 4% of an axis end) are not ticks.

Curves. Ink is blue or red (the red bend-region parts). Thick and thin lines are told apart by
the distance transform: pixels farther than a threshold from the background (half the largest
distance found) are cores of the thick line; the thick line is those cores grown back by the
threshold, and the thin line is what is left after removing the thick line grown by 3 more px.
The legend (lines and shape icons at the right) is removed first: rows with ink right of the
arrow tip of the x axis form legend bands, and in each band the ink from its leftmost point
reached from the right with gaps of at most 5% of the axis length is cleared.

Reading at x: the pixels of the chosen line in a band of +-2 columns; the value is the middle of
their vertical extent, the 95% interval that extent widened by 1 px and the calibration misfit.
A thick dashed line in a dash gap is read by interpolating between the nearest dashes on either
side (interval: both dashes' extents). A thin line hidden under the thick one is read as the
thick line's extent. Two separate runs in the band (a jump of the curve) give no value.
"""
import numpy as np
from scipy import ndimage as ndi


def _runs(v):
    out, start = [], None
    for i, x in enumerate(list(v) + [False]):
        if x and start is None:
            start = i
        elif not x and start is not None:
            out.append((start, i))
            start = None
    return out


def _longest_run(v):
    r = _runs(v)
    return max((b - a for a, b in r), default=0), r


def calibrate(image, y_axis_value, y_step):
    im = image.astype(int)
    hi, lo = im.max(axis=2), im.min(axis=2)
    black = (hi < 110) & (hi - lo < 50)
    H, W = black.shape
    # the axes are partly covered by the curves (the thick line of (d) lies on the x axis), so
    # an axis is the row (column) with the most black pixels, not the longest unbroken run
    col_n = black.sum(axis=0)
    row_n = black.sum(axis=1)
    yc = [c for c in range(W) if col_n[c] >= 0.9 * col_n.max()]
    xr = [r for r in range(H) if row_n[r] >= 0.9 * row_n.max()]
    yc = max(_group(yc), key=len)
    xr = max(_group(xr), key=len)
    yax = (min(yc) + max(yc) + 1) / 2  # continuous column of the y axis centre
    xax = (min(xr) + max(xr) + 1) / 2
    aw = max(yc) - min(yc) + 1  # axis line widths
    ah = max(xr) - min(xr) + 1
    # extents: from the other axis to the farthest black pixel of the axis line (arrow tips)
    x_lo = int(yax)
    ys = np.nonzero(black[:, min(yc):max(yc) + 1].any(axis=1))[0]
    y_lo, y_hi = int(ys.min()), int(ys.max())
    # x ticks: columns with black on both sides of the axis line within a short reach (a tick
    # may be partly hidden under a curve) and none at the reach itself (not a long line); a
    # group wider than a tick (the arrowhead) is not a tick
    reach = int(0.025 * W)
    r_top, r_bot = min(xr), max(xr)
    xt = []
    for c in range(x_lo, W):
        up = int(black[r_top - reach:r_top, c].sum())
        dn = int(black[r_bot + 1:r_bot + 1 + reach, c].sum())
        if up >= 0.15 * reach and dn >= 0.15 * reach and not black[r_top - reach, c] and not black[r_bot + reach, c]:
            xt.append(c)
    xt = [g for g in _group(xt) if len(g) <= 3 * aw]
    xt = [(g[0] + g[-1] + 1) / 2 for g in xt]
    xt = sorted(t for t in xt if abs(t - yax) > 2 * aw)
    # some ticks are hidden under the curves: the spacing is the smallest gap between found
    # ticks, and each tick's index is its distance from the y axis in spacings
    # (the candidate spacing that puts the most found ticks on its multiples; ties: the larger)
    def score(g):
        return sum(abs((t - yax) / g - round((t - yax) / g)) < 0.1 for t in xt)
    cands = [b - a for a, b in zip(xt, xt[1:]) if b - a >= 0.03 * W]
    spacing = max(cands, key=lambda g: (score(g), g))
    idx = [int(round((t - yax) / spacing)) for t in xt]
    keep = [(t, k) for t, k in zip(xt, idx) if abs((t - yax) / spacing - k) < 0.1 and 1 <= k <= 8]
    xt = [t for t, _ in keep]
    xk = [k for _, k in keep]
    x_hi = int(round(yax + 8 * spacing))  # the tick labelled pi, where the curves end
    # y ticks
    reach_y = int(0.04 * (y_hi - y_lo))
    c_l, c_r = min(yc), max(yc)
    ytk = []
    for r in range(y_lo, y_hi):
        le = int(black[r, c_l - reach_y:c_l].sum())
        ri = int(black[r, c_r + 1:c_r + 1 + reach_y].sum())
        if le >= 0.15 * reach_y and ri >= 0.15 * reach_y and not black[r, c_l - reach_y] and not black[r, c_r + reach_y]:
            ytk.append(r)
    ytk = [g for g in _group(ytk) if len(g) <= 3 * ah]
    ytk = [(g[0] + g[-1] + 1) / 2 for g in ytk]
    top_end = y_lo + 0.04 * (y_hi - y_lo)
    ytk = [t for t in ytk if t > top_end and abs(t - xax) > 2 * ah]
    # x fit: tick k from the y axis is k pi/8; the y axis is 0
    px = [yax] + xt
    vx = [0.0] + [k * np.pi / 8 for k in xk]
    bx, ax = np.polyfit(px, vx, 1)
    mx = float(np.max(np.abs(np.array(px) - (np.array(vx) - ax) / bx)))
    # y fit
    above = sorted([t for t in ytk if t < xax], reverse=True)
    below = sorted([t for t in ytk if t > xax])
    py = [xax] + above + below
    vy = [y_axis_value] + [y_axis_value + (k + 1) * y_step for k in range(len(above))] + \
         [y_axis_value - (k + 1) * y_step for k in range(len(below))]
    by, ay = np.polyfit(py, vy, 1)
    my = float(np.max(np.abs(np.array(py) - (np.array(vy) - ay) / by)))
    return dict(ax=ax, bx=bx, mx=mx, ay=ay, by=by, my=my, yax=yax, xax=xax, x_hi=x_hi,
                axis_len=x_hi - x_lo, n_xt=len(xt), n_yt=len(above) + len(below),
                y_ticks=(len(above), len(below)), black=black)


def _group(idx):
    out, cur = [], []
    for i in list(idx) + [None]:
        if cur and (i is None or i != cur[-1] + 1):
            out.append(cur)
            cur = []
        if i is not None:
            cur.append(i)
    return out


def lines(image, cal):
    im = image.astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    blue = (b > 120) & (b - r > 70) & (b - g > 70)
    red = (r > 170) & (r - g > 100) & (r - b > 100)
    ink = blue | red
    H, W = ink.shape
    ink[:, :int(cal["yax"]) + 1] &= False  # nothing of the curves lies left of the y axis
    # legend removal
    tip = cal["x_hi"]
    tol = int(0.05 * cal["axis_len"])
    band_rows = [rr for rr in range(H) if ink[rr, tip + int(0.03 * cal["axis_len"]):].any()]
    for grp in _group(band_rows):
        rows = slice(grp[0], grp[-1] + 1)
        colany = ink[rows].any(axis=0)
        c = W - 1
        last = None
        while c >= 0:
            if colany[c]:
                last = c
            elif last is not None and last - c > tol:
                break
            c -= 1
        if last is not None:
            ink[rows, last:] = False
    dist = ndi.distance_transform_edt(ink)
    thr = 0.5 * float(np.percentile(dist[ink], 99.5))
    core = dist > thr
    thick = ndi.binary_dilation(core, iterations=int(np.ceil(thr)) + 1) & ink
    thin = ink & ~ndi.binary_dilation(thick, iterations=3)
    # drop tiny specks of the thin mask (halo remnants)
    lab, n = ndi.label(thin)
    sizes = ndi.sum(thin, lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:] = sizes >= 30
    thin = keep[lab]
    return thick, thin, thr


def _extent(mask, c, half=2):
    band = mask[:, max(0, c - half):c + half + 1]
    rows = np.nonzero(band.any(axis=1))[0]
    if len(rows) == 0:
        return None
    runs = _runs(np.isin(np.arange(rows.min(), rows.max() + 1), rows))
    return rows.min(), rows.max() + 1, len(runs)


def read(image, at, which, y_axis_value, y_step):
    cal = calibrate(image, y_axis_value, y_step)
    thick, thin, thr = lines(image, cal)
    pad = 1.0 + cal["my"]
    gap = int(0.04 * cal["axis_len"])
    base = (f"x ticks {cal['n_xt']} (misfit {cal['mx']:.2f} px), y ticks {cal['y_ticks']} "
            f"(misfit {cal['my']:.2f} px); thick/thin threshold {thr:.1f} px")
    out = []
    for x in at:
        col = (x - cal["ax"]) / cal["bx"]
        c = int(round(col))
        mask = thick if which == "thick" else thin
        e = _extent(mask, c)
        if which == "thick" and e is not None and e[1] - e[0] < 1.5 * thr:
            e = None  # only the slanted corner of a dash end: read as a dash gap
        note = ""
        if e is None and which == "thin":
            e = _extent(thick, c)
            note = "thin line hidden under the thick line: read as the thick line's extent; "
        if e is None and which == "thick":
            left = right = None
            for d in range(3, gap):
                if left is None and _extent(thick, c - d, 0):
                    left = (c - d, _extent(thick, c - d, 0))
                if right is None and _extent(thick, c + d, 0):
                    right = (c + d, _extent(thick, c + d, 0))
            if left and right and left[1][2] == 1 and right[1][2] == 1:
                (cl, (tl, bl, _)), (cr, (tr, br, _)) = left, right
                w = (c - cl) / (cr - cl)
                mid = (1 - w) * (tl + bl) / 2 + w * (tr + br) / 2
                top, bot = min(tl, tr), max(bl, br)
                y = cal["ay"] + cal["by"] * mid
                ya, yb = cal["ay"] + cal["by"] * (top - pad), cal["ay"] + cal["by"] * (bot + pad)
                out.append({"x": x, "y": float(y), "lo": float(min(ya, yb)), "hi": float(max(ya, yb)),
                            "px": [float(col), float(mid)], "px_lo": float(top), "px_hi": float(bot),
                            "note": f"in a dash gap: interpolated between dashes at columns {cl}, {cr}; " + base})
                continue
        if e is None:
            out.append({"x": x, "y": None, "note": "no line pixels at this position"})
            continue
        top, bot, nr = e
        if nr > 1:
            out.append({"x": x, "y": None, "note": f"two separate runs of the line here (a jump), rows {top}-{bot}"})
            continue
        mid = (top + bot) / 2
        y = cal["ay"] + cal["by"] * mid
        ya, yb = cal["ay"] + cal["by"] * (top - pad), cal["ay"] + cal["by"] * (bot + pad)
        out.append({"x": x, "y": float(y), "lo": float(min(ya, yb)), "hi": float(max(ya, yb)),
                    "px": [float(col), float(mid)], "px_lo": float(top), "px_hi": float(bot),
                    "note": note + base})
    return out
