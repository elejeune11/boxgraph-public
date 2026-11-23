"""Fig. 2(F) (PDF p. 6): the open green squares, the numerical optimum of the mean-field model, tau = 10 (F = 2).

Axes as in fig2f_tau10.py; symbols read by _marks.py after the solid green line of Eq. 6
(same colour) is traced and removed. Symbols the line covers fail the size test and are
left out. The legend is blanked.
"""
import importlib.util
from pathlib import Path

MARKS = Path(__file__).with_name("_marks.py")

OTHERS = [(10, 10, 130), (230, 15, 90), (250, 65, 15), (255, 255, 255), (30, 30, 30), (128, 128, 128)]
SPEC = {"color": (10, 110, 60), "others": OTHERS, "tol": 70, "kind": "open", "fill_max": 0.5,
        "ref_width": 2659, "blank": [[1360, 0, 2300, 800]], "right": 40, "join": 4, "aspect": 1.3,
        "line_seed": (1174, 1430), "line_pad": 3, "line_max": 70,
        "x": {"labels": [500, 1000, 1500]},
        "y": {"labels": [0.03, 0.02, 0.01, 0], "y0_at_axis": True, "y_end_at_axis": True}}


def read(image, at):
    spec = importlib.util.spec_from_file_location("alonsomatilla2023_marks", MARKS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_markers(image, SPEC)
