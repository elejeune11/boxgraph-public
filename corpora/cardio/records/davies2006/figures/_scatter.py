"""Shared reading code for the scatter plots of davies2006 (Fig. 6 and Fig. 7, PDF p. 8).

Both panels are low-resolution raster images embedded in the PDF (spreadsheet charts): rendered at
1200 dpi, each image pixel is a block of about 8 x 8 page pixels (`blk`, measured on the image as the
width of the axis line). Everything below comes from the image; the only numbers typed in are the
printed tick labels.

Calibration
  axes      grey ink (< 235). The y axis is the column with the most grey ink in the left half; the
            x axis is the row with the most grey ink in the lower half (both span the whole plot).
  y ticks   short grey runs standing to the left of the y axis (rows whose 4 image pixels left of the
            axis are inked), grouped; matched bottom to top to the printed labels; straight-line
            fit, largest misfit reported.
  x ticks   short grey runs below the x axis, matched left to right to the printed labels.
Points
  black ink (< 110) inside the plot box, opened with a disk of a third of the point diameter so
  that the regression line and the r and p text (strokes one or two image pixels wide) go and the
  round markers stay. Each remaining blob is one marker or several fused ones: the number is the
  blob's area over the median blob area, rounded, or two when a blob of one marker's area is
  longer than 1.15 marker diameters along its long axis (two markers almost on top of each other).
  The length is measured with a band around the regression line blanked (the line is fitted to the
  long thin ink left once the markers are removed), so a stub of the line does not lengthen a lone
  marker: lone markers measure 0.92-1.03 diameters, the near-coincident pairs 1.23 and more.
  A fused blob is split by k-means on its pixels (deterministic start along its long axis).
Intervals (95%)
  a lone marker: its centroid +- (one image pixel + the calibration misfit) in each direction; a
  marker split from a fused blob: +- (a quarter of the marker diameter + the misfit), since the
  split is not exact where the markers overlap.
"""

import numpy as np
from scipy import ndimage
from scipy.cluster.vq import kmeans2


def _groups(idx):
    out, cur = [], []
    for i in idx:
        if cur and i != cur[-1] + 1:
            out.append(cur)
            cur = []
        cur.append(int(i))
    if cur:
        out.append(cur)
    return out


def _fit(pos, labels, what):
    """Ticks matched in order to the labels; one label may have no tick found (if at least four
    others do): the label left out is the one giving the smallest misfit."""
    sets = [list(labels)]
    if len(pos) == len(labels) - 1 and len(pos) >= 4:
        sets = [list(labels[:i]) + list(labels[i + 1:]) for i in range(len(labels))]
    if len(pos) != len(sets[0]):
        raise ValueError(f"{what}: {len(pos)} ticks found for {len(labels)} labels: {pos}")
    best = None
    p = np.array(pos, float)
    for labs in sets:
        v = np.array(labs, float)
        b, a = np.polyfit(p, v, 1)
        mis = float(np.max(np.abs((v - a) / b - p)))
        if best is None or mis < best[2]:
            best = (a, b, mis)
    return best


def calibrate(g, ylabels, xlabels):
    H, W = g.shape
    grey = g < 235
    cs = grey[:, : W // 2].sum(0)
    ycols = np.flatnonzero(cs >= 0.9 * cs.max())
    yc = _groups(ycols)[0]
    rs = grey[H // 2:, :].sum(1)
    xrows = np.flatnonzero(rs >= 0.9 * rs.max()) + H // 2
    xr = _groups(xrows)[-1]
    blk = len(yc)
    c_ax, r_ax = (yc[0] + yc[-1]) / 2.0, (xr[0] + xr[-1]) / 2.0
    # y ticks: grey just left of the axis line
    # (some ticks are faint, 230-240 of 255: a strip counts as inked when its mean is below 243)
    left = g[:, yc[0] - 4 * blk: yc[0] - blk].mean(axis=1) < 243
    left[xr[-1] + 1:] = False
    ytk = [(gg[0] + gg[-1]) / 2.0 for gg in _groups(np.flatnonzero(left)) if len(gg) <= 3 * blk]
    ytk = sorted(ytk, reverse=True)  # bottom first
    ya, yb, ym = _fit(ytk, ylabels, "y axis")
    below = g[xr[-1] + blk: xr[-1] + 4 * blk, :].mean(axis=0) < 243
    below[: yc[0]] = False
    xtk = [(gg[0] + gg[-1]) / 2.0 for gg in _groups(np.flatnonzero(below)) if len(gg) <= 3 * blk]
    xtk = sorted(xtk)
    xa, xb, xm = _fit(xtk, xlabels, "x axis")
    return {"c_ax": c_ax, "r_ax": r_ax, "blk": blk, "x": (xa, xb, xm), "y": (ya, yb, ym),
            "yc": yc, "xr": xr}


def read_points(image, ylabels, xlabels):
    g = image[..., :3].astype(float).mean(axis=2)
    cal = calibrate(g, ylabels, xlabels)
    blk = cal["blk"]
    dark = g < 110
    box = np.zeros_like(dark)
    box[: cal["xr"][0] - blk, cal["yc"][-1] + blk:] = True
    dark &= box
    # marker size: the largest blobs after a small opening are markers; diameter from their area
    lab0, n0 = ndimage.label(ndimage.binary_opening(dark, structure=np.ones((3 * blk, 3 * blk))))
    a0 = ndimage.sum(np.ones_like(dark), lab0, index=np.arange(1, n0 + 1))
    d = 2.0 * np.sqrt(np.median(a0) / np.pi)
    r = max(int(d / 4.0), 2)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (xx * xx + yy * yy) <= r * r
    m = ndimage.binary_opening(dark, structure=disk)
    # the regression line: the long thin ink left after removing the markers, fitted by a straight
    # line; a band around it is blanked when counting the markers in a blob (not for the centres)
    resid = dark & ~ndimage.binary_dilation(m, iterations=blk)
    rl, rn = ndimage.label(resid, structure=np.ones((3, 3)))
    keep = np.zeros(rn + 1, bool)
    for k, s in enumerate(ndimage.find_objects(rl), start=1):
        if max(s[0].stop - s[0].start, s[1].stop - s[1].start) > 2 * d:
            keep[k] = True
    lr, lc = np.nonzero(keep[rl])
    band = np.zeros_like(dark)
    if len(lc) > 50:
        sl, ic = np.polyfit(lc, lr, 1)
        dist = np.abs(lr - (sl * lc + ic)) / np.hypot(1.0, sl)
        half = np.percentile(dist, 95) + blk
        rr_, cc_ = np.mgrid[0:dark.shape[0], 0:dark.shape[1]]
        band = np.abs(rr_ - (sl * cc_ + ic)) / np.hypot(1.0, sl) <= half
        band[:, : int(lc.min()) - blk] = False
        band[:, int(lc.max()) + blk:] = False
    lab, n = ndimage.label(m)
    areas = ndimage.sum(m, lab, index=np.arange(1, n + 1))
    single = float(np.median(areas))
    xa, xb, xm = cal["x"]
    ya, yb, ym = cal["y"]
    pts = []
    for k in range(1, n + 1):
        cnt = int(round(areas[k - 1] / single))
        if cnt < 1:
            continue
        rows, cols = np.nonzero(lab == k)
        P = np.column_stack([cols, rows]).astype(float)
        nb = ~band[rows, cols]
        Q = P[nb] if nb.sum() > 10 else P
        mu0 = Q.mean(axis=0)
        vt0 = np.linalg.svd(Q - mu0, full_matrices=False)[2]
        pr0 = (Q - mu0) @ vt0[0]
        ext = float(pr0.max() - pr0.min() + 1.0)
        if cnt == 1 and ext > 1.15 * d:
            # two markers almost on top of each other: same area as one, but longer than round
            cnt = 2
        if cnt == 1:
            cen = [P.mean(axis=0)]
            half = float(blk)
            note = "lone marker"
        else:
            mu = P.mean(axis=0)
            u, s, vt = np.linalg.svd(P - mu, full_matrices=False)
            ax = vt[0]
            proj = (P - mu) @ ax
            init = np.array([mu + ax * q for q in np.linspace(proj.min() * 0.6, proj.max() * 0.6, cnt)])
            cen, _ = kmeans2(P, init, minit="matrix")
            half = d / 4.0
            note = f"one of {cnt} fused markers, split by k-means"
        for c, rr in cen:
            hx = half + xm
            hy = half + ym
            x = xa + xb * c
            y = ya + yb * rr
            ylo, yhi = sorted([ya + yb * (rr + hy), ya + yb * (rr - hy)])
            pts.append({"x": float(x), "y": float(y), "lo": float(ylo), "hi": float(yhi),
                        "px": [float(c), float(rr)], "px_lo": float(rr - hy), "px_hi": float(rr + hy),
                        "note": f"{note}; blob length {ext / d:.2f} diameters; x +-{abs(xb) * hx:.3g} (axis units); marker {d:.0f} px; "
                                f"misfit x {xm:.1f} px, y {ym:.1f} px"})
    pts.sort(key=lambda p: (p["x"], p["y"]))
    return pts
