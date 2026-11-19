"""Shared calibration for Fig. 3b (PDF p. 7), apical area fold change by row (gnuplot, see _gp.py).

y: the two major inward ticks on the left frame line carry the printed 1.2 and 0.8 (top to bottom);
the long horizontal reference line carries 1 (the plot draws y = 1 across it); the bottom frame line
carries 0.6. The top frame line has no label (the range is open above) and is not used.
x: the inward ticks on the bottom frame line carry the row labels 1 to 9, left to right.
Markers: open squares, read by _gp.read_markers (outline sides, error bars with caps). The series
are drawn in this order: MuVi SPIM (orange), confocal (red), simulations (blue); a later series'
colour counts as the earlier one's where it is drawn over it. `rows` keeps out the legend's sample
markers, which lie below the value 0.735 at the right.
"""
import _gp

YLABELS = [(1.2, "tick:0"), (1.0, "hline"), (0.8, "tick:1"), (0.6, "frame-bottom")]
XLABELS = [(float(k + 1), f"tick:{k}") for k in range(9)]
ORANGE, RED, BLUE = (255, 192, 32), (255, 0, 0), (0, 0, 255)


def read(image, at, rgb, over, error_bars, rows):
    # error bars are followed in their own colour only (an overlying marker's side can lie along a
    # bar and would extend it); gaps where a later series' marker hides the bar are bridged, up to
    # a little more than one marker's height
    spec = {"ylabels": YLABELS, "xlabels": XLABELS, "rgb": rgb, "over": over, "tol": 60,
            "shape": "square", "error_bars": error_bars, "rows": rows,
            "bar_own_only": True, "dash_gap": 130}
    return _gp.read_markers(image, at, spec)
