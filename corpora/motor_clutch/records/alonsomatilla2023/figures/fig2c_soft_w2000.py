"""Fig. 2(C) (PDF p. 6): the solid green triangles, omega = 2000, critical activity on soft substrates.

Axes as in fig2c_eq5.py; symbols read by _marks.py. The legend is blanked.
"""
import importlib.util
from pathlib import Path

MARKS = Path(__file__).with_name("_marks.py")

OTHERS = [(5, 45, 95), (80, 20, 245), (200, 0, 0), (255, 255, 255), (30, 30, 30), (128, 128, 128)]
SPEC = {"color": (140, 187, 140), "others": OTHERS, "tol": 70, "smax": 40, "kind": "filled", "triangle": True,
        "ref_width": 2603, "blank": [[680, 190, 1370, 640]], "right": 40, "join": 6,
        "x": {"labels": [0, 5, 10], "x0_at_axis": True, "x_end_at_axis": True},
        "y": {"labels": [0.8, 0.6, 0.4, 0.2, 0], "y0_at_axis": True, "y_end_at_axis": True}}


def read(image, at):
    spec = importlib.util.spec_from_file_location("alonsomatilla2023_marks", MARKS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_markers(image, SPEC)
