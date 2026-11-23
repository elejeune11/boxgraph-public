"""Fig. 5(B), inset (PDF p. 10): the dark-blue dots, omega_opt against tau (high-motor rigid limit).

Axes by _fig.calibrate with a lighter ink threshold (the inset's box and ticks are grey):
x ticks at 50 and the box's left line at 0 and right line at 100; y ticks at 50, 100 and the
bottom line at 0, the top line at 150. Dots read by _marks.py (filled symbols). The grey
dashed line under the dots is another colour and is not read.
"""
import importlib.util
from pathlib import Path

MARKS = Path(__file__).with_name("_marks.py")

SPEC = {"color": (10, 40, 100), "others": [(190, 190, 190), (255, 255, 255), (30, 30, 30), (200, 10, 20)],
        "tol": 70, "thr": 225, "smax": 30, "kind": "filled", "solid": 5, "join": 3, "merge": 1.45,
        # the inset is a bitmap of 8 px blocks at this dpi: dots vary by a block in size and
        # their centres are uncertain by about half a block plus the x error times the slope
        "rim": 24,
        "ref_width": 1650, "right": 40, "below": 40, "inset": 2,
        "x": {"labels": [0, 50, 100], "x0_at_axis": True, "x_end_at_axis": True},
        "y": {"labels": [150, 100, 50, 0], "y0_at_axis": True, "y_end_at_axis": True}}


def read(image, at):
    spec = importlib.util.spec_from_file_location("alonsomatilla2023_marks", MARKS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_markers(image, SPEC)
