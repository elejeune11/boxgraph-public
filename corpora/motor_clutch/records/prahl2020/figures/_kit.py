"""Shared reading code for the data figures of Prahl et al. 2020 (vector plots, rendered by pdftoppm).

Each reading file (figures/<reading id>.py) holds a CONFIG dict and calls one reader below. The
reading file pins this file's SHA-256, because the build caches a reading by the reading file's bytes.

Everything is found in the image. The only things typed in are the printed tick labels (and, for a
categorical axis, how many groups there are), plus which ink colour a series is drawn in.

Calibration: the axis lines are the longest straight runs of black ink; the tick marks are short
black runs leaving an axis line, inside or outside. The evenly spaced ticks are matched to the
printed labels from the low end (every k-th tick when unlabelled ticks lie between labels); a
log10 axis is matched by its decades (the tick after which the gap jumps). The fit residual is
reported and widens every interval.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from boxgraph import digitize as D


# ---------------------------------------------------------------- masks
def black(img, thr=90):
    """Black ink: every channel dark (grey dots and coloured dots are left out)."""
    return img[:, :, :3].max(axis=2) < thr


def ink(img, thr=200):
    return img[:, :, :3].astype(float).mean(axis=2) < thr


def colour(img, rgb, tol=60):
    d = np.sqrt(((img[:, :, :3].astype(float) - np.array(rgb, float)) ** 2).sum(axis=2))
    return d < tol


def _runs(idx):
    """(start, end) inclusive runs of consecutive integers."""
    out = []
    for i in idx:
        if out and i == out[-1][1] + 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return [tuple(r) for r in out]


# ---------------------------------------------------------------- axes
def axis_lines(bk, gap=1):
    """Column of the left axis line and row of the bottom axis line (longest black runs), with their
    widths, and the far ends (top of the y axis, right end of the x axis)."""
    H, W = bk.shape
    colrun = np.array([D._longest_run(bk[:, c], gap=gap)[0] for c in range(W)])
    m = colrun.max()
    cols = [c for c in range(W // 2) if colrun[c] >= 0.9 * m]
    c0 = cols[0]
    # the axis line: the contiguous columns at c0 as long as the longest (a bar standing against
    # the axis is shorter, since it stops below the top of the axis)
    top_len = colrun[c0:c0 + 40].max()
    yc = [c0]
    while colrun[yc[-1] + 1] >= 0.98 * top_len:
        yc.append(yc[-1] + 1)
    yc = [c for c in yc if colrun[c] >= 0.98 * top_len]
    ycol = (yc[0] + yc[-1]) / 2
    _, ytop, ybot = D._longest_run(bk[:, int(round(ycol))], gap=gap)
    rowrun = np.array([D._longest_run(bk[r, :], gap=1)[0] for r in range(H)])
    m2 = rowrun.max()
    rows = [r for r in range(H // 2, H) if rowrun[r] >= 0.9 * m2]
    r1 = rows[-1]
    xr = [r for r in range(r1 - 40, r1 + 1) if rowrun[r] >= 0.9 * m2]
    xrow = (xr[0] + xr[-1]) / 2
    _, xl, xrr = D._longest_run(bk[int(round(xrow)), :], gap=1)
    return {"ycol": ycol, "yw": yc[-1] - yc[0] + 1, "ytop": ytop, "ybot": ybot,
            "xrow": xrow, "xw": xr[-1] - xr[0] + 1, "xleft": xl, "xright": xrr - 1}


def _tick_candidates(bk, line_pos, half, lo, hi, axis, min_len=6, max_len=80):
    """Ticks leaving an axis line at `line_pos` (col for 'y', row for 'x'), on either side, between
    lo and hi along the axis. Returns [(centre, length, side)]."""
    found = []
    for side in (-1, 1):
        start = int(round(line_pos + side * (half + 1)))
        lens = []
        for t in range(int(lo), int(hi) + 1):
            n = 0
            p = start
            while 0 <= p < (bk.shape[1] if axis == "y" else bk.shape[0]):
                v = bk[t, p] if axis == "y" else bk[p, t]
                if not v:
                    break
                n += 1
                p += side
            lens.append(n)
        lens = np.array(lens)
        ok = [i for i, n in enumerate(lens) if min_len <= n <= max_len]
        for s, e in _runs(ok):
            if e - s > 25:  # a line along the axis, not a tick
                continue
            found.append(((s + e) / 2 + lo, float(np.median(lens[s:e + 1])), side))
    return found


def _match(ticks, labels, corner_lo, corner_hi, scale, every=None):
    """Evenly spaced tick positions (ascending in value) matched to labels."""
    t = sorted(ticks)
    if scale == "log10":
        pos = sorted(set([round(x, 1) for x in t] + [round(corner_lo, 1), round(corner_hi, 1)]))
        reg = D.regular_ticks(pos, tol=6)
        if len(reg) == len(labels):  # only the decade ticks are long enough to be found
            return list(zip(reg, labels)), "decade ticks (with the box corners)"
        gaps = np.diff(pos)
        dec = [pos[0]]
        for i in range(1, len(pos) - 1):
            if gaps[i] > 2.0 * gaps[i - 1]:
                dec.append(pos[i])
        if abs(pos[-1] - dec[-1]) > 2 and gaps[-1] < 0.5 * gaps[-2] if len(gaps) > 1 else False:
            dec.append(pos[-1])
        if len(dec) < len(labels):
            dec.append(pos[-1])
        if len(dec) != len(labels):
            raise RuntimeError(f"log axis: {len(dec)} decades found for {len(labels)} labels: {dec}")
        return list(zip(dec, labels)), "decades"
    reg = D.regular_ticks(t, tol=2.5)
    step = np.median(np.diff(reg)) if len(reg) > 1 else None
    # the corner ticks hidden in the other axis line
    m = len(labels)
    for c in (corner_lo, corner_hi):
        n = len(reg)
        if c == corner_hi and (n == m or (every and n >= every * (m - 1) + 1)):
            break  # the far corner is not needed
        if step and all(abs(c - x) > 0.5 * step for x in reg):
            if abs(abs(c - (min(reg) if c < min(reg) else max(reg))) - step) < 0.06 * step:
                reg = sorted(reg + [c])
    n, m = len(reg), len(labels)
    if every:  # labels on every k-th tick from the low end (more ticks may follow the last label)
        if n < every * (m - 1) + 1:
            raise RuntimeError(f"{n} evenly spaced ticks, too few for {m} labels on every {every}th")
        return list(zip(reg[::every][:m], labels)), f"every {every}th tick labelled, from the low end"
    if n == m:
        return list(zip(reg, labels)), "every tick labelled"
    if m > 1 and (n - 1) % (m - 1) == 0:
        k = (n - 1) // (m - 1)
        return list(zip(reg[::k], labels)), f"every {k}th tick labelled"
    raise RuntimeError(f"{n} evenly spaced ticks for {m} labels: {[round(x, 1) for x in reg]}")


def _dedupe(ps, tol=4):
    out = []
    for p in sorted(ps):
        if out and p - out[-1][-1] <= tol:
            out[-1].append(p)
        else:
            out.append([p])
    return [float(np.mean(g)) for g in out]


def calibrate(img, ylabels, xlabels=None, yscale="linear", xscale="linear", ytop=None, yevery=None, xevery=None, xcorners=False, axis_gap=1):
    """Axis objects from the image. Labels are listed from the low end. `ytop`: a row above which
    ticks are not looked for (e.g. a broken axis). Returns (xa, ya, info)."""
    bk = black(img)
    L = axis_lines(bk, axis_gap)
    # a closed box: a top line and a right line as long as the axes; their ticks count too
    tr = [r for r in range(max(0, L["ytop"] - 15), L["ytop"] + 16)
          if D._longest_run(bk[r, :], gap=1)[0] >= 0.9 * (L["xright"] - L["xleft"])]
    rc = [c for c in range(L["xright"] - 15, min(bk.shape[1], L["xright"] + 16))
          if D._longest_run(bk[:, c], gap=1)[0] >= 0.9 * (L["ybot"] - L["ytop"])]
    top_line, right_line = bool(tr), bool(rc)
    toprow = (tr[0] + tr[-1]) / 2 if tr else float(L["ytop"])
    rightcol = (rc[0] + rc[-1]) / 2 if rc else float(L["xright"])
    lo_y = L["ytop"] + 2 if ytop is None else ytop
    yt = _tick_candidates(bk, L["ycol"], L["yw"] / 2, lo_y, L["xrow"] - L["xw"], "y")
    if right_line:
        yt += _tick_candidates(bk, rightcol, L["yw"] / 2, lo_y, L["xrow"] - L["xw"], "y")
    yt = _dedupe([r for r, _, _ in yt])
    # a y tick is ascending in value with decreasing row: use -row
    ymarks, ynote = _match([-r for r in yt], ylabels, -L["xrow"], -toprow, yscale,
                           every=yevery)
    ya = D.Axis(yscale, [(-p, v) for p, v in ymarks])
    xa, xnote = None, ""
    xt = _tick_candidates(bk, L["xrow"], L["xw"] / 2, L["ycol"] + L["yw"], L["xright"] - L["yw"], "x")
    if top_line:
        xt += _tick_candidates(bk, toprow, L["xw"] / 2, L["ycol"] + L["yw"], L["xright"] - L["yw"], "x")
    xt = _dedupe([c for c, _, _ in xt])
    if xlabels is not None and xcorners:
        # the end labels sit at the box corners (the tick marks are bin centres, not labels)
        xmarks, xnote = [(L["ycol"], xlabels[0]), (rightcol, xlabels[-1])], "end labels at the box corners"
        xa = D.Axis(xscale, xmarks)
    elif xlabels is not None:
        xmarks, xnote = _match(xt, xlabels, L["ycol"], rightcol, xscale, every=xevery)
        xa = D.Axis(xscale, xmarks)
    info = {"lines": L, "x_ticks": xt, "ynote": ynote, "xnote": xnote,
            "y_res": ya.residual_px, "x_res": xa.residual_px if xa else None}
    return xa, ya, info


def _cal(img, cfg):
    return calibrate(img, cfg["ylabels"], cfg.get("xlabels"), cfg.get("yscale", "linear"), cfg.get("xscale", "linear"),
                     ytop=cfg.get("ytop"), yevery=cfg.get("yevery"), xevery=cfg.get("xevery"), xcorners=cfg.get("xcorners", False), axis_gap=cfg.get("axis_gap", 1))


def _yint(ya, r, h):
    a, b = ya.to_value(r - h), ya.to_value(r + h)
    return min(a, b), max(a, b)


def _note(info):
    s = f"y axis: {info['ynote']}, misfit {info['y_res']:.2f} px"
    if info.get("x_res") is not None:
        s += f"; x axis: {info['xnote']}, misfit {info['x_res']:.2f} px"
    return s


# ---------------------------------------------------------------- readers
def category_centres(info, n, below=True):
    """The n category ticks on the x axis (outside, below the axis line) from left to right."""
    L = info["lines"]
    xs = [c for c in info["x_ticks"] if c > L["ycol"] + 10]
    if len(xs) > n:  # a stray mark: keep the evenly spaced set
        xs = D.regular_ticks(xs, tol=4)
    if len(xs) != n:
        raise RuntimeError(f"{len(xs)} category ticks found, expected {n}: {xs}")
    return xs


def read_means(img, at, cfg):
    """Dot plots: the black mean line of each group and its error bar (two shorter caps, joined to
    the mean line by a stem). Groups are the x axis's category ticks."""
    xa, ya, info = _cal(img, cfg)
    bk = black(img, cfg.get("black", 90))
    if cfg.get("centres") == "lines":
        centres = mean_line_centres(bk, info, cfg["n"])
    else:
        centres = category_centres(info, cfg["n"])
    L = info["lines"]
    spacing = float(np.median(np.diff(centres))) if len(centres) > 1 else float(L["xright"] - L["ycol"])
    out = []
    h0 = 1.0 + info["y_res"]
    for x in at:
        i = int(round(float(x))) - 1
        c = int(round(centres[i]))
        # the mean line: the row group whose continuous black run through column c is the longest
        top = int(L["ytop"]) + 2
        bot = int(L["xrow"] - L["xw"] / 2) - 1
        runs = np.zeros(bk.shape[0], int)
        ext = {}
        for r in range(top, bot + 1):
            if not bk[r, c]:
                continue
            a = c
            while a > 0 and bk[r, a - 1]:
                a -= 1
            b = c
            while b < bk.shape[1] - 1 and bk[r, b + 1]:
                b += 1
            ext[r] = (a, b)
            # centred on the group and no wider than the group spacing (not a p-value bar)
            if abs((a + b) / 2 - c) <= 0.2 * (b - a) / 2 + 3 and (b - a) <= 1.2 * spacing:
                runs[r] = b - a + 1
        mlen = runs.max()
        mrows = [r for r in range(top, bot + 1) if runs[r] >= 0.92 * mlen]
        grp = max(_runs(mrows), key=lambda g: runs[g[0]:g[1] + 1].sum())
        mrow = (grp[0] + grp[1]) / 2
        thick = grp[1] - grp[0] + 1
        a, b = ext[grp[0]]
        mid = (a + b) / 2
        half = (b - a) / 2
        # caps: rows (other than the mean line) whose black run through c covers mid +- 0.3*half
        # and is shorter than the mean line by at least a stroke width... or equal (caps can match)
        caprows = [r for r in range(top, bot + 1) if r not in range(grp[0], grp[1] + 1) and r in ext
                   and ext[r][0] <= mid - 0.3 * half and ext[r][1] >= mid + 0.3 * half
                   and abs((ext[r][0] + ext[r][1]) / 2 - mid) <= 0.1 * half + 3
                   and ext[r][1] - ext[r][0] <= 1.05 * (b - a)]
        cgroups = _runs(caprows)
        above = [g for g in cgroups if g[1] < grp[0]]
        below = [g for g in cgroups if g[0] > grp[1]]

        def stem_ok(g):
            r0, r1 = (g[1], grp[0]) if g[1] < grp[0] else (grp[1], g[0])
            if r1 - r0 <= 6:  # cap touching the mean line
                return True
            col = ink(img, 160)[r0:r1 + 1, int(mid) - 4:int(mid) + 5].any(axis=1)
            return col.all()
        above = [g for g in above if stem_ok(g) and grp[0] - g[1] < 0.5 * (bot - top)]
        below = [g for g in below if stem_ok(g) and g[0] - grp[1] < 0.5 * (bot - top)]
        y = ya.to_value(mrow)
        lo, hi = _yint(ya, mrow, thick / 2 + h0)
        rd = {"x": float(x), "y": y, "lo": lo, "hi": hi, "px": [mid, mrow]}
        notes = [f"mean line {b - a + 1} px long, {thick} px thick"]
        if above:
            g = above[-1]
            rt = (g[0] + g[1]) / 2
            rd["bar_hi"] = ya.to_value(rt)
            rd["bar_hi_outer"] = ya.to_value(rt - (g[1] - g[0] + 1) / 2 - h0)
            rd["px_lo"] = rt
        else:
            rd["bar_hi"] = ya.to_value(grp[0])
            rd["bar_hi_outer"] = ya.to_value(grp[0] - h0)
            rd["px_lo"] = grp[0]
            notes.append("upper cap hidden in the mean line: bar at most the line")
        if below:
            g = below[0]
            rb = (g[0] + g[1]) / 2
            rd["bar_lo"] = ya.to_value(rb)
            rd["bar_lo_outer"] = ya.to_value(rb + (g[1] - g[0] + 1) / 2 + h0)
            rd["px_hi"] = rb
        else:
            rd["bar_lo"] = ya.to_value(grp[1])
            rd["bar_lo_outer"] = ya.to_value(grp[1] + h0)
            rd["px_hi"] = grp[1]
            notes.append("lower cap hidden in the mean line: bar at most the line")
        rd["note"] = "; ".join(notes) + "; " + _note(info)
        out.append(rd)
    return out


def mean_line_centres(bk, info, n):
    """Group centres from the mean lines themselves (when the x axis has no category ticks): the n
    longest horizontal black runs inside the plot, left to right."""
    L = info["lines"]
    top, bot = int(L["ytop"]) + 2, int(L["xrow"] - L["xw"] / 2) - 1
    left, right = int(L["ycol"] + L["yw"]), int(L["xright"])
    segs = []
    for r in range(top, bot):
        cols = np.nonzero(bk[r, left:right])[0]
        for s, e in _runs(list(cols)):
            segs.append((e - s + 1, r, s + left, e + left))
    segs.sort(reverse=True)
    chosen = []
    for ln, r, s, e in segs:
        if all(abs((s + e) / 2 - c) > 0.5 * ln for c in chosen):
            chosen.append((s + e) / 2)
        if len(chosen) == n:
            break
    return sorted(chosen)


def read_errorbar_points(img, at, cfg):
    """Points with vertical error bars at known x (numeric axis). The stem is the vertical black
    (or coloured) line at the point's column; its caps end the bar; the marker is a hollow or filled
    shape on the stem."""
    xa, ya, info = _cal(img, cfg)
    m = colour(img, cfg["rgb"], cfg.get("tol", 60)) if cfg.get("rgb") else black(img)
    L = info["lines"]
    top, bot = int(L["ytop"]) + int(L["yw"]) + 1, int(L["xrow"] - L["xw"] / 2) - 1
    h0 = 1.0 + info["y_res"]
    out = []
    for x in at:
        c0 = xa.to_pixel(float(x))
        # the stem: the column near c0 with the longest vertical run of ink
        best = None
        for c in range(int(c0) - 25, int(c0) + 26):
            n, s, e = D._longest_run(m[top:bot, c], gap=2)
            if best is None or n > best[0]:
                best = (n, s + top, e + top, c)
        n, s, e, c = best
        # bridge the hollow marker: extend the run across gaps of up to `gap` px of no ink
        gap = cfg.get("marker_gap", 70)
        colink = m[:, c - 1:c + 2].any(axis=1)
        while True:
            up = [r for r in range(max(top, s - gap), s) if colink[r]]
            if not up:
                break
            r = min(up)
            while r > top and colink[r - 1]:
                r -= 1
            s = r
        while True:
            dn = [r for r in range(e, min(bot, e + gap)) if colink[r]]
            if not dn or max(dn) < e:
                break
            r = max(dn)
            while r < bot - 1 and colink[r + 1]:
                r += 1
            if r + 1 <= e:
                break
            e = r + 1
        cols =[cc for cc in range(c - 8, c + 9) if D._longest_run(m[top:bot, cc], gap=2)[0] >= 0.8 * n]
        cs = (cols[0] + cols[-1]) / 2
        sw = cols[-1] - cols[0] + 1
        # caps: rows at the ends of the stem where ink spreads sideways
        hw = sw // 2 + 1
        rows = [r for r in range(max(s, top + 3), min(e, bot - 3)) if m[r, int(cs) - 4 * sw:int(cs) - hw].sum() >= 3
                and m[r, int(cs) + hw + 1:int(cs) + 4 * sw + 1].sum() >= 3]
        g = _runs(rows)
        if cfg.get("debug"):
            print("DEBUG", x, s, e, cs, sw, g)
        # the caps are the sideways ink at the two ends of the stem (a line crossing the stem
        # midway is not a cap)
        # (the outermost groups of sideways ink; a tick mark the stem runs into has none)
        ends_t, ends_b = g[:1], g[-1:]
        # the marker: what survives an opening wider than every stroke, nearest the stem
        k = 2 * sw + 3
        r0, r1 = max(top, s - 60), min(bot, e + 60)
        win = m[r0:r1, int(cs) - 80:int(cs) + 81]
        blob = ndimage.binary_opening(win, structure=np.ones((k, k), bool))
        lab, nl = ndimage.label(blob)
        mark = None
        if nl:
            cents = ndimage.center_of_mass(blob, lab, range(1, nl + 1))
            sizes = ndimage.sum(blob, lab, range(1, nl + 1))
            cand = [(abs(cc - 80), rr, sz) for (rr, cc), sz in zip(cents, sizes) if abs(cc - 80) < 15]
            if cand:
                _, rr, sz = min(cand)
                mark = (r0 + rr + 0.5, sz)
        stemcol = m[s:e, int(cs) - 1:int(cs) + 2].any(axis=1)
        gaps = [gg for gg in _runs(list(np.nonzero(~stemcol)[0])) if gg[1] - gg[0] > 3]
        if mark:
            rm = mark[0]
            mnote = f"filled marker centre (blob of {int(mark[1])} px)"
            hm = 2.0
        elif gaps:
            gg = max(gaps, key=lambda z: z[1] - z[0])
            rm = s + (gg[0] + gg[1]) / 2
            mnote = f"hollow marker centre (gap of {gg[1] - gg[0] + 1} px in the stem)"
            hm = 2.0
        else:
            rm = (s + e) / 2
            mnote = "no marker found: middle of the bar"
            hm = (e - s) / 2
        notes = []
        if ends_t and ends_t[0][0] < rm - sw:
            capt = ends_t[0]
        else:
            capt = (s, s)
            notes.append("no upper cap clear of the marker: the bar end is at most the stem's end")
        if ends_b and ends_b[-1][1] > rm + sw:
            capb = ends_b[-1]
        else:
            capb = (e - 1, e - 1)
            notes.append("no lower cap clear of the marker: the bar end is at most the stem's end")
        rt, rb = (capt[0] + capt[1]) / 2, (capb[0] + capb[1]) / 2
        if notes:
            mnote += "; " + "; ".join(notes)
        lo, hi = _yint(ya, rm, hm + h0)
        out.append({"x": float(x), "y": ya.to_value(rm), "lo": lo, "hi": hi, "px": [cs, rm],
                    "bar_hi": ya.to_value(rt), "bar_lo": ya.to_value(rb),
                    "bar_hi_outer": ya.to_value(rt - (capt[1] - capt[0] + 1) / 2 - h0),
                    "bar_lo_outer": ya.to_value(rb + (capb[1] - capb[0] + 1) / 2 + h0),
                    "px_lo": rt, "px_hi": rb,
                    "note": f"stem at column {cs:.0f} (x read back {xa.to_value(cs):.4g}); {mnote}; " + _note(info)})
    return out


def read_coloured_points(img, at, cfg):
    """Filled coloured markers with same-coloured error bars, at known x: the marker is the blob
    left after an opening wider than the stem; the bar ends are the extreme rows of the stem."""
    xa, ya, info = _cal(img, cfg)
    m = colour(img, cfg["rgb"], cfg.get("tol", 60))
    L = info["lines"]
    top, bot = int(L["ytop"]) + int(L["yw"]) + 1, int(L["xrow"] - L["xw"] / 2) - 1
    m[:top] = False
    m[bot + 1:] = False
    m[:, :int(L["ycol"] + L["yw"])] = False
    k = cfg.get("open", 9)
    blobs = ndimage.binary_opening(m, structure=np.ones((k, k), bool))
    lab, nl = ndimage.label(blobs)
    cents = ndimage.center_of_mass(blobs, lab, range(1, nl + 1))
    sizes = ndimage.sum(blobs, lab, range(1, nl + 1))
    # marker-like blobs: compact (bounding box about square), and of the commonest size
    objs = ndimage.find_objects(lab)
    shape_ok = []
    for sl, sz in zip(objs, sizes):
        hgt, wid = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        shape_ok.append(0.6 <= hgt / wid <= 1.6 and sz / (hgt * wid) >= 0.4)
    atc = [xa.to_pixel(float(x)) for x in at]
    good = [sz for (rr, cc), sz, ok in zip(cents, sizes, shape_ok) if ok and sz >= cfg.get("min_area", 60)
            and any(abs(cc - a) < cfg.get("xtol", 12) for a in atc)]
    # the commonest size (markers repeat at one size; letters and merged shapes vary)
    med = 0.0
    if good:
        best = max(good, key=lambda g0: sum(1 for g1 in good if abs(g1 - g0) <= 0.1 * g0))
        med = float(np.median([g1 for g1 in good if abs(g1 - best) <= 0.1 * best]))
    h0 = 1.0 + info["y_res"]
    out = []
    for x in at:
        c0 = xa.to_pixel(float(x))
        cand = [(abs(cc - c0), rr, cc, sz) for (rr, cc), sz, ok in zip(cents, sizes, shape_ok)
                if abs(cc - c0) < cfg.get("xtol", 12) and ok and 0.5 * med <= sz <= 1.6 * med]
        if not cand:
            out.append({"x": float(x), "y": None, "note": "no marker of this colour found at this x (hidden)"})
            continue
        _, rm, cm, sz = min(cand)
        # stem: same-coloured ink in a narrow band at the marker's column, contiguous with the marker
        band = m[:, int(cm) - 2:int(cm) + 3].any(axis=1)
        r = int(rm)
        while r > top and band[r - 1]:
            r -= 1
        rtop = r
        r = int(rm)
        while r < bot and band[r + 1]:
            r += 1
        rbot = r
        lo, hi = _yint(ya, rm, 2.0 + h0)
        other = ink(img, 200) & ~m

        def hidden(rr, step):  # the stem stops at ink of another colour (another series or an axis)
            return bool(other[rr + step:rr + step * 4:step, int(cm) - 2:int(cm) + 3].any()) or not (top < rr < bot)
        ht, hb = hidden(rtop, -1), hidden(rbot, 1)
        rd = {"x": float(x), "y": ya.to_value(rm), "lo": lo, "hi": hi, "px": [cm, rm],
              "note": f"marker blob {int(sz)} px at column {cm:.0f} (x read back {xa.to_value(cm):.4g}); "}
        if ht and hb:
            rd["note"] += "both bar ends hidden by other ink: bar not read; "
        else:
            if ht:
                rtop = rm - (rbot - rm)
                rd["note"] += "upper bar end hidden by other ink: taken as the mirror of the lower; "
            if hb:
                rbot = rm + (rm - rtop)
                rd["note"] += "lower bar end hidden by other ink: taken as the mirror of the upper; "
            rd.update({"bar_hi": ya.to_value(rtop + 2), "bar_lo": ya.to_value(rbot - 2),
                       "bar_hi_outer": ya.to_value(rtop - h0), "bar_lo_outer": ya.to_value(rbot + h0),
                       "px_lo": rtop, "px_hi": rbot})
            rd["note"] += "bar ends are the stem's extreme rows less half a cap stroke; "
        rd["note"] += _note(info)
        out.append(rd)
    return out


def read_hist(img, at, cfg):
    """Histogram bars (filled or outlined) at known bin centres: the top edge of the ink standing on
    the x axis at that column; an empty bin has no ink and reads 0."""
    xa, ya, info = _cal(img, cfg)
    m = ink(img, cfg.get("ink", 200))
    L = info["lines"]
    top = int(L["ytop"]) + int(L["yw"]) + 1
    base = int(L["xrow"] - L["xw"] / 2) - 1
    sub = m[top:base + 1].copy()
    lab, nl = ndimage.label(sub)
    # components standing on the axis (within 3 px of it)
    standing = set(np.unique(lab[-3:][lab[-3:] > 0]))
    h0 = 1.0 + info["y_res"]
    out = []
    for x in at:
        c = int(round(xa.to_pixel(float(x))))
        minw = 3 * max(L["xw"], L["yw"])  # a bar's top edge is wider than a tick mark

        def width(r):
            if not sub[r, c]:
                return 0
            a = c
            while a > 0 and sub[r, a - 1]:
                a -= 1
            b = c
            while b < sub.shape[1] - 1 and sub[r, b + 1]:
                b += 1
            return b - a + 1
        col = [r for r in range(sub.shape[0]) if lab[r, c] in standing and width(r) >= minw]
        if not col:
            r0 = base
            # a bar shorter than about two axis-line widths cannot be told from the axis and its tick
            hi = ya.to_value(base - 2 * L["xw"] - h0)
            out.append({"x": float(x), "y": 0.0, "lo": 0.0, "hi": max(hi, 0.0), "px": [c, r0],
                        "note": "no bar standing clear of the axis at this bin (at most a tick mark): zero, "
                                "or a bar lower than two axis-line widths; " + _note(info)})
            continue
        rt = top + min(col)
        # the top edge must be a horizontal edge (a bar), not a tick: check its width
        rowink = m[rt, c - 40:c + 41]
        w = int(rowink.sum())
        # the top stroke of an outlined bar: rows from rt while the ink is still a wide edge
        r = rt
        while r < base and width(r + 1 - top) >= minw and not cfg.get("filled", False):
            r += 1
        stroke = r - rt + 1 if not cfg.get("filled", False) else 0
        if stroke:
            edge = rt + stroke / 2  # the centre of the outline's top stroke
            lo, hi = _yint(ya, edge, stroke / 2 + h0)
        else:
            # a filled bar's edge stroke is centred on its top and cannot be told from the fill: take
            # it as wide as the axis line (the plotting default draws both alike) and allow a full
            # stroke either way
            edge = rt + L["xw"] / 2
            lo, hi = _yint(ya, edge, L["xw"] / 2 + h0)
        if base - rt < 4:
            hi = ya.to_value(base - 2 * L["xw"] - h0)
            out.append({"x": float(x), "y": 0.0, "lo": 0.0, "hi": max(hi, 0.0), "px": [c, base],
                        "note": "bar no taller than the axis line: zero or about one count; " + _note(info)})
            continue
        out.append({"x": float(x), "y": ya.to_value(edge), "lo": lo, "hi": hi, "px": [c, edge],
                    "note": f"bar top at row {edge:.1f} ({'filled' if cfg.get('filled') else 'outline'} bar, ink "
                            f"{w} px across); " + _note(info)})
    return out
