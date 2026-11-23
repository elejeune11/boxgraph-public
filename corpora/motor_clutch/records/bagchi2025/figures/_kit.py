"""Shared readers for the point, star, bar and line panels of this paper added in the
second pass (Figs 1, 2, 4, 6, 7, 8m, 9, 10l-m, 11l and S1-S5 Figs).

Axes are calibrated by _panel.calibrate (the axis lines and their tick marks found in
the image, matched in order to the printed labels the calling file gives; those labels
are the only values typed in). On top of it:

  rings    open circular markers (Fig 7): the hue mask is correlated with a thin ring
           whose radius is chosen as the one with the strongest response; a marker is a
           local maximum covering most of the ring. Lines joining the markers cover
           only two short arcs of a ring and are not taken.
  blobs    filled markers (stars, dots): connected parts of the hue mask, opened to
           strip thin joining lines, of a marker's size; the value is the centroid.
  bars     bar charts and histograms: in each bar's column span (found in the image
           as runs of columns where the bar colour stands on the baseline) the top
           edge is the median first row of the colour.
  stacked  bars of two colours drawn one above the other: the top of each colour.

Intervals (95%): one pixel of edge, plus the calibration misfit of the axis, plus for
markers a quarter of the marker's half-size (where its centre is in a resampled bitmap).
A region given in data units (`exclude`) is blanked before reading: a legend.
"""
import importlib.util
import os

import numpy as np
from scipy import ndimage, signal

_spec = importlib.util.spec_from_file_location("bagchi2025_panel", os.path.join(os.path.dirname(__file__), "_panel.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

hue_mask = P.hue_mask


def calibrate(img, xlabels, ylabels, x_corner=None, y_corner=None, tick_len=0.006, out_x=False, out_y=False,
              skip_x=0, skip_y=0, own=False):
    """As _panel.calibrate, with tick marks that may point out of the plot (out_x, out_y:
    below the x axis, left of the y axis). skip_x/skip_y: ticks found before the first
    labelled one (an unlabelled tick at the start of the axis)."""
    if not (out_x or out_y or skip_x or skip_y or own):
        return P.calibrate(img, xlabels, ylabels, x_corner, y_corner, tick_len)
    nd = P._neutral_dark(img)
    H, W = nd.shape
    c0, c1, yr0, yr1 = P._axis_line(nd, "col", 0.0, 0.45)
    r0, r1, xc0, xc1 = P._axis_line(nd, "row", 0.45, 1.0)
    L = max(6, int(tick_len * W))
    ystrip = (nd[:, max(0, c0 - 2 - L):c0 - 2] if out_y else nd[:, c1 + 2:c1 + 2 + L]).sum(axis=1)
    xstrip = (nd[r1 + 2:r1 + 2 + L, :] if out_x else nd[r0 - 2 - L:r0 - 2, :]).sum(axis=0)
    ycand = P._ticks(ystrip, yr0, r0 - (2 if out_y else 10), 0.6 * L)
    xcand = P._ticks(xstrip, c1 + (2 if out_x else 10), min(xc1 + 1, W), 0.6 * L)
    yt = sorted(ycand, reverse=True)[skip_y:]
    xt = sorted(xcand)[skip_x:]
    if len(yt) < len(ylabels) or len(xt) < len(xlabels):
        raise ValueError(f"ticks found x {xcand} y {ycand}; need {len(xlabels)} and {len(ylabels)}")
    ymarks = list(zip(yt[:len(ylabels)], ylabels))
    xmarks = list(zip(xt[:len(xlabels)], xlabels))
    for t in ([p for p, _ in ymarks], [p for p, _ in xmarks]):
        d = np.abs(np.diff(t))
        if len(d) > 1 and (d.max() - d.min()) > 0.05 * np.median(d):
            raise ValueError(f"uneven ticks {t}")
    if y_corner is not None:
        ymarks.append(((r0 + r1) / 2.0 + 0.5, y_corner))
    if x_corner is not None:
        xmarks.append(((c0 + c1) / 2.0 + 0.5, x_corner))
    if not xmarks:  # a category axis: x is the order of the marks (see run_spec, x_order)
        xmarks = [(0.0, 0.0), (1.0, 1.0)]
    Y, X = np.array(ymarks, float), np.array(xmarks, float)
    by, ay = np.polyfit(Y[:, 1], Y[:, 0], 1)
    bx, ax = np.polyfit(X[:, 1], X[:, 0], 1)
    mis_y = max(0.5, float(np.max(np.abs(Y[:, 0] - (ay + by * Y[:, 1])))))
    mis_x = max(0.5, float(np.max(np.abs(X[:, 0] - (ax + bx * X[:, 1])))))
    return dict(ay=ay, by=by, ax=ax, bx=bx, mis_y=mis_y, mis_x=mis_x, left=c1 + 1, bottom=r0, n_x=len(X), n_y=len(Y))
read_curve = P.read_curve


def px_x(cal, v):
    return cal["ax"] + cal["bx"] * v


def px_y(cal, v):
    return cal["ay"] + cal["by"] * v


def val_x(cal, c):
    return (c - cal["ax"]) / cal["bx"]


def val_y(cal, r):
    return (r - cal["ay"]) / cal["by"]


def inside(mask, cal, exclude=(), margin=4):
    """The mask within the plot (right of the y axis, above the x axis), with
    regions given in data units (x0, x1, y0, y1) blanked."""
    m = mask.copy()
    m[:, :int(cal["left"]) + margin] = False
    m[int(cal["bottom"]) - margin:, :] = False
    for x0, x1, y0, y1 in exclude:
        c0, c1 = sorted((px_x(cal, x0), px_x(cal, x1)))
        r0, r1 = sorted((px_y(cal, y0), px_y(cal, y1)))
        m[max(0, int(r0)):int(r1) + 1, max(0, int(c0)):int(c1) + 1] = False
    return m


def _note(cal):
    return f"x {cal['n_x']} marks misfit {cal['mis_x']:.2f} px; y {cal['n_y']} marks misfit {cal['mis_y']:.2f} px"


def _point(cal, c, r, size, what):
    h = 1.0 + cal["mis_y"] + size / 4.0
    a, b = val_y(cal, r - h), val_y(cal, r + h)
    return {"x": float(val_x(cal, c)), "y": float(val_y(cal, r)), "lo": float(min(a, b)), "hi": float(max(a, b)),
            "px": [float(c), float(r)], "px_lo": float(r - h), "px_hi": float(r + h),
            "note": f"{what}; x read as {val_x(cal, c):.4g} (+-{(1.0 + cal['mis_x'] + size / 4.0) / abs(cal['bx']):.2g}); "
                    + _note(cal)}


def rings(mask, cal, rmin, rmax, cover=0.55):
    """Centres of open circles in the mask (radius searched from rmin to rmax px)."""
    m = mask.astype(float)
    best = None
    for R in range(int(rmin), int(rmax) + 1, 2):
        yy, xx = np.mgrid[-R - 3:R + 4, -R - 3:R + 4]
        d = np.hypot(yy, xx)
        k = (np.abs(d - R) <= 2.0).astype(float)
        resp = signal.fftconvolve(m, k[::-1, ::-1], mode="same") / k.sum()
        if best is None or resp.max() > best[1].max():
            best = (R, resp)
    R, resp = best
    peaks = (resp == ndimage.maximum_filter(resp, size=2 * R + 1)) & (resp >= cover)
    lab, n = ndimage.label(peaks)
    out = []
    for i in range(1, n + 1):
        rr, cc = np.nonzero(lab == i)
        c, r = cc.mean() + 0.5, rr.mean() + 0.5
        near = [k for k, (c2, r2, _) in enumerate(out) if np.hypot(c - c2, r - r2) < R]
        if near:  # a flat top of the response split in two: one marker
            k = near[0]
            out[k] = ((out[k][0] + c) / 2, (out[k][1] + r) / 2, R)
        else:
            out.append((c, r, R))
    return sorted(out)


def read_rings(image, cal, mask, rmin, rmax, exclude=()):
    m = inside(mask, cal, exclude, margin=-int(rmax))  # a marker may sit on an axis
    m[:, :max(0, int(cal["left"]) - 2)] = False
    return [_point(cal, c, r, R, f"open circle, radius {R} px") for c, r, R in rings(m, cal, rmin, rmax)]


def read_blobs(image, cal, mask, min_area, open_px=3, exclude=(), max_area=None, fill=False, wide=False):
    """Filled markers: centroids of connected parts of the mask, thin lines opened away."""
    m = inside(mask, cal, exclude, margin=2)
    if fill:  # small open circles: fill them, so that opening keeps them and strips the dashes
        m = ndimage.binary_fill_holes(ndimage.binary_closing(m, structure=np.ones((3, 3), bool)))
    if open_px:
        m = ndimage.binary_opening(m, structure=np.ones((open_px, open_px), bool))
    else:  # thin strokes (asterisks): join the strokes of one marker
        m = ndimage.binary_closing(m, structure=np.ones((9, 9), bool))
    lab, n = ndimage.label(m)
    out = []
    for i in range(1, n + 1):
        rr, cc = np.nonzero(lab == i)
        if len(rr) < min_area or (max_area and len(rr) > max_area):
            continue
        if wide and (cc.max() - cc.min() + 1) < 3 * (rr.max() - rr.min() + 1):
            continue  # a median line is wide and flat; an outlier "+" is not
        size = max(rr.max() - rr.min() + 1, cc.max() - cc.min() + 1) / 2.0
        out.append(_point(cal, cc.mean() + 0.5, rr.mean() + 0.5, size, f"filled marker of {len(rr)} px"))
    return sorted(out, key=lambda d: d["x"])


def bar_spans(mask, cal, min_width=6, min_height=3):
    """Column spans (c0, c1 inclusive) where the colour stands on the baseline."""
    base = int(cal["bottom"]) - 4
    on = mask[base - min_height:base, :].sum(axis=0) >= min_height
    on[:int(cal["left"]) + 2] = False
    spans, c = [], 0
    W = len(on)
    while c < W:
        if on[c]:
            s = c
            while c + 1 < W and on[c + 1]:
                c += 1
            if c - s + 1 >= min_width:
                if spans and s - spans[-1][1] <= 30:  # an x tick mark interrupts a bar's foot
                    spans[-1] = (spans[-1][0], c)
                else:
                    spans.append((s, c))
        c += 1
    return spans


def top_edge(mask, c0, c1, below=None):
    """Median first row of the mask in columns c0..c1 (the middle 60%), over rows above `below`."""
    w = c1 - c0 + 1
    a, b = c0 + int(0.2 * w), c1 - int(0.2 * w)
    tops = []
    for c in range(a, b + 1):
        col = mask[:below, c] if below else mask[:, c]
        rows = np.nonzero(col)[0]
        if len(rows):
            tops.append(rows[0])
    return float(np.median(tops)) if tops else None, float(np.std(tops)) if tops else 0.0


def bar_value(cal, c0, c1, top, spread, what):
    r = top  # the first row of the bar: its edge is the top of that pixel
    h = 1.0 + cal["mis_y"] + 2 * spread
    a, b = val_y(cal, r - h), val_y(cal, r + h)
    c = (c0 + c1 + 1) / 2.0
    return {"x": float(val_x(cal, c)), "y": float(val_y(cal, r)), "lo": float(min(a, b)), "hi": float(max(a, b)),
            "px": [float(c), float(r)], "px_lo": float(r - h), "px_hi": float(r + h),
            "note": f"{what}, columns {c0}-{c1}; " + _note(cal)}


def _fit_spacing(cands, origin, span, tol=3.0, sign=1):
    """The tick spacing s (px) for which most candidates sit at origin + sign*k*s (k >= 1);
    ties go to the wider spacing. Returns [(position, k), ...] of the matched ticks."""
    best = (0, 0.0, [])
    for s in np.arange(20.0, span, 0.25):
        m = []
        for c in cands:
            k = round(sign * (c - origin) / s)
            if k >= 1 and abs(origin + sign * k * s - c) <= tol:
                m.append((c, k))
        if len({k for _, k in m}) > best[0] or (len({k for _, k in m}) == best[0] and s > best[1]):
            best = (len({k for _, k in m}), s, m)
    m = best[2]
    while m and all(k % 2 == 0 for _, k in m):  # every match at an even multiple: the spacing is twice
        m = [(c, k // 2) for c, k in m]
    return m


def calibrate_fit(img, xstep, ystep, x_corner, y_corner, tick_len=0.006, dark=140, frame=False, top_ticks=False,
                  x_first=None, min_ticks=2):
    """Axes whose ticks are partly hidden (by curves drawn over them, or a broken axis
    line): the tick marks that are visible are found along the whole axis, and the
    evenly spaced set that starts at the corner of the axes (labelled x_corner, y_corner)
    is kept; a tick k spacings from the corner carries the label corner + k * step
    (xstep, ystep: the printed spacing of the labels). dark: the grey level below which a
    neutral pixel is ink (raised for blurred bitmaps, whose thin ticks print grey)."""
    _, sat, val = P.hue(img)
    nd = (sat < 40) & (val < dark)
    H, W = nd.shape
    c0, c1, yr0, yr1 = P._axis_line(nd, "col", 0.0, 0.45)
    r0, r1, xc0, xc1 = P._axis_line(nd, "row", 0.45, 1.0)
    if xc1 - xc0 < 0.4 * W:  # the x axis line is drawn over by curves lying on it: it ends the y axis
        r1 = yr1 - 1
        r0 = r1 - (c1 - c0)
    L = max(6, int(tick_len * W))
    ystrip = nd[:, c1 + 2:c1 + 2 + L].sum(axis=1)
    xstrip = nd[r0 - 2 - L:r0 - 2, :].sum(axis=0)
    if top_ticks:  # the x ticks hidden by bars on the axis: read those hanging from the top frame
        ends = []
        for mc in np.linspace(xc0 + 40, xc1 - 40, 17).astype(int):  # the lower edge of the frame line,
            fr = max(0, yr0 - 10)                                       # as most columns see it (not a tick)
            while fr < r0 and not nd[fr, mc]:
                fr += 1
            while fr < r0 and nd[fr, mc]:
                fr += 1
            ends.append(fr)
        fr = int(np.median(ends))
        xstrip = nd[fr + 1:fr + 1 + L, :].sum(axis=0)
    ycand = P._ticks(ystrip, 0, r0 - 10, 0.6 * L)
    xcand = P._ticks(xstrip, c1 + 10, W, 0.6 * L)
    if frame:  # leave out the corners of a box frame: the top end of the y axis, the right end of the x axis
        ycand = [p for p in ycand if p > yr0 + 15]
        xcand = [p for p in xcand if p < xc1 - 15]
    xc, yc = (c0 + c1) / 2.0 + 0.5, (r0 + r1) / 2.0 + 0.5
    if x_corner is None:  # the corner carries no label: the first tick found carries x_first
        if not xcand:
            raise ValueError("no x ticks found")
        xc, x_corner = xcand[0], x_first
        xcand = xcand[1:]
    xm = _fit_spacing(xcand, xc, W - xc)
    ym = _fit_spacing(ycand, yc, yc, sign=-1)
    if len(xm) < min_ticks or len(ym) < min_ticks:
        raise ValueError(f"ticks x {xcand} y {ycand}: too few on an even spacing from the corner")
    X = np.array([(xc, x_corner)] + [(c, x_corner + k * xstep) for c, k in xm], float)
    Y = np.array([(yc, y_corner)] + [(r, y_corner + k * ystep) for r, k in ym], float)
    by, ay = np.polyfit(Y[:, 1], Y[:, 0], 1)
    bx, ax = np.polyfit(X[:, 1], X[:, 0], 1)
    mis_y = max(0.5, float(np.max(np.abs(Y[:, 0] - (ay + by * Y[:, 1])))))
    mis_x = max(0.5, float(np.max(np.abs(X[:, 0] - (ax + bx * X[:, 1])))))
    return dict(ay=ay, by=by, ax=ax, bx=bx, mis_y=mis_y, mis_x=mis_x, left=c1 + 1, bottom=r0, n_x=len(X), n_y=len(Y))


def run_spec(rid, image, at):
    """Read the panel the way _specs.py describes reading `rid`."""
    sp = importlib.util.spec_from_file_location("bagchi2025_specs", os.path.join(os.path.dirname(__file__), "_specs.py"))
    S = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(S)
    s = S.SPECS[rid]
    if s.get("flip"):  # a y axis on the right: read the mirrored panel, give columns back unmirrored
        W = image.shape[1]
        s2 = dict(s)
        s2["flip"] = False
        S.SPECS[rid] = s2
        out = _run(S, rid, np.ascontiguousarray(image[:, ::-1]), at)
        for d in out:
            if "px" in d:
                d["px"][0] = W - d["px"][0]
        return out
    out = _run(S, rid, image, at)
    if s.get("x_order"):  # categories: x is the position of the mark from the left, 1, 2, ...
        out = sorted(out, key=lambda d: d["px"][0])
        for i, d in enumerate(out):
            d["x"] = i + 1
            d["note"] = "category " + str(i + 1) + " from the left; " + d["note"].split("; x read as")[0]
    return out


def _run(S, rid, image, at):
    s = S.SPECS[rid]
    if s["kind"] == "stack":
        sp = importlib.util.spec_from_file_location("bagchi2025_stack", os.path.join(os.path.dirname(__file__), "_stack.py"))
        ST = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(ST)
        return ST.read_stack(image, s["yl"], s["bar"], s.get("tick_len", 10))
    if s["kind"] == "own":
        sp = importlib.util.spec_from_file_location("bagchi2025_" + s["module"],
                                                    os.path.join(os.path.dirname(__file__), s["module"] + ".py"))
        OW = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(OW)
        return getattr(OW, s["func"])(image, at, **s.get("args", {}))
    if "xstep" in s:
        cal = calibrate_fit(image, s["xstep"], s["ystep"], s["xc"], s["yc"], s.get("tick_len", 0.006),
                            s.get("dark", 140), s.get("frame", False), s.get("top_ticks", False),
                            s.get("x_first"), s.get("min_ticks", 2))
    else:
        cal = calibrate(image, s["xl"], s["yl"], x_corner=s.get("xc"), y_corner=s.get("yc"),
                    tick_len=s.get("tick_len", 0.006), out_x=s.get("out_x", False), out_y=s.get("out_y", False),
                    skip_x=s.get("skip_x", 0), skip_y=s.get("skip_y", 0), own=s.get("own", False))
    mask = hue_mask(image, *s["hue"], smin=s.get("smin", 45), vmin=s.get("vmin", 0), vmax=s.get("vmax", 255))
    kind = s["kind"]
    ex = s.get("exclude", [])
    if kind == "rings":
        return read_rings(image, cal, mask, *s.get("r", (30, 70)), exclude=ex)
    if kind == "blobs":
        return read_blobs(image, cal, mask, s.get("min_area", 200), s.get("open", 3), exclude=ex,
                          max_area=s.get("max_area"), fill=s.get("fill", False), wide=s.get("wide", False))
    if kind == "curve":
        return read_curve(image, at, cal, inside(mask, cal, ex), s["seed"])
    if kind == "hist_edges":
        return histogram_edges(image, cal, inside(mask, cal, ex), s.get("dark", 185))
    if kind == "hist":
        return histogram(image, cal, inside(mask, cal, ex), min_width=s.get("min_width", 6),
                         merge_px=s.get("merge_px", 0))
    if kind == "bars":
        m = inside(mask, cal, ex)
        return [bar_value(cal, c0, c1, *top_edge(m, c0, c1), "bar") for c0, c1 in bar_spans(m, cal)]
    if kind == "stacked":
        # every colour of the stack: the top of each, in each bar's column span (found from all colours)
        masks = [inside(hue_mask(image, *h, smin=s.get("smin", 45)), cal, ex) for h in s["hues"]]
        allm = np.logical_or.reduce(masks)
        out = []
        m, name = masks[s["which"]], s["names"][s["which"]]
        base = int(cal["bottom"]) - 6
        for c0, c1 in bar_spans(allm, cal):
            w = c1 - c0 + 1
            tops = []
            for c in range(c0 + int(0.2 * w), c1 - int(0.2 * w) + 1):  # the stack standing on the axis
                r, miss, last = base, 0, None
                while r >= 0 and miss <= 8:
                    if allm[r, c]:
                        miss = 0
                        if m[r, c]:
                            last = r
                    else:
                        miss += 1
                    r -= 1
                if last is not None:
                    tops.append(last)
            t, spread = (float(np.median(tops)), float(np.std(tops))) if tops else (None, 0.0)
            if t is not None:
                out.append(bar_value(cal, c0, c1, t, spread, f"top of the {name} segment"))
        return out
    raise ValueError(kind)


def histogram_edges(image, cal, mask, dark=185):
    """A histogram whose bins are outlined in dark ink: the bin edges are the dark
    vertical lines standing on the x axis (dark over most of the 30 rows above it);
    each bin lies between two neighbouring edges, and its value is the top of its
    colour (median first row over the middle 60% of the bin), half an outline above it
    taken into the interval."""
    _, sat, val = P.hue(image)
    nd = (sat < 40) & (val < dark)
    base = int(cal["bottom"]) - 3
    col = nd[base - 30:base, :].sum(axis=0) >= 24
    col[:int(cal["left"]) + 3] = False
    edges, cur = [(float(cal["left"]) - 3.0, 6)], []  # the y axis bounds the first bin
    for c in list(np.nonzero(col)[0]) + [None]:
        if cur and (c is None or c > cur[-1] + 2):
            edges.append(((cur[0] + cur[-1]) / 2.0 + 0.5, len(cur)))
            cur = []
        if c is not None:
            cur.append(c)
    out = []
    for (e0, w0), (e1, w1) in zip(edges, edges[1:]):
        if e1 - e0 < 10:
            continue
        c0, c1 = int(e0 + w0 / 2 + 1), int(e1 - w1 / 2 - 1)
        foot = np.nonzero(mask[base - 5:base, c0:c1 + 1].any(axis=0))[0]
        if len(foot) == 0:
            continue  # an empty stretch, not a bin
        # the bin is where its colour stands on the axis (an empty stretch beside a low bar whose
        # edge is too short to be found is left out)
        c0, c1 = c0 + int(foot[0]), c0 + int(foot[-1])
        e0, e1 = c0 - 1.0, c1 + 1.0
        w = c1 - c0 + 1
        tops = []
        for c in range(c0 + int(0.2 * w), c1 - int(0.2 * w) + 1):  # the run of colour standing on the axis
            r, miss, last = base - 1, 0, None
            while r >= 0 and miss <= 3:
                if mask[r, c]:
                    last, miss = r, 0
                else:
                    miss += 1
                r -= 1
            if last is not None:
                tops.append(last)
        if not tops:
            continue
        top, spread = float(np.median(tops)), float(np.std(tops))
        outline = max(w0, w1) / 2.0
        d = bar_value(cal, c0, c1, top - outline / 2.0, spread + outline / 4.0, "histogram bin between dark edges")
        d["x"] = float(val_x(cal, (e0 + e1) / 2.0))
        out.append(d)
    return out


def histogram(image, cal, mask, edge_mask=None, min_width=6, step_px=3, merge_px=0):
    """Bars of one colour that touch each other (a histogram): split where the top
    edge steps or where a dark bin edge stands between them."""
    base = int(cal["bottom"]) - 4
    m = inside(mask, cal, margin=2)
    W = m.shape[1]
    tops = np.full(W, np.nan)
    for c in range(int(cal["left"]) + 2, W):
        rows = np.nonzero(m[:base, c])[0]
        if len(rows) and m[base - 3:base, c].all():
            tops[c] = rows[0]
    segs, c = [], 0
    while c < W:
        if np.isnan(tops[c]):
            c += 1
            continue
        s = c
        while c + 1 < W and not np.isnan(tops[c + 1]) and abs(tops[c + 1] - tops[c]) <= step_px:
            c += 1
        if c - s + 1 >= min_width:
            segs.append((s, c))
        c += 1
    merged = []
    for s, c in segs:  # a stray line inside a bin splits it: join pieces of equal height a few px apart
        if merged and merge_px and s - merged[-1][1] <= 20 and \
                abs(np.median(tops[s:c + 1]) - np.median(tops[merged[-1][0]:merged[-1][1] + 1])) <= merge_px:
            merged[-1] = (merged[-1][0], c)
        else:
            merged.append((s, c))
    out = []
    for s, c in merged:
        seg = tops[s + (c - s) // 5:c - (c - s) // 5 + 1]
        seg = seg[~np.isnan(seg)]
        out.append(bar_value(cal, s, c, float(np.median(seg)), float(np.std(seg)), "histogram bin"))
    return out
