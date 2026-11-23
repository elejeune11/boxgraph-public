"""Shared marker-reading code for the symbol series of alonsomatilla2023 (MATLAB panels).

The axes are calibrated by `_fig.calibrate` (see its docstring). A series is its symbols:

  mask     pixels within `tol` of the series colour and nearer to it than to the stub's other
           colours, inside the plot box, outside blanked regions (the legend).
  symbols  connected groups of the mask after closing gaps of `join` px (anti-aliased rims,
           a line drawn across a symbol). Each group's fill fraction (mask pixels over its
           bounding box) tells filled symbols (> `fill_min`, default 0.3) from open ones (< `fill_max`, default 0.2);
           `kind` picks one. Groups much smaller than the median symbol are dropped (bits of
           other symbols' rims).
  value    the centre of the group's bounding box. MATLAB centres circles and diamonds on the
           data point; for triangles the bounding-box centre and the centroid differ by h/6,
           which is added to the interval (`triangle: True`).
  merged   a group more than `merge` (1.15) times the median symbol's height or width is two symbols
           drawn over each other; it is left out (figures.md lists them).

Intervals (95%): one pixel, the axis misfit, a quarter of the rim thickness, and h/6 for
triangles. x is read like y (the symbols are at integer positions, but the code does not
assume it).
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage

_FIG = Path(__file__).with_name("_fig.py")


def _fig():
    spec = importlib.util.spec_from_file_location("alonsomatilla2023_fig", _FIG)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def kind_is_filled(spec):
    return spec["kind"] == "filled"


def read_markers(image, spec):
    fg = _fig()
    f = image.shape[1] / float(spec.get("ref_width", image.shape[1]))
    spec = dict(fg.scaled(dict(spec, seed=(0, 0)), image.shape[1]),
                join=max(int(spec.get("join", 3) * f), 1), rim=spec.get("rim", 6) * f,
                min_px=int(spec.get("min_px", 30) * f * f))
    cal = fg.calibrate(image, spec)
    xa, ya = cal["x"], cal["y"]
    c0, r0, c1, r1 = [int(v) for v in cal["box"]]
    m = fg.colour_mask(image, spec["color"], spec.get("others", ()), spec.get("tol", 60))
    keep = np.zeros_like(m)
    pad = spec.get("inset", 4)
    keep[r0 + pad:r1 - pad + spec.get("below", 0), c0 + pad:c1 - pad + spec.get("right", 0)] = True
    for (a, b, c, d) in spec.get("blank", []):
        keep[b:d, a:c] = False
    m &= keep
    if spec.get("line_seed"):
        # a line of the same colour runs through the symbols: trace it from a seed point
        # (columns of the mask, the run nearest the previous one, _fig.trace) and remove
        # each column's run, widened by `line_pad` px; symbols it covers are then partial
        # and fail the size test below
        tr = fg.trace(m, c0 + pad, c1 - pad, (spec["line_seed"][0] * f, spec["line_seed"][1] * f),
                      3, 40 * f)
        lp = spec.get("line_pad", 3) * f
        lmax = spec.get("line_max", 60) * f            # a longer run is a symbol merged with the line
        good = sorted(c for c, (_, L) in tr.items() if L <= lmax)
        if good:
            cens = np.interp(sorted(tr), good, [tr[c][0] for c in good])
            for c, ce in zip(sorted(tr), cens):
                cen, L = tr[c]
                if L > lmax:
                    cen, L = ce, float(np.median([tr[g][1] for g in good]))
                m[max(int(cen - L / 2 - lp), 0):int(cen + L / 2 + lp) + 1, c] = False
    # filled symbols: the parts of the mask that survive an opening (thin rims, line edges
    # and anti-aliased fringes do not), grown back by r + 2 px within the mask (a disc of radius r
    # fits a triangle to within r of its tip); open symbols: the rest
    r = max(int(spec.get("solid", 6) * f), 1)
    solid = ndimage.binary_opening(m, iterations=r)
    filled_px = m & ndimage.binary_dilation(solid, iterations=r + 2)
    m = filled_px if spec["kind"] == "filled" else (m & ~filled_px)
    j = spec.get("join", 3)
    lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=j))
    lab = np.where(m, lab, 0)
    groups = []
    for k, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        sub = lab[sl] == k
        if sub.sum() < spec.get("min_px", 30):
            continue
        # specks of mixed colour where another symbol overlaps are dropped: keep the pieces of
        # at least 15% of the largest (a line across a symbol leaves two large pieces)
        pl, pn = ndimage.label(sub)
        if pn > 1:
            sizes = ndimage.sum(sub, pl, index=range(1, pn + 1))
            sub = np.isin(pl, 1 + np.where(sizes >= 0.15 * sizes.max())[0])
        rows, cols = np.where(sub)
        sl = (slice(sl[0].start + rows.min(), sl[0].start + rows.max() + 1),
              slice(sl[1].start + cols.min(), sl[1].start + cols.max() + 1))
        h, w = int(rows.max() - rows.min() + 1), int(cols.max() - cols.min() + 1)
        # fill: the share of the central 40% of the bounding box that is ink. Filled symbols
        # are ink there even when a line crosses them; open ones are empty inside.
        rc, cc = (sl[0].start + sl[0].stop) / 2.0, (sl[1].start + sl[1].stop) / 2.0
        ws = (slice(int(rc - 0.2 * h), int(rc + 0.2 * h) + 1), slice(int(cc - 0.2 * w), int(cc + 0.2 * w) + 1))
        win = m[ws]
        # pixels of other ink (a line drawn across the symbol) are left out of the share
        other = ~win & (image[ws].astype(float).sum(axis=2) < 600)
        seen = win.size - int(other.sum())
        groups.append({"sl": sl, "h": h, "w": w, "fill": float(win.sum()) / seen if seen > 0 else 0.0})
    if not groups:
        return []
    kind = spec["kind"]
    if kind == "filled":
        groups = [g for g in groups if g["fill"] > spec.get("fill_min", 0.3)]
    else:
        groups = [g for g in groups if g["fill"] < spec.get("fill_max", 0.2)]
    if not groups:
        return []
    if spec.get("aspect"):                     # square-ish symbols only (not bits of a line)
        groups = [g for g in groups if 1 / spec["aspect"] <= g["h"] / g["w"] <= spec["aspect"]]
    if not groups:
        return []
    # the symbol size: the median over groups at least 40% of the largest bounding box (pieces
    # of symbols cut by lines would otherwise pull it down)
    big = max(g["h"] * g["w"] for g in groups)
    full = [g for g in groups if g["h"] * g["w"] >= 0.4 * big]
    H = float(np.median([g["h"] for g in full]))
    W = float(np.median([g["w"] for g in full]))
    groups = [g for g in groups if g["h"] > 0.6 * H and g["w"] > 0.6 * W]
    rim = spec.get("rim", 6)
    out = []
    for g in sorted(groups, key=lambda g: g["sl"][1].start):
        rs, cs = g["sl"]
        col = (cs.start + cs.stop) / 2.0
        row = (rs.start + rs.stop) / 2.0
        x = fg.to_val(xa, col)
        if g["h"] > spec.get("merge", 1.15) * H or g["w"] > spec.get("merge", 1.15) * W:
            continue                                     # left out; figures.md says where
        # a symbol shorter (taller) than the median is partly hidden (or has a bit of a line or
        # another symbol attached): its centre may be off by half the difference
        half = (1.0 + ya["misfit"] + 0.25 * rim + (g["h"] / 6.0 if spec.get("triangle") else 0.0)
                + 0.5 * abs(H - g["h"]))
        y = fg.to_val(ya, row)
        a1, a2 = fg.to_val(ya, row - half), fg.to_val(ya, row + half)
        out.append({"x": x, "y": y, "lo": min(a1, a2), "hi": max(a1, a2), "px": [col, row],
                    "px_lo": row - half, "px_hi": row + half,
                    "note": f"{kind} symbol {g['w']}x{g['h']} px, fill {g['fill']:.2f}; "
                            f"x misfit {xa['misfit']:.1f} px, y misfit {ya['misfit']:.1f} px"})
    return out
