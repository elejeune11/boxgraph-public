"""Shared reading code for the data figures of Bangasser et al. 2017 (vector plots in the article,
Excel charts in the Supplementary Information), rendered by pdftoppm.

Each reading file (figures/<reading id>.py) holds a CONFIG dict and calls one reader below. The
reading file pins this file's SHA-256, because the build caches a reading by the reading file's
bytes.

Everything is found in the image. The only things typed in are the printed tick labels, the ink
colour of an axis and of a series, and which side the y axis is on (two panels have two y axes).

Calibration. An axis line is the longest straight run of the axis colour (the y axis on the chosen
side of the crop, the x axis in its lower part). Its tick marks are short runs of the same colour
leaving the line outward. Ticks are matched in order to the printed labels from the low end (every
k-th tick when there are more ticks than labels, evenly spaced), and a straight line (linear or
log10) is fitted; its largest misfit in pixels widens every interval.

Markers. A filled marker's fill is a disc of one colour inside a black outline. Its inner radius
Ri is the largest inscribed radius among the series' fill blobs (lines of the same colour are
removed by an opening wider than a line). A marker's centre is any point where (a) every visible
fill pixel of the marker lies within Ri + 1.5 px and (b) a disc of radius Ri - 2 px is all ink
(fill, outline, or another marker drawn over it). The set of such points is the reading: its
middle is the value and its extent (plus the calibration misfit and 1 px) the interval. A marker
partly hidden under another series' marker so gets an honestly wider interval; one hidden
entirely is located only to within the ink that hides it.

Error bars. The stem is the run of bar colour in a narrow band at the marker's column, above and
below the marker's outline; its end is the cap (a horizontal run at least three stem widths wide).
A stem that does not leave the marker is a bar hidden by the marker: its end is reported as at most
the marker's edge. A stem that stops at other ink without a cap is taken as the mirror of the other
end, and the reading says so.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from boxgraph import digitize as D


# ---------------------------------------------------------------- masks
def cmask(img, rgb, tol=70):
    d = np.sqrt(((img[:, :, :3].astype(float) - np.array(rgb, float)) ** 2).sum(axis=2))
    return d < tol


def hue(img, name):
    """A series colour by hue rather than by one RGB value (shaded raster markers: dark rim, light
    highlight, same hue)."""
    r, g, b = (img[:, :, i].astype(int) for i in range(3))
    if name == "blue":
        return (b - np.maximum(r, g) > 40)
    if name == "red":
        return (r - np.maximum(g, b) > 60)
    if name == "green":
        return (g - np.maximum(r, b) > 30)
    if name == "gold":
        return (r - b > 70) & (g - b > 40) & (r >= g)
    raise ValueError(name)


def black(img, thr=100):
    return img[:, :, :3].max(axis=2) < thr


def ink(img, thr=215):
    return img[:, :, :3].astype(float).min(axis=2) < thr


def _runs(idx):
    out = []
    for i in idx:
        if out and i == out[-1][1] + 1:
            out[-1][1] = i
        else:
            out.append([i, i])
    return [tuple(r) for r in out]


def _disk(r):
    r = int(max(1, round(r)))
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


# ---------------------------------------------------------------- axes
GAP = 160  # an axis line may pass under a marker's fill: bridge gaps up to this many px

def _line_cols(m, lo, hi, frac=0.9, outer="left"):
    """The y axis line among columns in [lo, hi): of the vertical lines nearly as long as the
    longest (bar edges can be), the outermost one on the axis side. Returns (c0, c1, top, bottom)."""
    # a line has an unbroken stretch of at least a quarter of the image (a stack of tick labels
    # bridged by the gap does not)
    rng = [c for c in range(max(0, lo), min(m.shape[1], hi)) if D._longest_run(m[:, c], gap=1)[0] >= 0.25 * m.shape[0]]
    runs = {c: D._longest_run(m[:, c], gap=GAP) for c in rng}
    best = max(r[0] for r in runs.values())
    cols = sorted(c for c, r in runs.items() if r[0] >= frac * best)
    groups = _runs(cols)
    grp = groups[0] if outer == "left" else groups[-1]
    tops = [runs[c][1] for c in range(grp[0], grp[1] + 1)]
    bots = [runs[c][2] for c in range(grp[0], grp[1] + 1)]
    return grp[0], grp[1], int(np.median(tops)), int(np.median(bots))


def _line_rows(m, lo, hi, frac=0.9):
    rng = [r for r in range(max(0, lo), min(m.shape[0], hi)) if D._longest_run(m[r, :], gap=1)[0] >= 0.25 * m.shape[1]]
    runs = {r: D._longest_run(m[r, :], gap=GAP) for r in rng}
    best = max(v[0] for v in runs.values())
    rows = sorted(r for r, v in runs.items() if v[0] >= frac * best)
    rbest = max(runs, key=lambda r: runs[r][0])
    grp = [g for g in _runs(rows) if g[0] <= rbest <= g[1]][0]
    lefts = [runs[r][1] for r in range(grp[0], grp[1] + 1)]
    rights = [runs[r][2] for r in range(grp[0], grp[1] + 1)]
    return grp[0], grp[1], int(np.median(lefts)), int(np.median(rights))


def _ticks(m, start, step, along, axis, minlen, maxlen, maxthick=30, skip=None):
    """Tick marks leaving a line: for each position along it, the run of ink from `start` going
    `step` (+1/-1) across. axis 'y': along rows (runs go along columns); 'x': along columns."""
    lens = []
    for t in along:
        n, p = 0, start
        lim = m.shape[1] if axis == "y" else m.shape[0]
        if skip is not None:  # coloured ink drawn over the tick's root (a curve along the axis)
            q = 0
            while q < 20 and 0 <= p < lim and (skip[t, p] if axis == "y" else skip[p, t]) and not (m[t, p] if axis == "y" else m[p, t]):
                p += step
                q += 1
        while 0 <= p < lim and (m[t, p] if axis == "y" else m[p, t]):
            n += 1
            p += step
        lens.append(n)
    ok = [i for i, n in enumerate(lens) if minlen <= n <= maxlen]
    out = []
    for s, e in _runs(ok):
        if e - s + 1 > maxthick:  # wider than a tick stroke: a marker or a label touching the line
            continue
        out.append((along[0] + (s + e) / 2.0 + 0.5, float(np.max(lens[s:e + 1]))))
    # tick marks share one length: keep the commonest length (+-4 px); other marks (a marker's
    # outline or an error bar cap touching the axis) are left out
    if out:
        Ls = [L for _, L in out]
        tol = lambda L0: max(4.0, 0.2 * L0)
        best = max(Ls, key=lambda L0: sum(1 for L1 in Ls if abs(L1 - L0) <= tol(L0)))
        out = [(p, L) for p, L in out if abs(L - best) <= tol(best)]
    return out


def _match(pos, labels, scale, every=None):
    """Tick positions (ascending in value) matched to labels (ascending)."""
    pos = sorted(pos)
    m = len(labels)
    if every:
        reg = pos if scale == "log10" else D.regular_ticks(pos, tol=8)
        sel = reg[::every][:m]
        if len(sel) != m:
            raise RuntimeError(f"{len(reg)} ticks, too few for {m} labels on every {every}th: {pos}")
        return list(zip(sel, labels)), f"every {every}th tick labelled"
    if len(pos) == m:
        return list(zip(pos, labels)), "every tick labelled"
    reg = D.regular_ticks(pos, tol=8)
    n = len(reg)
    if n == m:
        return list(zip(reg, labels)), "evenly spaced ticks, every one labelled"
    if m > 1 and n > m and (n - 1) % (m - 1) == 0:
        k = (n - 1) // (m - 1)
        return list(zip(reg[::k], labels)), f"every {k}th tick labelled"
    if 2 <= len(pos) < m:
        # some ticks hidden (under a marker): place the ticks found on the evenly spaced label grid
        step = float(min(np.diff(pos)))
        k = [int(round((p - pos[0]) / step)) for p in pos]
        if len(set(k)) == len(k) and k[-1] <= m - 1:
            b, a = np.polyfit(k, pos, 1)
            if max(abs(a + b * j - p) for p, j in zip(pos, k)) < 0.02 * b:
                # anchored at the low end (the lowest label sits at the axis corner, where its tick is found)
                return [(p, labels[j]) for p, j in zip(pos, k)], f"{len(pos)} of {m} ticks found (the others hidden), placed on the label grid from the low end"
    raise RuntimeError(f"{len(pos)} ticks ({n} evenly spaced) for {m} labels: {[round(p, 1) for p in pos]}")


def calibrate(img, cfg):
    """Returns xa, ya, info. cfg: ylabels, xlabels, yscale, xscale, yside ('left'|'right'),
    yrgb, xrgb (axis colours; black by default), yevery, xevery, tick (min, max) length in px."""
    H, W = img.shape[:2]
    my = cmask(img, cfg["yrgb"], 90) if cfg.get("yrgb") else black(img)
    mx = cmask(img, cfg["xrgb"], 90) if cfg.get("xrgb") else black(img)
    side = cfg.get("yside", "left")
    if side == "left":
        c0, c1, ytop, ybot = _line_cols(my, 0, int(W * 0.6))
    else:
        c0, c1, ytop, ybot = _line_cols(my, int(W * 0.4), W, outer="right")
    # the x axis line may be drawn over by curves near y = 0: then it is found in all ink
    r0, r1, xl, xr = _line_rows(ink(img, 160) if cfg.get("xaxis_any_ink") else mx, int(H * 0.3), H)
    tmin, tmax = cfg.get("tick", (8, 90))
    thick_y = int(2 * (r1 - r0 + 1) + 4)  # a tick stroke is about as thick as an axis line
    thick_x = int(2 * (c1 - c0 + 1) + 4)
    # y ticks: outward from the y axis line (left for a left axis, right for a right axis)
    along = list(range(max(0, ytop - 3), min(H, r1 + 4)))
    if side == "left":
        yt = _ticks(my, c0 - 1, -1, along, "y", tmin, tmax, thick_y)
    else:
        yt = _ticks(my, c1 + 1, +1, along, "y", tmin, tmax, thick_y)
    if cfg.get("yticks_inside"):
        yt += _ticks(my, c1 + 1 if side == "left" else c0 - 1, 1 if side == "left" else -1, along, "y", tmin, tmax, thick_y)
    ypos = sorted(set(round(p, 1) for p, _ in yt))
    if (cfg.get("yscale", "linear") == "linear" and cfg["ylabels"][0] == 0 and len(ypos) < len(cfg["ylabels"])
            and side == "left" and not cfg.get("no_zero_axis")):
        # the 0 tick hidden in the corner: the x axis line is the y = 0 row (the axis starts at 0)
        xr0 = (r0 + r1) / 2 + 0.5
        if all(abs(p - xr0) > 6 for p in ypos):
            ypos = sorted(ypos + [xr0])
    ymarks, ynote = _match([-p for p in ypos], cfg["ylabels"], cfg.get("yscale", "linear"), cfg.get("yevery"))
    ya = D.Axis(cfg.get("yscale", "linear"), [(-p, v) for p, v in ymarks])
    xa, xnote = None, ""
    if cfg.get("xlabels") is not None:
        a0, a1 = max(0, xl - 3), min(W, xr + 4)
        if side == "left":  # x ticks lie right of the y axis line (labels left of it are not ticks)
            a0 = max(a0, c0 - 3)
        if cfg.get("xrange"):  # where to look for x ticks, as fractions of the crop width
            a0, a1 = int(cfg["xrange"][0] * W), int(cfg["xrange"][1] * W)
        along = list(range(a0, a1))
        sk = ink(img, 160) if cfg.get("xaxis_any_ink") else None  # a tick may start under a curve
        xt = _ticks(mx, r1 + 1, +1, along, "x", tmin, tmax, thick_x, skip=sk)
        if cfg.get("xticks_inside"):
            xt += _ticks(mx, r0 - 1, -1, along, "x", tmin, tmax, thick_x)
        xpos = sorted(set(round(p, 1) for p, _ in xt))
        if cfg.get("xdrop"):  # tick-like marks to drop, by index from the left (e.g. a second y axis)
            xpos = [p for i, p in enumerate(xpos) if i not in cfg["xdrop"]]
        xmarks, xnote = _match(xpos, cfg["xlabels"], cfg.get("xscale", "linear"), cfg.get("xevery"))
        xa = D.Axis(cfg.get("xscale", "linear"), xmarks)
    info = {"ycol": (c0, c1), "ytop": ytop, "ybot": ybot, "xrow": (r0, r1), "xleft": xl, "xright": xr,
            "ynote": ynote, "xnote": xnote, "y_res": ya.residual_px, "x_res": xa.residual_px if xa else None,
            "yticks": ypos}
    return xa, ya, info


def _note(info):
    s = f"y axis: {info['ynote']}, misfit {info['y_res']:.2f} px"
    if info.get("x_res") is not None:
        s += f"; x axis: {info['xnote']}, misfit {info['x_res']:.2f} px"
    return s


def _yint(ya, r0, r1):
    a, b = ya.to_value(r0), ya.to_value(r1)
    return min(a, b), max(a, b)


def _plot_box(info, img):
    c0, c1 = info["ycol"]
    r0, r1 = info["xrow"]
    return int(info["ytop"]), int(r0), int(min(c0, info["xleft"])), int(info["xright"])


# ---------------------------------------------------------------- markers with error bars
def read_points(img, at, cfg):
    xa, ya, info = calibrate(img, cfg)
    H, W = img.shape[:2]
    fill = hue(img, cfg["hue"]) if cfg.get("hue") else cmask(img, cfg["rgb"], cfg.get("tol", 70))
    top, bot, left, right = _plot_box(info, img)
    if cfg.get("yside") == "right":
        lim_l, lim_r = int(info["xleft"]), int(info["ycol"][0])
    else:
        lim_l, lim_r = int(info["ycol"][1]) + 1, W
    region = np.zeros_like(fill)
    region[max(0, top - 60):bot + 80, max(0, lim_l - 80):min(W, lim_r + 80)] = True  # markers may sit on the axis
    for fx0, fy0, fx1, fy1 in cfg.get("exclude", []):  # legend keys etc., as fractions of the crop
        region[int(fy0 * H):int(fy1 * H), int(fx0 * W):int(fx1 * W)] = False
    fill &= region
    edt = ndimage.distance_transform_edt(fill)
    # inscribed radius of the fill discs: the largest blob maximum of the distance transform
    # (the median of those within 20% of it: unhidden markers)
    lab0, n0 = ndimage.label(fill)
    maxes = np.array(ndimage.maximum(edt, lab0, range(1, n0 + 1))) if n0 else np.array([0.0])
    ri = float(cfg["ri"]) if cfg.get("ri") else float(np.median(maxes[maxes >= 0.8 * maxes.max()]))
    # fill discs without the lines of the same colour: an opening wider than any line
    core = ndimage.binary_opening(fill, structure=_disk(cfg.get("open_frac", 0.6) * ri))
    lab, nl = ndimage.label(core)
    objs = ndimage.find_objects(lab)
    # outline thickness: black run sideways from the fill edge at each disc's middle row (median)
    bk0 = black(img, cfg.get("black", 110))
    th = []
    for j, sl in enumerate(objs, start=1):
        rr, cc = np.nonzero(lab[sl] == j)
        r = int(rr.mean()) + sl[0].start
        for c, step in ((cc.min() + sl[1].start - 1, -1), (cc.max() + sl[1].start + 1, 1)):
            n = 0
            while 0 <= c < W and bk0[r, c] and n < ri:
                n += 1
                c += step
            th.append(n)
    t_out = float(np.median(th)) if th else 0.0
    inkm = ink(img)
    ink_edt = ndimage.distance_transform_edt(inkm)
    bar = cmask(img, cfg["bar_rgb"], cfg.get("bar_tol", 90)) if cfg.get("bar_rgb") else black(img, cfg.get("black", 110))
    bar[:, max(0, info["ycol"][0] - 2):info["ycol"][1] + 3] = False  # a stem along the y axis cannot be told from it
    if cfg.get("hue"):
        bar &= ~hue(img, cfg["hue"])  # a dark marker fill of the series' hue is not a black stem
    h0 = 1.0 + info["y_res"]
    from_image = not at
    if from_image:  # every marker of the series, left to right; x is read from the image
        cents = sorted(((sl[1].start + sl[1].stop) / 2.0 for j, sl in enumerate(objs, start=1) if sl is not None
                        and (lab[sl] == j).sum() <= 1.5 * np.pi * ri * ri))
        at = [xa.to_value(c) for c in cents]
    atc = [xa.to_pixel(float(x)) for x in at]
    out = []
    for i, x in enumerate(at):
        c0 = atc[i]
        gaps = [abs(c0 - a) for j, a in enumerate(atc) if j != i]
        win = min([2.0 * ri + 6] + [0.5 * g for g in gaps])
        # visible fill blobs whose centroid lies within the window
        cand = []
        for j, sl in enumerate(objs, start=1):
            if sl is None:
                continue
            rr, cc = np.nonzero(lab[sl] == j)
            cc = cc + sl[1].start
            rr = rr + sl[0].start
            # a marker's fill blob is about a disc of radius ri (a fill cut by a stem is less);
            # a larger blob is a thick line of the series' colour, not a marker
            if abs(cc.mean() - c0) <= win and len(rr) <= 1.5 * np.pi * ri * ri:
                cand.append((len(rr), rr, cc))
        hint = cfg.get("pick", {}).get(str(x)) if cfg.get("pick") else None
        hidden = False
        if not cand:
            # hidden: centre anywhere a fill disc fits inside ink, near raw fill pixels in the window
            rawr, rawc = np.nonzero(fill[:, max(0, int(c0 - win)):int(c0 + win) + 1])
            if len(rawr) == 0:
                out.append({"x": float(x), "y": None, "note": "no ink of this series near this x: not drawn or hidden entirely"})
                continue
            rows = range(max(0, rawr.min() - int(2 * ri)), min(H, rawr.max() + int(2 * ri)))
            cols = range(max(0, int(c0 - win)), min(W, int(c0 + win) + 1))
            F = [(r, c) for r in rows for c in cols if ink_edt[r, c] >= ri - 2]
            how = "marker hidden under other ink: centre anywhere a fill disc fits in that ink; its error bar is not read"
            hidden = True
        else:
            if hint == "top":
                n, rr, cc = min(cand, key=lambda t: t[1].mean())
            elif hint == "bottom":
                n, rr, cc = max(cand, key=lambda t: t[1].mean())
            else:
                n, rr, cc = max(cand, key=lambda t: t[0])
            # boundary pixels of the blob (subsampled)
            pts = np.stack([rr + 0.5, cc + 0.5], axis=1)
            if len(pts) > 600:
                pts = pts[np.linspace(0, len(pts) - 1, 600).astype(int)]
            R0, R1 = int(rr.min() - ri - 3), int(rr.max() + ri + 4)
            C0, C1 = int(cc.min() - ri - 3), int(cc.max() + ri + 4)
            gr, gc = np.mgrid[max(0, R0):min(H, R1), max(0, C0):min(W, C1)]
            gr = gr.ravel()
            gc = gc.ravel()
            F = []
            for slack in (2.0, 4.0, 6.0):  # relaxed when the fill is cut by a stem or a line drawn over it
                okb = ink_edt[gr, gc] >= ri - slack
                g1, c1 = gr[okb], gc[okb]
                if len(g1):
                    d2 = ((g1[:, None] + 0.5 - pts[None, :, 0]) ** 2 + (c1[:, None] + 0.5 - pts[None, :, 1]) ** 2).max(axis=1)
                    sel = d2 <= (ri + slack) ** 2
                    F = list(zip(g1[sel], c1[sel]))
                if F:
                    break
            how = f"fill blob of {n} px (inscribed radius of the series {ri:.1f} px, slack {slack:.0f} px)"
            if not F:
                q = int(round(ri / 3))
                F = [(int(round(rr.mean())) + d, int(round(cc.mean()))) for d in (-q, q)]
                how += "; no centre satisfied both conditions: blob centroid +- a third of the radius"
        if not F:
            out.append({"x": float(x), "y": None, "note": "no marker of this series found here (only lines of its colour)"})
            continue
        Fr = np.array([f[0] for f in F], float) + 0.5
        Fc = np.array([f[1] for f in F], float) + 0.5
        rc = (Fr.min() + Fr.max()) / 2
        cc_ = (Fc.min() + Fc.max()) / 2
        lo, hi = _yint(ya, Fr.min() - h0, Fr.max() + h0)
        rd = {"x": float(xa.to_value(cc_)) if from_image else float(x), "y": ya.to_value(rc), "lo": lo, "hi": hi, "px": [cc_, rc]}
        notes = ["x read from the image" if from_image else "x as given", f"{how}; centre rows {Fr.min():.0f}-{Fr.max():.0f}, column {cc_:.0f} (x read back {xa.to_value(cc_):.4g})"]
        if cfg.get("error_bars", True) and not hidden:
            _bars(rd, bar, fill, ya, rc, cc_, ri, t_out, h0, notes, cfg)
        rd["note"] = "; ".join(notes) + "; " + _note(info)
        out.append(rd)
    return out


def _bars(rd, bar, fill, ya, rc, cc, ri, t_out, h0, notes, cfg):
    """Error bar ends above and below a marker centred at (rc, cc)."""
    H, W = bar.shape
    c = int(cc)
    band = cfg.get("band", 3)

    def width(r):
        if not (0 <= r < H):
            return 0
        row = bar[r, c - band:c + band + 1]
        if not row.any():
            return 0
        c1 = c - band + int(np.argmax(row))
        a = b = c1
        while a > 0 and bar[r, a - 1]:
            a -= 1
        while b < W - 1 and bar[r, b + 1]:
            b += 1
        return b - a + 1

    res = {}
    for name, step in (("hi", -1), ("lo", +1)):
        # the marker's edge in this direction: the end of its fill, then its outline
        r = int(rc)
        n = 0
        while 0 <= r < H and fill[r, c] and n < 2 * ri:
            r += step
            n += 1
        if n < 0.5 * ri:  # fill hidden here: the nominal edge
            r = int(round(rc + step * ri))
        edge = r + step * t_out
        start = int(round(edge))
        thr = 3 * band + 6
        ws = []
        r = start
        gap = 0
        last = None
        cap = None

        def straight(rows):
            w = [width(q) for q in rows]
            return max(w) <= 1.3 * min(w) + 2

        while 0 <= r < H and gap <= 2:
            w = width(r)
            if w == 0:
                gap += 1
            else:
                gap = 0
                sw = float(min(ws)) if len(ws) >= 3 else None
                wide = w >= (max(2.5 * sw, sw + 8) if sw is not None else thr)
                if wide and (sw is not None or abs(r - start) <= 2):
                    # a wide row: a cap if it is a straight stroke followed by white, else other ink
                    rows = [r]
                    rr = r + step
                    while 0 <= rr < H and width(rr) >= (max(2.5 * sw, sw + 8) if sw is not None else thr) and len(rows) < 30:
                        rows.append(rr)
                        rr += step
                    after = [width(rr + step * q) for q in range(0, 3)]
                    if all(a == 0 for a in after) and straight(rows):
                        if sw is None:  # a cap flush with the outline: its stroke taken as the outline's
                            outer = rows[-1]
                            inner = outer - step * max(len(rows) - 1, int(round(t_out)) - 1)
                            cap = (min(inner, outer), max(inner, outer))
                        else:
                            cap = (min(rows), max(rows))
                        break
                    if sw is not None:
                        cap = "other"
                        break
                    # not a cap at the outline: the outline's remnant where the stem leaves it
                ws.append(w)
                last = r
            r += step
        res[name] = (edge, last, cap)
    for name, step in (("hi", -1), ("lo", +1)):
        edge, last, cap = res[name]
        word = "upper" if step < 0 else "lower"
        oth = res["lo" if name == "hi" else "hi"]
        if isinstance(cap, tuple):
            row = (cap[0] + cap[1]) / 2 + 0.5
            half = (cap[1] - cap[0] + 1) / 2
            rd[f"bar_{name}"] = ya.to_value(row)
            rd[f"bar_{name}_outer"] = ya.to_value(row + step * (half + h0))
        elif last is None and cap is None:
            row = edge
            rd[f"bar_{name}"] = ya.to_value(row)
            rd[f"bar_{name}_outer"] = ya.to_value(row + step * h0)
            notes.append(f"{word} bar end inside the marker: at most the marker's edge")
        elif isinstance(oth[2], tuple):
            orow = (oth[2][0] + oth[2][1]) / 2 + 0.5
            row = 2 * rc - orow
            half = (oth[2][1] - oth[2][0] + 1) / 2
            rd[f"bar_{name}"] = ya.to_value(row)
            rd[f"bar_{name}_outer"] = ya.to_value(row + step * (half + h0))
            notes.append(f"{word} bar end hidden by other ink: taken as the mirror of the other end")
        else:
            row = (last if last is not None else edge) + 0.5
            rd[f"bar_{name}"] = ya.to_value(row)
            rd[f"bar_{name}_outer"] = ya.to_value(row + step * (h0 + 6))
            notes.append(f"{word} bar end: no cap found, the stem's visible end (widened by 6 px)")
        rd["px_lo" if name == "hi" else "px_hi"] = row


# ---------------------------------------------------------------- bar charts
def read_barchart(img, at, cfg):
    """Bars with black outlines standing on the x axis, read left to right (at = 1, 2, ...). The
    value is the middle of the bar's top outline stroke; the error bar is the black stem at the
    bar's middle column, above the top (and below it, inside the bar), ended by caps."""
    xa, ya, info = calibrate(img, dict(cfg, xlabels=None))
    bk = black(img, cfg.get("black", 110))
    r0, r1 = info["xrow"]
    c0, c1 = info["ycol"]
    H, W = img.shape[:2]
    lo_c = c1 + 3 if cfg.get("yside", "left") == "left" else 0
    hi_c = W if cfg.get("yside", "left") == "left" else c0 - 3
    # long vertical black runs ending on the axis line: bar edges
    runlen = np.zeros(W, int)
    tops = np.zeros(W, int)
    for c in range(lo_c, hi_c):
        r = r0 - 1
        n = 0
        while r >= 0 and bk[r, c]:
            n += 1
            r -= 1
        runlen[c] = n
        tops[c] = r + 1
    minh = cfg.get("min_edge", 25)
    cols = [c for c in range(lo_c, hi_c) if runlen[c] >= minh]
    edges = [g for g in _runs(cols)]
    # an edge is a few px wide; the error bar stem inside a bar does not reach the axis
    edges = [g for g in edges if g[1] - g[0] <= 40]
    if edges:  # bar edges share one stroke width; a narrower run (a stem or hatching) is not an edge
        wmed = float(np.median([g[1] - g[0] + 1 for g in edges]))
        edges = [g for g in edges if abs(g[1] - g[0] + 1 - wmed) <= 4]
    # pair edges into bars: a bar's width is the distance between the first two edges (the first
    # bar's left edge stands on the axis next to the y axis); an edge with no partner at that
    # distance (its partner broken by hatching) gets one synthesized at that distance
    if len(edges) < 2:
        raise RuntimeError(f"{len(edges)} bar edges found: {edges}")
    wbar = edges[1][0] - edges[0][0]
    bars, i, synth = [], 0, 0
    while i < len(edges):
        a = edges[i]
        if i + 1 < len(edges) and abs(edges[i + 1][0] - a[0] - wbar) <= 0.1 * wbar:
            bars.append((a, edges[i + 1]))
            i += 2
        else:
            bars.append((a, (a[0] + wbar, a[1] + wbar)))
            synth += 1
            i += 1
    h0 = 1.0 + info["y_res"]
    out = []
    for x in at:
        i = int(round(float(x))) - 1
        if i >= len(bars):
            out.append({"x": float(x), "y": None, "note": f"only {len(bars)} bars found"})
            continue
        (a0, a1), (b0, b1) = bars[i]
        mid = int((a0 + b1) / 2)
        # top stroke: rows of black spanning the bar between the edges, near the edges' tops
        t = int(min(tops[a0:a1 + 1].min(), tops[b0:b1 + 1].min()))
        span = range(a1 + 3, b0 - 2)
        rows = [r for r in range(t, min(r0, t + 60)) if bk[r, list(span)].mean() > 0.6]
        if not rows:
            out.append({"x": float(x), "y": None, "note": "no top stroke found"})
            continue
        g = _runs(rows)[0]
        rt = (g[0] + g[1]) / 2 + 0.5
        sh = (g[1] - g[0] + 1) / 2
        lo, hi = _yint(ya, rt - sh - h0, rt + sh + h0)
        rd = {"x": float(x), "y": ya.to_value(rt), "lo": lo, "hi": hi, "px": [mid, rt]}
        notes = [f"bar {i + 1} between columns {a0}-{b1}; top stroke rows {g[0]}-{g[1]}"]
        # error bar: stem above the top stroke at the bar's middle column
        band = 3

        def present(r):
            return bk[r, mid - band:mid + band + 1].any()

        def width(r):
            row = bk[r, mid - 40:mid + 41]
            if not row[40 - band:40 + band + 1].any():
                return 0
            cc = 40 - band + int(np.argmax(row[40 - band:40 + band + 1]))
            a = b = cc
            while a > 0 and row[a - 1]:
                a -= 1
            while b < len(row) - 1 and row[b + 1]:
                b += 1
            return b - a + 1
        r = g[0] - 1
        last = None
        gap = 0
        while r > 0 and gap <= 2:
            if present(r):
                last, gap = r, 0
            else:
                gap += 1
            r -= 1
        if last is None or g[0] - last < 4:
            rd["bar_hi"] = rd["y"]
            rd["bar_hi_outer"] = ya.to_value(g[0] - h0)
            rd["px_lo"] = g[0]
            notes.append("no stem above the bar: upper end at most the top stroke")
            up = None
        else:
            sw = max(2, width((g[0] + last) // 2))
            caps = [rr for rr in range(last, g[0]) if width(rr) >= 3 * sw]
            cg = _runs(caps)
            if cg and cg[0][0] - last <= 3:
                cap = cg[0]
                rr = (cap[0] + cap[1]) / 2 + 0.5
                rd["bar_hi"] = ya.to_value(rr)
                rd["bar_hi_outer"] = ya.to_value(rr - (cap[1] - cap[0] + 1) / 2 - h0)
            else:
                rr = last + 0.5
                rd["bar_hi"] = ya.to_value(rr)
                rd["bar_hi_outer"] = ya.to_value(rr - h0)
                notes.append("upper cap not found: the stem's end")
            rd["px_lo"] = rr
            up = rr
        # lower end: below the top stroke, inside the bar
        r = g[1] + 1
        caps = []
        while r < r0 - 2:
            if width(r) >= 12 and width(r) < (b0 - a1) * 0.9:
                caps.append(r)
            elif caps and r - caps[-1] > 2:
                break
            r += 1
        cg = _runs(caps)
        if cg and present(cg[0][0] - 2):
            cap = cg[0]
            rr = (cap[0] + cap[1]) / 2 + 0.5
            rd["bar_lo"] = ya.to_value(rr)
            rd["bar_lo_outer"] = ya.to_value(rr + (cap[1] - cap[0] + 1) / 2 + h0)
            rd["px_hi"] = rr
        elif up is not None:
            rr = 2 * rt - up
            rd["bar_lo"] = ya.to_value(rr)
            rd["bar_lo_outer"] = ya.to_value(rr + h0 + sh)
            rd["px_hi"] = rr
            notes.append("lower end hidden in the bar: taken as the mirror of the upper")
        else:
            rd["bar_lo"] = rd["y"]
            rd["bar_lo_outer"] = ya.to_value(g[1] + h0)
            rd["px_hi"] = g[1]
            notes.append("no error bar drawn: at most the stroke")
        rd["note"] = "; ".join(notes) + "; " + _note(info)
        out.append(rd)
    return out


# ---------------------------------------------------------------- curves
def read_curve(img, at, cfg):
    """A curve of one colour traced column by column from a starting run ('start': 'top',
    'bottom' or a value of y near which to start), read at the given x. Marker blobs of the same
    colour (fill discs) are removed first. The value is the middle of the run of curve colour in
    that column; the interval is the run's extent plus the misfit."""
    xa, ya, info = calibrate(img, cfg)
    m = cmask(img, cfg["rgb"], cfg.get("tol", 70))
    top, bot, left, right = _plot_box(info, img)
    m[:max(0, top - 5)] = False
    m[bot:] = False
    if cfg.get("yside", "left") == "left":
        m[:, :info["ycol"][1] + 2] = False
    if cfg.get("remove_markers", True):
        edt = ndimage.distance_transform_edt(m)
        lw = cfg.get("line_halfwidth", 8)
        blobs = ndimage.binary_dilation(edt > lw, structure=_disk(cfg.get("marker_r", 40)))
        m &= ~blobs
    h0 = 1.0 + info["y_res"]
    out = []
    want = {float(x): xa.to_pixel(float(x)) for x in at}
    cols = sorted(int(round(c)) for c in want.values())
    # trace from the first column with ink, following the run nearest the previous one
    W = m.shape[1]
    c_start = max(0, min(cols))
    c_end = min(W - 1, max(cols))
    prev = None
    path = {}
    start = cfg.get("start", "top")
    for c in range(c_start, c_end + 1):
        rr = np.nonzero(m[:, c])[0]
        if len(rr) == 0:
            continue
        segs = []
        for a, b in _runs(list(rr)):  # runs split by a few px of antialiasing are one run
            if segs and a - segs[-1][1] <= cfg.get("merge", 1):
                segs[-1] = (segs[-1][0], b)
            else:
                segs.append((a, b))
        rs = [(a + b) / 2 for a, b in segs]
        ext = {(a + b) / 2: (a, b) for a, b in segs}
        if prev is None:
            if start == "top":
                r = min(rs)
            elif start == "bottom":
                r = max(rs)
            else:
                rp = ya.to_pixel(float(start))
                r = min(rs, key=lambda q: abs(q - rp))
        else:
            r = min(rs, key=lambda q: abs(q - prev))
            if abs(r - prev) > cfg.get("max_jump", 60):
                continue
        prev = r
        path[c] = ext[r]
    for x, cpx in want.items():
        c = int(round(cpx))
        near = [k for k in path if abs(k - c) <= cfg.get("near", 2)]
        if not near:
            out.append({"x": x, "y": None, "note": "curve not visible in this column (hidden or outside the plot)"})
            continue
        k = min(near, key=lambda q: abs(q - c))
        a, b = path[k]
        r = (a + b) / 2 + 0.5
        lo, hi = _yint(ya, a - h0, b + 1 + h0)
        out.append({"x": x, "y": ya.to_value(r), "lo": lo, "hi": hi, "px": [k + 0.5, r],
                    "note": f"run rows {a}-{b} in column {k}; " + _note(info)})
    return out
