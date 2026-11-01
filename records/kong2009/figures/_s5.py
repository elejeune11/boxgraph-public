"""Shared reading code for Fig. S5: open circles of four colours (black, red, green, blue), one
per measured lifetime, on an L-shaped pair of axes with outward ticks.

At short lifetimes the circles of a series pile up into clusters where single circles cannot be
told apart; only circles that stand clear of the other circles of their own colour are read.
A circle is found by matching a ring of the circles' radius against the colour's mask: at a centre,
most of the ring's visible pixels (inside the plot box) must be in the colour, and the inside of the
ring must be nearly empty of that colour (in a cluster, neighbouring rings cross it). A circle on
the x axis (ln 1 = 0) is cut by the axis and only its upper half is drawn.

A reading file supplies the printed tick labels it matched, the colour, a rough ring radius in
pixels and regions (legend, title) not searched."""

import numpy as np
from scipy import ndimage as ndi
from scipy.signal import fftconvolve

import _lt
import _s4


def colour_mask(img, colour):
    r, g, b = (img[..., i].astype(int) for i in range(3))
    if colour == "black":
        return np.maximum(np.maximum(r, g), b) < 100
    if colour == "red":
        return (r > 150) & (g < 110) & (b < 110)
    if colour == "green":
        return (g > 150) & (r < 130) & (b < 130)
    if colour == "blue":
        return (b > 150) & (r < 110) & (g < 110)
    raise ValueError(colour)


def _ring(r, w):
    k = int(np.ceil(r + w)) + 1
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
    d = np.hypot(yy, xx)
    return (np.abs(d - r) <= w / 2).astype(float), (d <= r - w).astype(float)


def read_rings(image, at, y_labels, x_labels, colour, r_px, exclude=(), min_score=0.8, max_inside=0.2):
    black = _lt.mask_for(image, "black")
    ycols, xrows = _lt.find_axes(black)
    ya = _lt.YAxis(_s4._y_ticks(black, ycols, xrows), [list(y_labels)])
    xc = _lt.x_ticks(black, ycols, xrows)
    if len(xc) != len(x_labels):
        raise ValueError(f"found {len(xc)} x ticks at columns {[round(c) for c in xc]}, expected {len(x_labels)}")
    xa = _lt.Linear(list(zip(sorted(xc), x_labels)))
    seg = ya.segs[0]
    H, W = black.shape
    plot = np.zeros((H, W), bool)
    plot[:xrows[0], ycols[1] + 1:] = True  # the plot box: right of the y axis, above the x axis
    for (fx0, fy0, fx1, fy1) in exclude:
        plot[int(fy0 * H):int(fy1 * H), int(fx0 * W):int(fx1 * W)] = False
    m = colour_mask(image, colour) & plot
    m = ndi.binary_dilation(m, iterations=1)  # close anti-aliasing gaps in the ring
    line = ycols[1] - ycols[0] + 1
    w = max(4.0, 0.8 * line)
    # the radius: the one that best matches the clearest ring
    best = None
    for r in np.arange(0.85 * r_px, 1.15 * r_px + 0.5, 1.0):
        ring, _ = _ring(r, w)
        s = fftconvolve(m.astype(float), ring, mode="same") / ring.sum()
        if best is None or s.max() > best[0]:
            best = (s.max(), r)
    r = best[1]
    ring, disk = _ring(r, w)
    present = fftconvolve(m.astype(float), ring, mode="same")
    visible = fftconvolve(plot.astype(float), ring, mode="same")
    inside = fftconvolve(m.astype(float), disk, mode="same") / disk.sum()
    score = np.where(visible > 0.45 * ring.sum(), present / np.maximum(visible, 1), 0)
    cand = (score >= min_score) & (inside <= max_inside)
    out = []
    taken = np.zeros_like(cand)
    order = np.argsort(-score[cand])
    rows, cols = np.nonzero(cand)
    per_y = abs(seg.b)
    per_x = abs(xa.b)
    for i in order:
        rr, cc = rows[i], cols[i]
        if taken[rr, cc]:
            continue
        y0, y1 = max(0, rr - int(r)), min(H, rr + int(r) + 1)
        x0, x1 = max(0, cc - int(r)), min(W, cc + int(r) + 1)
        taken[y0:y1, x0:x1] = True
        # sub-pixel centre: the score-weighted mean over a small window
        ys, xs = np.mgrid[rr - 2:rr + 3, cc - 2:cc + 3]
        sw = score[rr - 2:rr + 3, cc - 2:cc + 3]
        row, col = float((ys * sw).sum() / sw.sum()), float((xs * sw).sum() / sw.sum())
        tol = 2.0 + ya.misfit_px
        x, y = float(xa.value(col)), float(seg.value(row))
        out.append({"x": round(x, 3), "y": y, "lo": y - tol * per_y, "hi": y + tol * per_y,
                    "px": [col, row], "px_lo": row - tol, "px_hi": row + tol,
                    "note": f"ring of radius {r:.0f} px, {score[rr, cc]:.2f} of its visible outline in colour, "
                            f"inside {inside[rr, cc]:.2f}; x to within {(2 + xa.misfit_px) * per_x:.3f}"})
    out.sort(key=lambda d: d["x"])
    # two circles a column apart would make one x index twice: keep both but separate the x by the
    # printed precision; they do not occur on these panels
    return out
