"""Shared reading code for the figures of gong2018 (MATLAB-style plots).

Each reading file in this directory is a stub naming one panel, one series and
the printed axis labels it matched, and calling `read_spec` here.  The stubs pin
this file by its SHA-256, so a change here forces each stub to be re-checked.

Everything is found in the image:
  axes     boxgraph.digitize.find_axes finds the plot box (the black spines) and
           the major tick marks; the ticks are matched, in order, to the printed
           labels given in the stub (the only values typed in from the paper).
           A linear (or log10) fit of pixel against value gives the calibration
           and its misfit.
  markers  pixels of the series colour (within a tolerance) inside the plot box,
           split into connected blobs; a blob whose bounding box has the size of
           a marker (between `min_px` and `max_px` on its longer side) is one
           data point, at the centre of its bounding box.  Blobs of the series'
           line or of a dotted line are smaller and are dropped; blobs touching
           the box edge are dropped (cut markers).  Two markers that touch are
           split by their expected size along x.

Intervals (95%): the panels are raster images upsampled into the PDF, so a
marker centre is known to about one source pixel (`src_px`, in rendered
pixels), plus the calibration misfit (at least half a pixel), plus half a pixel
of quantisation, all in pixels and turned into values through the calibration.
"""
import math

import numpy as np
from scipy import ndimage as ndi

from boxgraph import digitize as dg


def _dark(img):
    f = img.astype(float)
    return (f.mean(axis=2) < 110) & ((f.max(axis=2) - f.min(axis=2)) < 70)


def _spines(d):
    """Plot box from the long dark lines: (c0, r0, c1, r1) as the inner edges,
    plus the spine thicknesses."""
    H, W = d.shape
    rowfrac = d.sum(axis=1) / W
    colfrac = d.sum(axis=0) / H
    rows = np.nonzero(rowfrac > 0.5)[0]
    cols = np.nonzero(colfrac > 0.5)[0]
    if len(rows) == 0 or len(cols) == 0:
        raise dg.CalibrationError("no spines found")

    def groups(idx):
        g, cur = [], [idx[0]]
        for i in idx[1:]:
            if i == cur[-1] + 1:
                cur.append(i)
            else:
                g.append(cur)
                cur = [i]
        g.append(cur)
        return g
    rg, cg = groups(rows), groups(cols)
    top, bot = rg[0], rg[-1]
    left, right = cg[0], cg[-1]
    return (left[-1] + 1, top[-1] + 1, right[0], bot[0]), (top, bot, left, right)


def _tick_positions(d, box, axis, length, sides="both"):
    """Inward tick marks mirrored on both spines (MATLAB style): positions along
    the axis where the band just inside both opposite spines is dark."""
    c0, r0, c1, r1 = box
    gap = 4
    if axis == "x":
        a = d[r1 - length:r1 - gap, c0:c1].mean(axis=0)
        b = d[r0 + gap:r0 + length, c0:c1].mean(axis=0)
        off = c0
    else:
        a = d[r0:r1, c0 + gap:c0 + length].mean(axis=1)
        b = d[r0:r1, c1 - length:c1 - gap].mean(axis=1)
        off = r0
    # "both": a tick must show on both spines (robust against curves touching
    # one spine); "either": one spine is enough (a marker hides the other)
    ok = (a > 0.45) & (b > 0.45) if sides == "both" else (a > 0.45) | (b > 0.45)
    hit = np.nonzero(ok)[0]
    out, cur = [], []
    for i in list(hit) + [None]:
        if cur and (i is None or i != cur[-1] + 1):
            if len(cur) <= 40:
                out.append(off + (cur[0] + cur[-1] + 1) / 2)
            cur = []
        if i is not None:
            cur.append(i)
    return out


def calibrate(img, spec):
    d = _dark(img)
    box, _ = _spines(d)
    L = spec.get("tick_px", 30)
    xs, ys = spec["x"], spec["y"]
    xt = _tick_positions(d, box, "x", L, spec["x"].get("sides", "both"))
    yt = _tick_positions(d, box, "y", L, spec["y"].get("sides", "both"))
    # ticks at the box corners are hidden in the perpendicular spine: add the
    # box edges when the labels say the axis starts or ends on a tick
    # ("start" is the low-pixel end: left for x, top for y)
    ex = spec["x"].get("edge_ticks", [])
    ey = spec["y"].get("edge_ticks", [])
    xt = xt + ([float(box[0])] if "start" in ex else []) + ([float(box[2])] if "end" in ex else [])
    yt = yt + ([float(box[1])] if "start" in ey else []) + ([float(box[3])] if "end" in ey else [])
    xt, yt = sorted(xt), sorted(yt)       # rows grow downward: top label first
    found = type("F", (), {"box": box})
    if len(xt) != len(xs["labels"]):
        raise dg.CalibrationError(f"found {len(xt)} x ticks {xt}, expected {len(xs['labels'])}")
    if len(yt) != len(ys["labels"]):
        raise dg.CalibrationError(f"found {len(yt)} y ticks {yt}, expected {len(ys['labels'])}")
    xa = dg.Axis(xs.get("scale", "linear"), list(zip(xt, xs["labels"])))
    ya = dg.Axis(ys.get("scale", "linear"), list(zip(yt, ys["labels"])))
    return xa, ya, found.box


def _mask(img, color, tol):
    f = img.astype(float)
    return np.sqrt(((f - np.asarray(color, float)) ** 2).sum(axis=2)) <= tol


def _rings(m, spec):
    """Centres of open-circle ("ring": [r_in, r_out]) or plus-sign ("plus":
    [half length, half width]) markers: the mean of the mask over the marker's
    shape, at every pixel; local maxima above `score`.  A dotted line or a
    connecting line fills only part of the shape and scores low."""
    from scipy.signal import fftconvolve
    if "ring" in spec:
        r_in, r_out = spec["ring"]
        R = int(math.ceil(r_out)) + 1
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        rr = np.hypot(yy, xx)
        k = ((rr >= r_in) & (rr <= r_out)).astype(float)
        size = int(r_out)
    elif "plus" in spec:
        a, w = spec["plus"]
        R = int(math.ceil(a))
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        k = (((np.abs(yy) <= w) & (np.abs(xx) <= a)) | ((np.abs(xx) <= w) & (np.abs(yy) <= a))).astype(float)
        size = int(a)
    elif "xcross" in spec:            # an "x": the plus turned by 45 degrees
        a, w = spec["xcross"]
        R = int(math.ceil(a))
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        u, v = (xx + yy) / math.sqrt(2), (xx - yy) / math.sqrt(2)
        k = (((np.abs(u) <= w) & (np.abs(v) <= a * math.sqrt(2))) |
             ((np.abs(v) <= w) & (np.abs(u) <= a * math.sqrt(2)))) & (np.abs(xx) <= a) & (np.abs(yy) <= a)
        k = k.astype(float)
        size = int(a)
    elif "square" in spec:            # open square: [outer half side, inner half side]
        a, b = spec["square"]
        R = int(math.ceil(a))
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
        m_out = (np.abs(xx) <= a) & (np.abs(yy) <= a)
        m_in = (np.abs(xx) < b) & (np.abs(yy) < b)
        k = (m_out & ~m_in).astype(float)
        size = int(a)
    else:                             # open downward triangle: [outer half width, edge width]
        a, w = spec["triangle"]
        R = int(math.ceil(a))
        yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(float)
        # top edge at -h/3, apex at 2h/3 below the centroid, h = sqrt(3) a
        h = math.sqrt(3) * a

        def inside(s):
            hs = math.sqrt(3) * s
            top = yy >= -hs / 3
            sides = np.abs(xx) <= s * (2 * hs / 3 - yy) / hs
            return top & sides
        k = (inside(a) & ~inside(max(a - 2 * w, 0.0))).astype(float)
        size = int(a * 1.2)
        del h
    k /= k.sum()
    score = fftconvolve(m.astype(float), k, mode="same")
    peak = (score == ndi.maximum_filter(score, size=size)) & (score >= spec["score"])
    lab, n = ndi.label(peak)
    cents = ndi.center_of_mass(peak, lab, range(1, n + 1))
    # a flat-topped score gives several maxima on one marker: merge those
    # closer than the marker's size, weighting by score
    pts = sorted(((c + 0.5, r + 0.5, score[int(r), int(c)]) for r, c in cents), key=lambda p: -p[2])
    merged = []
    for c, r, s in pts:
        for g in merged:
            if math.hypot(c - g[0] / g[2], r - g[1] / g[2]) < size:
                g[0] += c * s
                g[1] += r * s
                g[2] += s
                break
        else:
            merged.append([c * s, r * s, s])
    return [(g[0] / g[2], g[1] / g[2]) for g in merged]


def _series_mask(img, spec, box):
    m = _mask(img, spec["color"], spec["tol"])
    c0, r0, c1, r1 = box
    inset = 3
    keep = np.zeros_like(m)
    keep[int(r0) - spec.get("pad", 0):int(r1) + spec.get("pad", 0),
         int(c0) + inset:int(c1) + spec.get("pad", 0)] = True
    # boxes holding the panel's own labels in the series colour (legend text),
    # found by eye on the rendered crop and given in the stub
    for ea, eb, ec, ed in spec.get("exclude", []):
        keep[eb:ed, ea:ec] = False
    return m & keep


def markers(img, spec, xa, ya, box):
    m = _series_mask(img, spec, box)
    if any(s in spec for s in ("ring", "plus", "xcross", "square", "triangle")):
        return _finish(_rings(m, spec), spec, xa, ya)
    if "erode" in spec and "grid_from" in spec:
        # markers of one series that touch their neighbours: the x positions
        # are those of another series on the same grid (found in this image by
        # its own spec); at each, the eroded blob in a window of one marker
        # width is the marker, its bounding box grown back by the radius
        g = dict(spec["grid_from"])
        cols = [p[0] for p in _rings(_series_mask(img, g, box), g)]
        r = spec["erode"]
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        me = ndi.binary_erosion(m, structure=(np.hypot(yy, xx) <= r))
        half = spec["window_px"] // 2
        pts = []
        for col in sorted(cols):
            a = int(col) - half
            win = me[:, a:a + 2 * half]
            lab, n = ndi.label(win)
            if n == 0:
                continue
            sizes = ndi.sum(win, lab, range(1, n + 1))
            k = int(np.argmax(sizes)) + 1
            if sizes[k - 1] < spec["min_area"]:
                continue
            rows = np.nonzero((lab == k).any(axis=1))[0]
            pts.append((col, (rows.min() + rows.max() + 1) / 2))
        return _finish(pts, spec, xa, ya)
    if "erode" in spec:
        # thick filled-ish markers joined by thin lines: an erosion by a disk
        # wider than the lines but narrower than the marker's strokes leaves
        # one blob per marker; its bounding box is grown back by the radius
        r = spec["erode"]
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        m = ndi.binary_erosion(m, structure=(np.hypot(yy, xx) <= r))
        lab, n = ndi.label(m)
        pts = []
        for sl in ndi.find_objects(lab):
            h = sl[0].stop - sl[0].start + 2 * r
            w = sl[1].stop - sl[1].start + 2 * r
            if spec["min_px"] <= max(h, w) <= spec["max_px"]:
                pts.append(((sl[1].start + sl[1].stop) / 2, (sl[0].start + sl[0].stop) / 2))
        return _finish(pts, spec, xa, ya)
    lab, n = ndi.label(m)
    pts = []
    size = spec["marker_px"]
    for sl in ndi.find_objects(lab):
        h = sl[0].stop - sl[0].start
        w = sl[1].stop - sl[1].start
        if max(h, w) < spec["min_px"]:
            continue
        if h > spec["max_px"]:
            continue
        # touching markers: split the blob along x into ceil(w/size) pieces
        k = max(1, int(round(w / size)))
        for j in range(k):
            ca = sl[1].start + j * w / k
            cb = sl[1].start + (j + 1) * w / k
            sub = lab[sl[0], int(ca):int(math.ceil(cb))] > 0
            rows, cols = np.nonzero(sub)
            if len(rows) == 0:
                continue
            col = int(ca) + (cols.min() + cols.max() + 1) / 2
            row = sl[0].start + (rows.min() + rows.max() + 1) / 2
            pts.append((col, row))
    return _finish(pts, spec, xa, ya)


def _finish(pts, spec, xa, ya):
    pts = sorted(pts)
    out = []
    # center_px: how far the marker's plotted point may sit from the centre
    # found (a triangle's bounding-box centre vs its centroid: h/6)
    e = spec["src_px"] + 0.5 + spec.get("center_px", 0)
    for col, row in pts:
        ex = e + max(xa.residual_px, 0.5)
        ey = e + max(ya.residual_px, 0.5)
        x = xa.to_value(col)
        y = ya.to_value(row)
        a, b = ya.to_value(row + ey), ya.to_value(row - ey)
        out.append({"x": x, "y": y, "lo": min(a, b), "hi": max(a, b), "px": [col, row],
                    "px_lo": row - ey, "px_hi": row + ey,
                    "note": f"marker centre; x known to +/-{ex:.1f} px"})
    return out


def read_spec(image, at, spec):
    xa, ya, box = calibrate(image, spec)
    pts = markers(image, spec, xa, ya, box)
    if spec.get("x_min") is not None:
        pts = [p for p in pts if p["x"] >= spec["x_min"]]
    if spec.get("x_max") is not None:
        pts = [p for p in pts if p["x"] <= spec["x_max"]]
    return pts
