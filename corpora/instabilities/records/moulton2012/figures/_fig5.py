"""Fig. 5 (PDF p. 5): shell edge radius r_s against time t, panels (a), (b), (c).

Shared reading code for every Fig. 5 reading. Each panel is rendered as its own crop.

Calibration, all from the image:
- dark (black) pixels: grey level below 110 and not red; red (dashed line): R > 180, G and B < 120.
- the y axis is the dark column with the longest vertical run; the x axis the dark row with the
  longest horizontal run. Tick marks stand outward (below the x axis, left of the y axis).
- x: the long ticks below the axis are the labelled majors 10, 20, 30 (left to right); a line is
  fitted through (column, label) and its rms misfit kept. The intermediate short ticks (5, 15, 25)
  and the axis origin are checked against the fit (reported in the note, not used).
- y: ticks left of the axis, all of one length; the labelled ones are those level with the two
  label texts left of the ticks, 2.0 (upper) and 1.0 (lower). The other ticks are evenly spaced;
  their count between the labelled ones fixes their step (0.2 in every panel).
  A line is fitted through all ticks (row, value) and its rms misfit kept.
Curve: the black curve is the only dark mark inside the plot box away from the axes and ticks.
In each column its centre is the middle of the dark rows (the curve is single valued in t).
Columns where the curve is hidden (crossing the red dashes) are left out and bridged.
Maxima (ribs): local minima of the centre row, separated by at least 0.4 in t and standing at
least 15 px above the neighbouring trough; maxima within 8 px of the box edges are not taken.
The time of a maximum is a parabola vertex fitted to the centre rows within 6 px of the extreme;
its 95% interval spans the columns where the centre stays within half a line width of the extreme
(a flat top cannot be located better than that) plus twice the x misfit. The height is the
extreme centre row; its interval is half the line width plus twice the y misfit.
Red dashed line: at a requested t, the centre row of the red pixels in the columns of the nearest
dash on each side of t, linearly interpolated; interval half the dash width plus twice the y
misfit plus the interpolation gap times the local slope.
"""
import numpy as np


def _masks(img):
    im = img[..., :3].astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    red = (r > 180) & (g < 120) & (b < 120)
    grey = im.mean(-1)
    dark = (grey < 110) & ~red
    return dark, red


def _groups(idx, gap=1):
    out = []
    for c in idx:
        c = int(c)
        if out and c - out[-1][-1] <= gap:
            out[-1].append(c)
        else:
            out.append([c])
    return out


def _longest(v):
    best, cur = 0, 0
    for x in v:
        cur = cur + 1 if x else 0
        best = max(best, cur)
    return best


def calibrate(img):
    dark, red = _masks(img)
    H, W = dark.shape
    colrun = np.array([_longest(dark[:, c]) for c in range(W)])
    rowrun = np.array([_longest(dark[r, :]) for r in range(H)])
    ycols = [c for c in range(W) if colrun[c] > 0.8 * colrun.max()]
    xrows = [r for r in range(H) if rowrun[r] > 0.8 * rowrun.max()]
    yaxis = _groups(ycols)[0]
    xaxis = _groups(xrows)[-1]
    c_left, c_right = yaxis[0], yaxis[-1]
    r_top_ax, r_bot_ax = xaxis[0], xaxis[-1]
    # x axis extent
    xcols = np.where(dark[(r_top_ax + r_bot_ax) // 2, :])[0]
    x_end = int(xcols.max())
    # y axis extent
    yrows = np.where(dark[:, (c_left + c_right) // 2])[0]
    y_top = int(yrows.min())
    # x ticks: dark runs just below the axis
    below = r_bot_ax + 3
    xt = []
    for g in _groups(np.where(dark[below, :])[0]):
        c = (g[0] + g[-1]) / 2
        n = 0
        rr = below
        while rr < H and dark[rr, int(round(c))]:
            rr += 1
            n += 1
        xt.append((c, n))
    lens = np.array([n for _, n in xt])
    long = [c for c, n in xt if n > 0.75 * lens.max()]
    short = [c for c, n in xt if n <= 0.75 * lens.max()]
    # the leftmost long tick may be the y axis itself continuing below; keep ticks right of it
    long = [c for c in long if c > c_right + 20]
    labels = [10.0, 20.0, 30.0][-len(long):]
    ax_, bx_ = np.polyfit(long, labels, 1)
    xres = np.array(labels) - (ax_ * np.array(long) + bx_)
    xrms = float(np.sqrt(np.mean(xres ** 2))) if len(long) > 2 else 0.0
    xrms = max(xrms, abs(ax_) * 1.0)  # at least one pixel
    # y ticks: dark runs just left of the axis
    left = c_left - 3
    yt = []
    for g in _groups(np.where(dark[:r_top_ax - 2, left])[0]):
        r = (g[0] + g[-1]) / 2
        n = 0
        cc = left
        while cc > 0 and dark[int(round(r)), cc]:
            cc -= 1
            n += 1
        yt.append((r, n))
    # all y ticks have the same length: the labelled ones are those level with the label text
    # (dark blobs left of the ticks); the upper label is 2.0, the lower 1.0
    tick_left = min(left - n for _, n in yt)
    txt = np.where(dark[:r_top_ax, :max(1, tick_left - 15)].any(1))[0]
    lab = [(g[0] + g[-1]) / 2 for g in _groups(txt, gap=3) if len(g) > 20]
    tick_rows = [r for r, _ in yt]
    majors = sorted({min(tick_rows, key=lambda r: abs(r - lr)) for lr in lab})
    upper, lower = majors[0], majors[-1]  # rows: 2.0 above, 1.0 below
    between = [r for r, n in yt if upper < r < lower]
    step = 1.0 / (len(between) + 1)
    rows, vals = [], []
    for r, n in yt:
        k = round((lower - r) / ((lower - upper) / (len(between) + 1)))
        rows.append(r)
        vals.append(1.0 + k * step)
    ay, by = np.polyfit(rows, vals, 1)
    yres = np.array(vals) - (ay * np.array(rows) + by)
    yrms = max(float(np.sqrt(np.mean(yres ** 2))), abs(ay) * 1.0)
    # line width of the curve: median vertical run of dark pixels in the box at flat spots
    box = (c_right + 12, x_end - 4, y_top + 2, r_top_ax - 12)
    origin_t = float(ax_ * ((c_left + c_right) / 2) + bx_)
    short_t = [float(ax_ * c + bx_) for c in short if c > c_right + 20]
    return {"dark": dark, "red": red, "ax": ax_, "bx": bx_, "xrms": xrms, "ay": ay, "by": by,
            "yrms": yrms, "box": box, "origin_t": origin_t, "short_t": short_t, "step": step}


def trace(cal):
    dark = cal["dark"]
    c0, c1, r0, r1 = cal["box"]
    cols, cen, wid = [], [], []
    for c in range(c0, c1):
        rr = np.where(dark[r0:r1, c])[0]
        if len(rr) == 0:
            continue
        g = _groups(rr, gap=2)
        if len(g) != 1:
            continue
        cols.append(c)
        cen.append(r0 + (g[0][0] + g[0][-1]) / 2)
        wid.append(len(g[0]))
    cols, cen = np.array(cols), np.array(cen)
    lw = float(np.median(np.sort(wid)[: max(1, len(wid) // 4)]))
    return cols, cen, lw


def _extrema(cal, sign):
    """sign=+1: maxima of r_s (minimum rows); sign=-1: minima of r_s."""
    from scipy.signal import find_peaks
    cols, cen, lw = trace(cal)
    full = np.arange(cols.min(), cols.max() + 1)
    f = np.interp(full, cols, cen)
    dist = int(0.4 / abs(cal["ax"]))
    idx, _ = find_peaks(-sign * f, distance=dist, prominence=15)
    c0, c1 = cal["box"][0], cal["box"][1]
    out = []
    for i in idx:
        if full[i] < c0 + 8 or full[i] > c1 - 8:
            continue
        ext = f[i]
        near = np.abs(f - ext) <= 6
        lo, hi = i, i
        while lo > 0 and near[lo - 1]:
            lo -= 1
        while hi < len(f) - 1 and near[hi + 1]:
            hi += 1
        xs = full[lo:hi + 1]
        p = np.polyfit(xs - full[i], f[lo:hi + 1], 2)
        cv = full[i] - p[1] / (2 * p[0]) if p[0] != 0 else full[i]
        if abs(cv - full[i]) > (hi - lo):
            cv = full[i]
        flat = np.abs(f - ext) <= lw / 2
        a, b = i, i
        while a > 0 and flat[a - 1]:
            a -= 1
        while b < len(f) - 1 and flat[b + 1]:
            b += 1
        out.append({"col": float(cv), "row": float(ext), "col_lo": float(full[a]), "col_hi": float(full[b]), "lw": lw})
    return out


def peaks(img, at, what, sign=+1):
    cal = calibrate(img)
    ext = _extrema(cal, sign)
    ax_, bx_, ay, by = cal["ax"], cal["bx"], cal["ay"], cal["by"]
    res = []
    for n in at:
        k = int(round(float(n)))
        if k < 1 or k > len(ext):
            res.append({"x": n, "y": None, "note": f"only {len(ext)} extrema found inside the box"})
            continue
        e = ext[k - 1]
        t = ax_ * e["col"] + bx_
        if what == "time":
            ta, tb = sorted([ax_ * e["col_lo"] + bx_, ax_ * e["col_hi"] + bx_])
            lo = min(ta, t) - 2 * cal["xrms"]
            hi = max(tb, t) + 2 * cal["xrms"]
            res.append({"x": n, "y": float(t), "lo": float(lo), "hi": float(hi),
                        "px": [e["col"], e["row"]],
                        "note": f"extremum {k}; x misfit {cal['xrms']:.3f}; axis origin reads t = {cal['origin_t']:.3f}"})
        else:
            y = ay * e["row"] + by
            d = abs(ay) * e["lw"] / 2 + 2 * cal["yrms"]
            res.append({"x": n, "y": float(y), "lo": float(y - d), "hi": float(y + d),
                        "px": [e["col"], e["row"]],
                        "note": f"extremum {k} at t = {t:.2f}; line width {e['lw']:.0f} px; y misfit {cal['yrms']:.4f}"})
    return res


def red_line(img, at):
    cal = calibrate(img)
    red = cal["red"]
    c0, c1, r0, r1 = cal["box"]
    cols, cen = [], []
    for c in range(c0 - 10, c1 + 4):
        rr = np.where(red[r0:r1, c])[0]
        if len(rr) == 0:
            continue
        cols.append(c)
        cen.append(r0 + rr.mean())
    cols, cen = np.array(cols), np.array(cen)
    dashes = _groups(cols, gap=1)
    lookup = dict(zip(cols.tolist(), cen.tolist()))
    dw = []
    for c in cols[::50]:
        dw.append(int(red[r0:r1, c].sum()))
    width = float(np.median(dw))
    centres = [(np.mean(d), np.mean([lookup[c] for c in d])) for d in dashes if len(d) > 5]
    ax_, bx_, ay, by = cal["ax"], cal["bx"], cal["ay"], cal["by"]
    res = []
    for v in at:
        t = float(v)
        col = (t - bx_) / ax_
        inside = [d for d in dashes if d[0] <= col <= d[-1] and len(d) > 5]
        if inside:
            d = inside[0]
            sel = [c for c in d if abs(c - col) <= 20]
            row = float(np.mean([lookup[c] for c in sel]))
            gap = 0.0
        else:
            left = [cd for cd in centres if cd[0] < col]
            right = [cd for cd in centres if cd[0] > col]
            if not left or not right:
                res.append({"x": v, "y": None, "note": "outside the dashed line"})
                continue
            (ca, ra), (cb, rb) = left[-1], right[0]
            row = float(ra + (rb - ra) * (col - ca) / (cb - ca))
            gap = abs(rb - ra)
        y = ay * row + by
        d = abs(ay) * (width / 2 + gap / 2) + 2 * cal["yrms"] + abs((rb - ra) / (cb - ca) * ay) * 2 * cal["xrms"] / abs(ax_) if not inside else abs(ay) * width / 2 + 2 * cal["yrms"]
        res.append({"x": v, "y": float(y), "lo": float(y - d), "hi": float(y + d), "px": [float(col), row],
                    "note": f"dash width {width:.0f} px; {'inside a dash' if inside else 'bridged between dashes'}"})
    return res
