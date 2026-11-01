"""Figs. 4D (PDF p. 6, 3T3 fibroblasts on PA gels) and 5D (PDF p. 7, MSCs on HA
gels): box plots of the measured spreading area (red: elastic, blue:
viscoelastic) and the predicted areas (cross: elastic, triangle: viscoelastic).
Read by _boxplot.py (see its docstring).  y labels: 0 to 0.5 (Fig. 4D) and 0 to
1.5 (Fig. 5D), in units of 10^4 um^2.
"""
import importlib.util
from pathlib import Path

BOXES = [([255, 0, 0], 90), ([0, 0, 255], 90)]
PANELS = {
    "4d": {"y_labels": [0.5, 0.4, 0.3, 0.2, 0.1, 0], "y_mult": 1e4, "ticks": "out", "tick_len": 30,
           "axis_max_col": 900, "boxes": BOXES, "src_px": 8, "line_w": 8, "open_r": 6,
           "center_px": [0, 10]},
    "5d": {"y_labels": [1.5, 1, 0.5, 0], "y_mult": 1e4, "ticks": "out", "tick_len": 30,
           "axis_max_col": 900, "boxes": BOXES, "src_px": 8, "line_w": 8, "open_r": 6,
           "center_px": [0, 10]},
}


def read(image, panel, kind):
    spec = importlib.util.spec_from_file_location("gong2018_boxplot", Path(__file__).with_name("_boxplot.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if kind == "pred":
        return mod.read_markers(image, PANELS[panel])
    return mod.read_box(image, PANELS[panel], kind)
