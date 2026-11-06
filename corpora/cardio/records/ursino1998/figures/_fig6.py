"""Shared reading code for Fig. 6 (p. 7): cardiac output (top), stroke volume (middle) and
normalized dSV/dHR (bottom) against paced heart rate. Model points are filled diamonds joined by a
thin line; Melbin et al.'s data (bottom) are open circles joined by a dashed line. Calibration as
in _excel.py: x ticks 20-180 (top, middle; labels every 40 beats/min) or 70-190 on the line at
dSV/dHR = 0 (bottom); y ticks at every printed label.
"""
import importlib.util
import os

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "_excel", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_excel.py"))
X = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(X)

PANELS = {
    "co": dict(xvals=[20, 60, 100, 140, 180], yvals=[50, 60, 70, 80, 90, 100, 110, 120, 130]),
    "sv": dict(xvals=[20, 60, 100, 140, 180], yvals=[20, 40, 60, 80, 100, 120]),
    "d": dict(xvals=[70, 110, 150, 190], yvals=[-1, -0.8, -0.6, -0.4, -0.2, 0], x_axis="top",
              x_at_yaxis=True, y_at_xaxis=True),
}


def read_diamonds(image, panel, legend=None):
    p = X.Panel(image, legend=legend, **PANELS[panel])
    pts = p.filled(12, kinds={"diamond"}, amin=600)
    # a marker is a blob of the common marker size and shape; thick ink where lines cross a
    # circle is smaller or misshapen
    med_a = float(np.median([q["area"] for q in pts]))
    med_w = float(np.median([q["w"] for q in pts]))
    pts = [q for q in pts if abs(q["area"] - med_a) < 0.3 * med_a and abs(q["w"] - med_w) < 0.2 * med_w]
    return p.points(pts, 3.0, "filled diamond, at the centre of its box")


def read_circles(image, panel, legend=None):
    p = X.Panel(image, legend=legend, **PANELS[panel])
    pts = p.open(300, 6000, kinds={"circle"})
    return p.points(pts, 3.0, "open circle, at the centre of its hole")
