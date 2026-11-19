"""Fig. 4H (PDF p. 9): the blue dots, measured opening angle Phi against delta/R of single folds
(n = 24 from 3 replicates).

Shared code in _fig4.py (calibration from the ticks: x step 0.25, y step 10 degrees, as for the
curves of this panel): blue blobs inside the axes, touching dots split by area. The legend, in the
lower right part of the plot (its blue dot beside "Phi"), is left out: blobs right of half the
plot width and below 70% of its height (no data point lies there). No error bars are drawn. Interval: 3 px on a dot's centre
(half a dot radius for a dot split from an overlap) plus twice the calibration misfit.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("trushko2020_fig4", Path(__file__).with_name("_fig4.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    m = _mod()
    cal = m.calibrate(image, 0.25, 10.0)
    pts = m.read_markers(image, m.BLUE, 0.25, 10.0, 0.0)
    W = image.shape[1]
    x0 = cal["ycol"]
    return [p for p in pts
            if not (p["px"][0] > x0 + 0.5 * (W - x0) and p["px"][1] > 0.7 * cal["xrow"])]
