"""Filled round markers of one colour on a framed plot, with both axes calibrated from ticks.

Calibration from the image: the frame (the four longest dark lines); the tick marks
pointing in from the bottom edge (x) and the left edge (y); long ticks carry the
printed labels, short ticks lie halfway (see _lib.grid_axis). The caller gives the
labels it matched: the values at the frame edges and the label step.
Markers: the colour mask is opened with a disk a little narrower than a marker, which
removes tick marks, lines and text strokes. The marker radius R is the median radius of
the isolated blobs. Eroding the mask with a disk of radius R - margin leaves one small
core per marker, also for markers that overlap, as long as their centres are more than
about 2*margin apart; each core's centroid is a marker centre. A blob whose area is
clearly larger than its cores account for holds markers too close to separate; it is
reported with its extra count in the note (and the centre of that blob).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

_spec = importlib.util.spec_from_file_location("gardel_lib", Path(__file__).with_name("_lib.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)


def disk(r):
    r = int(round(r))
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def both_edges(main, other, tol=12.0):
    """Ticks of one axis from its labelled edge (`main`) and the opposite edge (`other`). A marker
    touching a tick lengthens it, so where a tick is found on both edges its length is the shorter
    of the two (the position is the main edge's). Opposite edges without ticks change nothing."""
    out = []
    for c, ln in main:
        near = [l2 for c2, l2 in other if abs(c2 - c) < tol]
        if len(other) >= 3 and not near:
            continue        # a line or marker meeting the edge, not a tick (ticks are mirrored)
        out.append((c, min([ln] + near)))
    # a line running along the axis from the edge (a dashed threshold line) is far longer than
    # any tick: drop strokes longer than 1.5 times the median of the longer half
    if len(out) >= 3:
        lens = sorted(ln for _, ln in out)
        ref = float(np.median(lens[len(lens) // 2:]))
        out = [(c, ln) for c, ln in out if ln <= 1.5 * ref]
    return out


def calibrate(img, xv, xstep, yv, ystep, depth=400, region=None, x_first_major=None, y_first_major=None,
              tick_level=120):
    """xv = (value at left edge, value at right edge), yv = (value at bottom edge, value at top edge).
    x_first_major / y_first_major: the label under the leftmost / topmost long tick, when given."""
    fr = L.frame(img, region=region)
    tx = both_edges(
        L.ticks(img, fr["bottom"], (fr["left"] + 15, fr["right"] - 15), "x", -1, depth, lw=fr["lw_row"],
                level=tick_level),
        L.ticks(img, fr["top"], (fr["left"] + 15, fr["right"] - 15), "x", 1, depth, lw=fr["lw_row"],
                level=tick_level))
    ty = both_edges(
        L.ticks(img, fr["left"], (fr["top"] + 15, fr["bottom"] - 15), "y", 1, depth, lw=fr["lw_col"],
                level=tick_level),
        L.ticks(img, fr["right"], (fr["top"] + 15, fr["bottom"] - 15), "y", -1, depth, lw=fr["lw_col"],
                level=tick_level))
    ax, bx, mx, dx = L.grid_axis(tx, fr["left"], fr["right"], xv[0], xv[1], xstep, first_major=x_first_major)
    ay, by, my, dy = L.grid_axis(ty, fr["bottom"], fr["top"], yv[0], yv[1], ystep, first_major=y_first_major)
    return {"fr": fr, "ax": ax, "bx": bx, "mx": mx, "dx": dx, "ay": ay, "by": by, "my": my, "dy": dy}


def inner_radius(area, shape):
    """Radius of the largest disk (or half-side of the largest square) inside a marker of this area."""
    if shape in ("square", "diamond"):
        return np.sqrt(area) / 2.0
    if shape == "triangle":
        return np.sqrt(area / (3.0 * np.sqrt(3.0)))
    return np.sqrt(area / np.pi)


def find_markers(mask, fr, open_r, margin=4, inset=6, shape="disk", min_fill=0.65, single_from="large"):
    m = mask.copy()
    m[:int(fr["top"]) + inset] = False
    m[int(fr["bottom"]) - inset:] = False
    m[:, :int(fr["left"]) + inset] = False
    m[:, int(fr["right"]) - inset:] = False
    m = ndi.binary_opening(m, structure=disk(open_r))
    lab, n = ndi.label(m)
    areas = ndi.sum(m, lab, range(1, n + 1))
    if shape == "disk":
        single = float(np.median(areas))
    elif shape == "ellipse":    # touching pairs are common: a single marker is a smaller blob
        single = float(np.percentile(areas, 30))
    else:   # chained markers make most blobs large: the single marker is the typical small blob
        single = float(np.median([a for a in areas if a <= 1.5 * np.min(areas)]))
    R = inner_radius(single, shape)
    if shape == "blob":
        # markers that do not touch each other (oval dots): each opened blob of about a marker's
        # size and filling most of its bounding box (an ellipse fills 79%) is one marker; smaller
        # or sparser blobs are text, arrow heads or pieces of dashed lines
        if single_from == "median":
            single = float(np.median(areas))
        else:
            single = float(np.median([a for a in areas if a >= 0.3 * np.max(areas)]))
        R = inner_radius(single, "disk")
        out = []
        for i, sl in enumerate(ndi.find_objects(lab), start=1):
            box = (sl[0].stop - sl[0].start) * (sl[1].stop - sl[1].start)
            if not (0.6 * single <= areas[i - 1] <= 1.6 * single) or areas[i - 1] / box < min_fill:
                continue
            r, c = ndi.center_of_mass(m, lab, i)
            out.append({"r": float(r), "c": float(c), "R": R, "blob_markers": 1, "split": False,
                        "blob_area_ratio": float(areas[i - 1] / single)})
        return out, R, single
    if shape == "ellipse":
        # oval markers: their half-width and half-height from the blobs of one marker's area
        ones = [sl for i, sl in enumerate(ndi.find_objects(lab)) if 0.7 * single <= areas[i] <= 1.3 * single]
        a = float(np.median([(sl[1].stop - sl[1].start) / 2.0 for sl in ones]))
        b = float(np.median([(sl[0].stop - sl[0].start) / 2.0 for sl in ones]))
        R = b
        ia, ib = max(1, int(a - margin)), max(1, int(b - margin))
        yy, xx = np.mgrid[-ib:ib + 1, -ia:ia + 1]
        se = (xx / ia) ** 2 + (yy / ib) ** 2 <= 1
    elif shape == "square":
        se = np.ones((2 * int(R - margin) + 1,) * 2, bool)
    else:
        se = disk(R - margin)
    core = ndi.binary_erosion(m, structure=se)
    clab, cn = ndi.label(core)
    cores = []
    for k, sl in enumerate(ndi.find_objects(clab), start=1):
        rr, cc = np.nonzero(clab[sl] == k)
        rr = rr + sl[0].start
        cc = cc + sl[1].start
        r0, c0 = rr.mean(), cc.mean()
        # a core much longer than wide holds two markers too close to give two cores: their
        # centres lie `margin` inside the two ends of the core, along its long axis
        cov = np.cov(np.vstack([rr - r0, cc - c0])) if len(rr) > 2 else np.eye(2)
        w, v = np.linalg.eigh(cov)
        ax = v[:, 1]
        t = (rr - r0) * ax[0] + (cc - c0) * ax[1]
        length = t.max() - t.min()
        if length > 2 * margin + 8:
            for e in (t.min() + margin, t.max() - margin):
                cores.append((r0 + e * ax[0], c0 + e * ax[1], True))
        else:
            cores.append((r0, c0, False))
    # cores closer than half a marker radius are one marker broken by edge noise: merge them
    merged = []
    for r, c, s in sorted(cores):
        for k, (r2, c2, s2, nk) in enumerate(merged):
            if np.hypot(r - r2, c - c2) < 0.5 * R:
                merged[k] = ((r2 * nk + r) / (nk + 1), (c2 * nk + c) / (nk + 1), s2 or s, nk + 1)
                break
        else:
            merged.append((r, c, s, 1))
    cores = [(r, c, s) for r, c, s, _ in merged]
    parent = [lab[int(round(r)), int(round(c))] for r, c, _ in cores]
    out = []
    for i in range(1, n + 1):
        mine = [cores[k] for k in range(len(cores)) if parent[k] == i]
        expect = areas[i - 1] / single
        for r, c, split in mine:
            out.append({"r": float(r), "c": float(c), "R": R, "blob_markers": len(mine), "split": split,
                        "blob_area_ratio": float(expect)})
    return out, R, single


def read_markers(img, mask, xv, xstep, yv, ystep, open_r=None, margin=4, region=None, what="marker",
                 x_first_major=None, y_first_major=None, shape="disk", tick_level=120, exclude=None,
                 min_fill=0.65, single_from="large"):
    cal = calibrate(img, xv, xstep, yv, ystep, region=region, x_first_major=x_first_major,
                    y_first_major=y_first_major, tick_level=tick_level)
    if open_r is None:
        open_r = 10
    mk, R, single = find_markers(mask, cal["fr"], open_r, margin, shape=shape, min_fill=min_fill,
                                 single_from=single_from)
    if exclude is not None:
        mk = [p for p in mk if not exclude(img, p)]
    out = []
    for p in sorted(mk, key=lambda d: (d["c"], d["r"])):
        x = (p["c"] - cal["ax"]) / cal["bx"]
        y = (p["r"] - cal["ay"]) / cal["by"]
        # centre precision: 1.5 px for an isolated round marker; for markers that overlap,
        # the erosion core is pulled toward the overlap by up to `margin` px
        pr = 1.5 + (margin if p["blob_markers"] > 1 else 0.0) + (R / 2 if p["split"] else 0.0)
        ey = (pr + cal["my"]) / abs(cal["by"])
        ex = (pr + cal["mx"]) / abs(cal["bx"])
        note = f"{what} centre (R = {R:.1f} px), x +-{ex:.3g}"
        if not out:
            note += f"; x axis {cal['dx']}; y axis {cal['dy']}"
        if p["split"]:
            note += ("; one end of an elongated overlap of markers whose centres are too close for two cores "
                     "(more markers may hide between the ends)")
        elif p["blob_markers"] > 1:
            note += f"; one of {p['blob_markers']} overlapping markers (blob area {p['blob_area_ratio']:.2f} markers)"
        elif p["blob_area_ratio"] > 1.35:
            note += f"; WARNING blob area {p['blob_area_ratio']:.2f} markers but one core: hidden marker possible"
        out.append({"x": float(x), "y": float(y), "lo": float(y - ey), "hi": float(y + ey), "px": [p["c"], p["r"]],
                    "note": note})
    return out
