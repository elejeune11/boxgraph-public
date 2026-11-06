"""Axis calibration for the figures of gong2018 read in the second pass.

Like _common.calibrate (which stays as it is for the first-pass readings), but the
spine whose tick marks are used is chosen per axis, so a curve or a marker
crossing the other spine does not hide or add a tick:

  spec["x"]["band"]  "bottom" or "top": the spine along which x ticks are sought
  spec["y"]["band"]  "left" or "right"
  spec[...]["out"]   true when the ticks point outward (Excel-style plots) rather
                     than inward (MATLAB)
  spec[...]["edge_ticks"]  ["start", "end"]: a label at a box corner, whose tick is
                     hidden in the perpendicular spine, sits on that spine
  spec["box"]        "spines" (closed box, the default) or "axes" (only the left
                     and bottom axis lines are drawn)

Ticks are matched in order to the printed labels in the stub (the only values typed
in from the paper); a linear or log10 fit gives the calibration and its misfit.
"""
import numpy as np

from boxgraph import digitize as dg


def dark(img, level=110):
    f = img.astype(float)
    return (f.mean(axis=2) < level) & ((f.max(axis=2) - f.min(axis=2)) < 70)


def _groups(idx):
    if len(idx) == 0:
        return []
    g, cur = [], [idx[0]]
    for i in idx[1:]:
        if i == cur[-1] + 1:
            cur.append(i)
        else:
            g.append(cur)
            cur = [i]
    g.append(cur)
    return g


def find_box(d, frac=0.5):
    """(c0, r0, c1, r1) inner edges of the plot box from long dark lines; for an
    open plot (axes only) the top and right are the ends of the axis lines."""
    H, W = d.shape
    rows = np.nonzero(d.sum(axis=1) / W > frac)[0]
    cols = np.nonzero(d.sum(axis=0) / H > frac)[0]
    rg, cg = _groups(rows), _groups(cols)
    if not rg or not cg:
        raise dg.CalibrationError("no axis lines found")
    return rg, cg


def _ticks(band, off, min_frac=0.45, max_len=40):
    hit = np.nonzero(band > min_frac)[0]
    return [off + (g[0] + g[-1] + 1) / 2 for g in _groups(list(hit)) if len(g) <= max_len]


def calibrate(img, spec):
    d = dark(img, spec.get("dark", 110))
    # `min_col`: columns left of it hold the rotated axis title, not a spine
    d[:, :spec.get("min_col", 0)] = False
    rg, cg = find_box(d, spec.get("line_frac", 0.5))
    L = spec.get("tick_px", 16)
    gap = spec.get("gap", 4)
    if spec.get("box", "spines") == "spines":
        top, bot, left, right = rg[0], rg[-1], cg[0], cg[-1]
        c0, r0, c1, r1 = left[-1] + 1, top[-1] + 1, right[0], bot[0]
        if spec.get("bottom_from_left"):
            # the bottom spine is drawn over by a curve lying on it: the box's bottom is
            # where the left spine ends
            colline = d[:, left[0]:left[-1] + 1].all(axis=1)
            r1 = int(np.nonzero(colline)[0].max()) + 1 - spec.get("spine_px", 0)
            bot = [r1]
    else:
        bot, left = rg[-1], cg[0]
        c0, r1 = left[-1] + 1, bot[0]
        # the axis lines' extent
        line = d[bot[0]:bot[-1] + 1].any(axis=0)
        c1 = int(np.nonzero(line)[0].max()) + 1
        colline = d[:, left[0]:left[-1] + 1].any(axis=1)
        r0 = int(np.nonzero(colline)[0].min())
        top, right = [r0 - 1], [c1]
    xs, ys = spec["x"], spec["y"]
    xb = xs.get("band", "bottom")
    yb = ys.get("band", "left")
    if xs.get("out"):
        band = d[bot[-1] + 1 + gap // 2:bot[-1] + 1 + L, c0:c1] if xb == "bottom" else d[top[0] - L:top[0] - gap // 2, c0:c1]
    else:
        band = d[r1 - L:r1 - gap, c0:c1] if xb == "bottom" else d[r0 + gap:r0 + L, c0:c1]
    xt = _ticks(band.mean(axis=0), c0, xs.get("min_frac", 0.45))
    if ys.get("out"):
        band = d[r0:r1, left[0] - L:left[0] - gap // 2] if yb == "left" else d[r0:r1, right[-1] + 1 + gap // 2:right[-1] + 1 + L]
    else:
        band = d[r0:r1, c0 + gap:c0 + L] if yb == "left" else d[r0:r1, c1 - L:c1 - gap]
    yt = _ticks(band.mean(axis=1), r0, ys.get("min_frac", 0.45))
    # a mark within a few px of a box end is the perpendicular spine's own edge, not
    # a tick (a corner label is given by edge_ticks)
    end = spec.get("corner_px", 8)
    xt = [t for t in xt if c0 + end < t < c1 - end]
    yt = [t for t in yt if r0 + end < t < r1 - end]
    # `regular`: a marker touching the spine also looks like a tick; keep the largest
    # evenly spaced set of marks (the labelled ticks are evenly spaced)
    if xs.get("regular"):
        xt = dg.regular_ticks(xt)
    if ys.get("regular"):
        yt = dg.regular_ticks(yt)
    ex, ey = xs.get("edge_ticks", []), ys.get("edge_ticks", [])
    xt = sorted(xt + ([float(c0)] if "start" in ex else []) + ([float(c1)] if "end" in ex else []))
    yt = sorted(yt + ([float(r0)] if "start" in ey else []) + ([float(r1)] if "end" in ey else []))
    # `anchored`: both ends of the axis carry labels (edge_ticks start and end) and the
    # labels are evenly spaced, but some interior ticks are hidden under the data:
    # keep the marks within `anchor_tol` px of an expected position, with its label
    for ax, (ts, lo, hi) in (("x", (xt, c0, c1)), ("y", (yt, r0, r1))):
        a = spec[ax]
        if not a.get("anchored"):
            continue
        n = len(a["labels"]) - 1
        exp = [lo + k * (hi - lo) / n for k in range(n + 1)]
        tol = a.get("anchor_tol", 8)
        pairs = []
        for k, e in enumerate(exp):
            near = [t for t in ts if abs(t - e) <= tol]
            if near:
                pairs.append((min(near, key=lambda t: abs(t - e)), a["labels"][k]))
        axis = dg.Axis(a.get("scale", "linear"), pairs)
        if ax == "x":
            xa_anch = axis
        else:
            ya_anch = axis
    if xs.get("anchored") or ys.get("anchored"):
        xa = xa_anch if xs.get("anchored") else dg.Axis(xs.get("scale", "linear"), list(zip(xt, xs["labels"])))
        ya = ya_anch if ys.get("anchored") else dg.Axis(ys.get("scale", "linear"), list(zip(yt, ys["labels"])))
        return xa, ya, (c0, r0, c1, r1)
    if len(xt) != len(xs["labels"]):
        raise dg.CalibrationError(f"found {len(xt)} x ticks {xt}, expected {len(xs['labels'])}")
    if len(yt) != len(ys["labels"]):
        raise dg.CalibrationError(f"found {len(yt)} y ticks {yt}, expected {len(ys['labels'])}")
    xa = dg.Axis(xs.get("scale", "linear"), list(zip(xt, xs["labels"])))
    ya = dg.Axis(ys.get("scale", "linear"), list(zip(yt, ys["labels"])))
    return xa, ya, (c0, r0, c1, r1)
