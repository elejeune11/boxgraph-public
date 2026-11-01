"""Figs. 4B (PDF p. 6, PA gels) and 5B (PDF p. 7, HA gels) of gong2018: measured
relaxation stiffness vs time for the elastic (blue dots) and viscoelastic (red
dots) gels, and, in the inset, the normalized stiffness of the viscoelastic gel
(red dots) with its fitted curve (black line), on a log time axis.

Main panel: the inset covers the top and right spines, so the calibration uses
the left and bottom axis lines (_axes.py, box "axes": their extents give the
top-left and bottom-right corners, which carry the first and last labels); y
ticks from the left spine, where the red dots near t = 0 hide some ticks and add
marks of their own (`anchored`: only marks within a few px of the evenly spaced
positions between the two labelled corners are kept, each with its label); x
ticks from the bottom spine.  The
inset's area and the coloured in-plot labels are excluded.
Inset: its own crop and closed box, ticks from the right and bottom spines.
The dots and the line are read by _lines.py at the reader's chosen times: the
middle of the run of the colour in a window of +/-`half` columns (the dots are
spaced up to about 60 px at late times).
"""
import importlib.util
from pathlib import Path

PANELS = {
    "4b": {"axes": {"box": "axes", "line_frac": 0.3, "tick_px": 16, "min_col": 350, "corner_px": 14,
                    "x": {"labels": [0, 10, 20, 30, 40, 50], "edge_ticks": ["start", "end"], "band": "bottom"},
                    "y": {"labels": [4, 3.5, 3, 2.5, 2], "edge_ticks": ["start", "end"], "band": "left",
                          "anchored": True}},
           # the inset, and the labels "Viscoelastic ECM" and "Elastic ECM"
           "exclude": [[1450, 0, 3200, 1250], [580, 1180, 1620, 1340], [680, 1620, 1420, 1770]]},
    "5b": {"axes": {"box": "axes", "line_frac": 0.3, "tick_px": 16, "min_col": 400, "corner_px": 14,
                    "x": {"labels": [0, 10, 20, 30, 40, 50], "edge_ticks": ["start", "end"], "band": "bottom"},
                    "y": {"labels": [1.5, 1.4, 1.3, 1.2, 1.1, 1, 0.9], "edge_ticks": ["start", "end"],
                          "band": "left", "anchored": True}},
           "exclude": [[1250, 0, 3200, 1550], [580, 1380, 1450, 1530], [690, 1810, 1300, 1960]]},
}
INSETS = {
    "4b": {"tick_px": 16,
           "x": {"labels": [0.01, 0.1, 1, 10, 100], "scale": "log10", "edge_ticks": ["start", "end"], "band": "bottom"},
           "y": {"labels": [1, 0.9, 0.8, 0.7], "band": "right"}},
    "5b": {"tick_px": 16,
           "x": {"labels": [0.01, 0.1, 1, 10, 100], "scale": "log10", "edge_ticks": ["start", "end"], "band": "bottom"},
           "y": {"labels": [1, 0.9, 0.8, 0.7], "band": "right"}},
}
SERIES = {
    "red": {"color": [217, 83, 25], "tol": 70, "open_r": 0, "max_run": 90, "min_run": 8, "half": 30,
            "src_px": 8, "margin": 25},
    "blue": {"color": [0, 114, 189], "tol": 70, "open_r": 0, "max_run": 90, "min_run": 8, "half": 30,
             "src_px": 8, "margin": 25},
    # inset: the dots under the line, and the black line over the dots
    "inset_dots": {"color": [217, 83, 25], "tol": 70, "open_r": 0, "max_run": 70, "min_run": 6, "half": 6,
                   "src_px": 8, "margin": 25},
    "inset_fit": {"color": [0, 0, 0], "tol": 120, "open_r": 3, "max_run": 50, "min_run": 6, "half": 2,
                  "src_px": 8, "margin": 25},
}
INSET_EXCLUDE = {"4b": [[1450, 0, 2950, 330]], "5b": [[1200, 0, 2900, 600]]}  # the inset legends


def _load(name):
    spec = importlib.util.spec_from_file_location(f"gong2018{name}", Path(__file__).with_name(f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_main(image, at, panel, series):
    p = PANELS[panel]
    return _load("_lines").read_curve(image, at, p["axes"], SERIES[series], p["exclude"])


def read_inset(image, at, panel, series):
    return _load("_lines").read_curve(image, at, INSETS[panel], SERIES[series], INSET_EXCLUDE[panel])
