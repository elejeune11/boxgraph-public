"""Fig. 1g (PDF p. 4): the dotted steel-blue line, the pre-stress profile chosen for the simulations,
normalised to its midline value, against the row of cells from the ventral midline.

Calibration (gnuplot, see _gp.py): y: the top frame line carries the printed 1.2, the bottom one 0,
the major inward ticks on the left frame line 1, 0.8, 0.6, 0.4, 0.2; x: the left frame line carries 0
and the inward ticks 1 to 7 (left to right; the mirrored ticks on the top frame line are used when
dots hide bottom ones). The crop leaves out the time colour bar to the right of the plot (its frame
would pass for the plot's). The dotted line is drawn over the dots; its dots and gaps are read over a
window of +-25 columns. Colour steel blue (48, 96, 128).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _gp  # noqa: E402

SPEC = {"ylabels": [1.2, 1.0, 0.8, 0.6, 0.4, 0.2, 0.0],
        "xlabels": [(0.0, "frame-left")] + [(float(k + 1), f"tick:{k}") for k in range(7)],
        "rgb": (48, 96, 128), "tol": 40, "win": 25, "rows": (-0.05, 1.15)}


def read(image, at):
    return _gp.read_lines(image, at, SPEC)
