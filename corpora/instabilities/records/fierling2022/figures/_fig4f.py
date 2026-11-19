"""Shared calibration for Fig. 4f (PDF p. 8): curvature of the ventral tissue along AP and DV against
time (gnuplot, see _gp.py).

y: the major inward ticks on the left frame line carry the printed 0.01, -0.01, -0.02, -0.03, -0.04,
-0.05 (top to bottom); the thick black zero axis drawn across the plot carries 0 (its tick lies
under it).
x: the inward ticks on the bottom frame line carry the printed -4, -2, 0, 2, 4, 6 (left to right).
The frame lines (the plotted range, -5 to 8 and -0.055 to 0.012) are not labelled and are not used.
A line is the run of its colour near each position (_gp.read_lines). The DV MuVi line carries a shaded
band (minimum and maximum over the n = 6 embryos), drawn in its colour at 25% opacity.
"""
import _gp

YLABELS = [(0.01, "tick:0"), (0.0, "hline"), (-0.01, "tick:1"), (-0.02, "tick:2"), (-0.03, "tick:3"),
           (-0.04, "tick:4"), (-0.05, "tick:5")]
XLABELS = [(float(v), f"tick:{k}") for k, v in enumerate(range(-4, 7, 2))]
GOLD, CYAN, DGOLD, DBLUE = (255, 192, 32), (0, 238, 238), (192, 128, 0), (0, 0, 139)
BAND_DV = (239, 223, 191)  # dark goldenrod at 25% opacity on white


def _restore_ticks(image):
    """The 25% opaque band is drawn over some inward ticks, turning their black into a dark gold that
    the tick finder (dark and grey) misses. Within 50 px inside the top and bottom frame lines, pixels
    that are dark (mean < 90) and not blue (red >= blue, which leaves out the navy line) are set to
    black. Nothing else in the image changes."""
    import numpy as np
    img = image.copy()
    fr = _gp.frame(img)
    f = img.astype(float)
    dark = (f.mean(axis=2) < 90) & (f[:, :, 0] >= f[:, :, 2])
    for r0, r1 in ((int(fr["top_in"]), int(fr["top_in"]) + 50), (int(fr["bottom_in"]) - 50, int(fr["bottom_in"]) + 1)):
        sub = dark[r0:r1, int(fr["left_in"]):int(fr["right_in"]) + 1]
        block = img[r0:r1, int(fr["left_in"]):int(fr["right_in"]) + 1]
        block[sub] = 0
    return np.asarray(img)


def line(image, at, rgb, rows, win=12, tol=50, band=None):
    spec = {"ylabels": YLABELS, "xlabels": XLABELS, "rgb": rgb, "tol": tol, "win": win, "rows": rows}
    if band:
        spec.update({"band_rgb": band, "band_tol": 14, "band_over": [GOLD, CYAN, DGOLD, DBLUE]})
    return _gp.read_lines(_restore_ticks(image), at, spec)
