# Fig. 7 (p. 8) of jin2015: four log-log panels with green, red, black and blue solid curves
# (neo-Hookean wrinkle analysis) and open blue circles (von Karman plate on a linear substrate).
# Axes are calibrated from the panel's own tick marks: the long (major) ticks carry the decade
# labels seen on the panel, every minor tick is matched to k*10^n and included in the fit.
import importlib.util
import pathlib

import numpy as np

_spec = importlib.util.spec_from_file_location("jin_helpers", pathlib.Path(__file__).resolve().parent / "_jin.py")
J = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(J)

# decade labels on the long ticks, in pixel order (x left to right, y top to bottom), and the
# decade range of the axis, as printed on each panel
PANELS = {
    "a": {"x": ([10.0, 100.0], 0, 3), "y": ([0.1, 0.01], -3, 0)},
    "b": {"x": ([10.0, 100.0], 0, 3), "y": ([10.0], 0, 2)},
    "c": {"x": ([1.0, 10.0, 100.0], -1, 3), "y": ([0.1, 0.01], -3, 0)},
    "d": {"x": ([1.0, 10.0, 100.0], -1, 3), "y": ([10.0], 0, 2)},
}


def calibrate(image, panel):
    box, half = J.frame(image)
    cfg = PANELS[panel]
    xt = J.merge_ticks(J.ticks(image, box, half, "bottom"), J.ticks(image, box, half, "top"))
    yt = J.merge_ticks(J.ticks(image, box, half, "left"), J.ticks(image, box, half, "right"))
    xax = J.log_axis(xt, *cfg["x"])
    yax = J.log_axis(yt, *cfg["y"])
    return box, half, xax, yax


def mask_of(image, box, half, colour):
    if colour == "black":
        m = J.dark(image, 100)
        c0, r0, c1, r1 = [int(round(v)) for v in box]
        h = int(half) + 26  # frame line plus the longest tick
        m[:, :c0 + h] = False
        m[:, c1 - h:] = False
        m[:r0 + h, :] = False
        m[r1 - h:, :] = False
        return m
    return J.hue_mask(image, colour)


def read_line(image, at, panel, colour, thick_max=None, seed_col_frac=None):
    """A solid curve of one colour. With seed_col_frac, the curve is followed from where it
    meets the column at that fraction of the plot width (taking its single run there)."""
    box, half, xax, yax = calibrate(image, panel)
    m = mask_of(image, box, half, colour)
    tag = (f"{colour} curve; x axis from {xax.n} ticks (misfit {xax.misfit_px:.1f} px), "
           f"y axis from {yax.n} ticks (misfit {yax.misfit_px:.1f} px);")
    seed = None
    margin = int(half) + 26
    if colour == "blue":  # the open circles lie on the blue curve: erase each ring before tracing
        c0, r0, c1, r1 = box
        found, R = J.ring_centres(m, 14, 30, (c0 + half + 2, r0 + half + 2, c1 + 60, r1 - half - 2))
        yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]]
        for c, r, _ in found:
            m[(xx - c) ** 2 + (yy - r) ** 2 <= (R + 10) ** 2] = False
        tag += f" {len(found)} circles of radius {R} px erased;"
    if seed_col_frac is not None:
        c0, r0, c1, r1 = box
        col = c0 + seed_col_frac * (c1 - c0)
        rr = J.curve_rows(m, col, r0 + margin, r1 - margin)
        if len(rr) == 1:
            seed = (xax.to_val(col), yax.to_val(rr[0][0]))
    return J.read_curve(m, xax, yax, box, half, at, win=55 if colour == "blue" else 40, thick_max=thick_max,
                        margin=margin, tag=tag, seed=seed)


def read_circles(image, panel, rmin=14, rmax=30):
    """The open blue circles: centre of each ring, with an interval of the ring's own
    thickness plus the calibration misfit and one pixel."""
    box, half, xax, yax = calibrate(image, panel)
    m = J.hue_mask(image, "blue")
    c0, r0, c1, r1 = box
    inner = (c0 + half + 2, r0 + half + 2, c1 + 2 * rmax, r1 - half - 2)  # circles may sit on the right frame
    found, R = J.ring_centres(m, rmin, rmax, inner)
    out = []
    for col, row, score in found:
        w = 3.0 + yax.misfit_px + 1.0
        lo, hi = yax.to_val(row + w), yax.to_val(row - w)
        out.append({"x": xax.to_val(col), "y": yax.to_val(row), "lo": min(lo, hi), "hi": max(lo, hi),
                    "px": [col, row], "px_lo": row - w, "px_hi": row + w,
                    "note": f"ring radius {R} px, match {score:.2f}; axes misfit x {xax.misfit_px:.1f}, "
                            f"y {yax.misfit_px:.1f} px"})
    return out
