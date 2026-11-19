"""Shared calibration for Fig. 3c and Fig. 3d (PDF p. 7): AP and DV length fold change at t = -1 min
by row of cells (gnuplot, see _gp.py).

x: the major inward ticks on the bottom frame line carry the printed 1 to 9, left to right.
y: Fig. 3c: the top frame line carries the printed 1.2, the bottom one 0.6; the major inward ticks on
the left frame line carry 1.1, 0.9, 0.8, 0.7 (top to bottom) and the long black reference line 1
(its tick is hidden under it). Fig. 3d: the frame top lies above the printed 1.2, which is the
first inward tick; the ticks carry 1.2, 1.1, 0.9, 0.8, 0.7, the reference line 1, the bottom
frame line 0.6.
Markers: open triangles (up in c, down in d) with min-max error bars, read by _gp.read_markers; the
MuVi points are drawn at each row, the confocal ones 0.1 to its left: each is searched within 0.4
of the row. The point is the triangle's centroid (gnuplot's triangle points put the point a third of
the height from the flat side); the flat side is found in the image and the height comes from the
median height-to-width ratio of the triangles whose outline is whole (an error-bar cap over an apex
would otherwise move it). Simulations: a line, read by _gp.read_lines.
"""
import _gp

XLABELS = [(float(k + 1), f"tick:{k}") for k in range(9)]
Y_C = [(1.2, "frame-top"), (1.1, "tick:0"), (1.0, "hline"), (0.9, "tick:1"), (0.8, "tick:2"),
       (0.7, "tick:3"), (0.6, "frame-bottom")]
Y_D = [(1.2, "tick:0"), (1.1, "tick:1"), (1.0, "hline"), (0.9, "tick:2"), (0.8, "tick:3"),
       (0.7, "tick:4"), (0.6, "frame-bottom")]
GOLD, RED, CYAN = (255, 192, 32), (255, 0, 0), (0, 238, 238)
DGOLD, DRED, DBLUE = (192, 128, 0), (139, 0, 0), (0, 0, 139)


def markers(image, at, ylabels, rgb, over, shape, rows, dash_gap=0):
    spec = {"ylabels": ylabels, "xlabels": XLABELS, "rgb": rgb, "over": over, "tol": 60,
            "shape": shape, "error_bars": True, "rows": rows, "bar_own_only": True,
            "dash_gap": dash_gap, "centre": "longest", "point": "centroid", "apex": "typical"}
    return _gp.read_markers(image, at, spec)


def line(image, at, ylabels, rgb, rows, win=25):
    return _gp.read_lines(image, at, {"ylabels": ylabels, "xlabels": XLABELS, "rgb": rgb, "tol": 50,
                                      "win": win, "rows": rows})
