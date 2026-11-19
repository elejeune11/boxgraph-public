"""Supp. Fig. 3f (PDF p. 25): the solid dark-violet line, simulated depth of the ventral furrow against
the myosin pre-stress (nondimensional).

Calibration (gnuplot, see _gp.py): y: the top frame line carries the printed 0.4, the bottom one 0,
the major inward ticks on the left frame line 0.35 to 0.05 (top to bottom); x: the left frame line
carries 0, the right one 8000, the inward ticks 1000 to 7000 (the line lies on the bottom frame line
up to about 3500 and hides the bottom ticks' lower part, so the mirrored ticks on the top frame line
are used when the bottom ones are not all seen). Colour dark violet (148, 0, 211).
Where the line lies on the bottom frame line it is read from its upper edge (see _gp.read_lines).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _gp  # noqa: E402

SPEC = {"ylabels": [(0.4, "frame-top")] + [(round(0.35 - 0.05 * k, 2), f"tick:{k}") for k in range(7)]
        + [(0.0, "frame-bottom")],
        "xlabels": [(0.0, "frame-left")] + [(1000.0 * (k + 1), f"tick:{k}") for k in range(7)]
        + [(8000.0, "frame-right")],
        "rgb": (148, 0, 211), "tol": 60, "win": 12, "rows": (-0.02, 0.41)}


def read(image, at):
    return _gp.read_lines(image, at, SPEC)
