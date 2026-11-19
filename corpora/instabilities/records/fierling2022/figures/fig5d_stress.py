"""Fig. 5d (PDF p. 10): the black step line, simulated AP stress sigma_AP against DV distance from the
ventral midline (at t = 0'30'').

Calibration from the image (see _gp.py): y from the frame lines (printed 250 at the top, -50 at the
bottom) and the major inward ticks on the left frame line between them (200, 150, 100, 50, 0); x
from the frame lines (printed 0 and 40) and the four long inward ticks (8, 16, 24, 32; the short
ones between are minor ticks).
The line is black like the frame: it is read as the run of black near each position, inside the
frame. At x = 0 the line starts on the left frame line, whose own black would be taken for it: the
first step is read 1 um inside the frame (it runs flat from the frame to about 3 um) and reported at
x = 0, with a note.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))  # the shared helpers beside this file
import _gp  # noqa: E402

SPEC = {"ylabels": [250.0, 200.0, 150.0, 100.0, 50.0, 0.0, -50.0],
        "xlabels": [(0.0, "frame-left"), (8.0, "tick:0"), (16.0, "tick:1"), (24.0, "tick:2"), (32.0, "tick:3"),
                    (40.0, "frame-right")],
        "rgb": (0, 0, 0), "tol": 60, "win": 12, "rows": (-45.0, 245.0),
        # the first step of the black line touches the left frame line and would pass for a long tick:
        # tick candidates are kept below 100 px (the ticks found are about 50 px long)
        "tick_max": 100}


def read(image, at):
    shifted = [float(x) + 1.0 if float(x) == 0.0 else float(x) for x in at]
    out = _gp.read_lines(image, shifted, SPEC)
    for r, x in zip(out, at):
        if float(x) == 0.0:
            r["x"] = 0.0
            r["note"] = r.get("note", "") + "; read at 1 um, on the first flat step that starts at the frame"
    return out
