# Fig. 4(a) (p. 4) of jin2015: the bilayers simulated by finite elements, as blue markers in the
# (Hs/Hf, Gf/Gs) plane: open circles = subcritical creases, pluses = supercritical creases.
# Axes from _fig3.py (panel "4a"). The legend box (a dark rectangle inside the plot) is found and
# its sample markers are left out. Circles: ring correlation; pluses: the blue blobs left after
# the rings are erased, at their centroid. The value is G_f/G_s, indexed by H_s/H_f.
import importlib.util
import pathlib

import numpy as np

_s = importlib.util.spec_from_file_location("jin_fig3", pathlib.Path(__file__).resolve().parent / "_fig3.py")
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)
J = F.J


def _legend(image, box, half):
    """The legend rectangle: the dark lines inside the plot longer than 15% of its width/height."""
    m = J.dark(image, 130)
    c0, r0, c1, r1 = [int(round(v)) for v in box]
    h = int(half) + 30
    inner = m[r0 + h:r1 - h, c0 + h:c1 - h]
    W, H = inner.shape[1], inner.shape[0]
    rows = [r for r in range(H) if inner[r].sum() > 0.15 * W]
    groups = []
    for r in rows:  # the legend's top and bottom edges are the first two groups of long dark rows
        if groups and r - groups[-1][-1] <= 3:
            groups[-1].append(r)
        else:
            groups.append([r])
    if len(groups) < 2:
        return None
    top, bot = groups[0][0], groups[1][-1]
    band = inner[top:bot + 1]
    cols = [c for c in range(W) if band[:, c].mean() > 0.8]  # its sides: dark over the whole band
    if not cols:
        return None
    return (c0 + h + min(cols), r0 + h + top, c0 + h + max(cols), r0 + h + bot)


def read(image, at, kind):
    box, half, xax, yax = F.calibrate(image, "4a")
    c0, r0, c1, r1 = box
    blue = J.hue_mask(image, "blue")
    leg = _legend(image, box, half)
    region = (c0 + half + 2, r0 + half + 2, c1 + 40, r1 + 40)
    rings, R = J.ring_centres(blue, 14, 30, region, frac=0.45)
    pts = []
    if kind == "circles":
        pts = [(c, r) for c, r, _ in rings]
        what = f"ring radius {R} px"
    else:
        from scipy.ndimage import label
        m = blue.copy()
        yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]]
        for c, r, _ in rings:
            m[(xx - c) ** 2 + (yy - r) ** 2 <= (R + 8) ** 2] = False
        m[:int(r0 + half + 2), :] = False
        lab, n = label(m, structure=np.ones((3, 3)))
        for i in range(1, n + 1):
            ys, xs = np.nonzero(lab == i)
            hgt, wid = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
            if len(ys) < 60 or not (0.5 < hgt / wid < 2.0) or max(hgt, wid) > 4 * R:
                continue  # not a plus: text of the legend, specks
            # a plus: the crossing of its bars is the column and row with most pixels
            col = float((xs.min() + xs.max()) / 2.0)
            row = float((ys.min() + ys.max()) / 2.0)
            if all((col - c) ** 2 + (row - r) ** 2 > (2 * R) ** 2 for c, r in pts):
                pts.append((col, row))  # a plus cut by the frame line counts once
        what = "plus marker, centre of its bounding box"
    if leg is not None:
        lc0, lr0, lc1, lr1 = leg
        pts = [(c, r) for c, r in pts if not (lc0 - 5 <= c <= lc1 + 5 and lr0 - 5 <= r <= lr1 + 5)]
    out = []
    for c, r in sorted(pts):
        w = 3.0 + yax.misfit_px + 1.0
        lo, hi = yax.to_val(r + w), yax.to_val(r - w)
        out.append({"x": xax.to_val(c), "y": yax.to_val(r), "lo": min(lo, hi), "hi": max(lo, hi), "px": [c, r],
                    "px_lo": r - w, "px_hi": r + w,
                    "note": f"{what}; axes misfit x {xax.misfit_px:.1f}, y {yax.misfit_px:.1f} px"})
    return out
