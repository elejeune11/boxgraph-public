"""Fig. 2(a) (PDF p. 3): the black points, finite-element thresholds for cusp formation against eta.

Shared code in _tal.py; calibration as fig2a_linear.py. The points are filled black circles joined by
a black line, and the blue linear-instability line crosses some of them, so the mask is black or
blue ink. The circles (radius about 20 px) are found as the cores of that mask farther than
15 px from any background pixel: lines (about 12 px wide), text strokes and arrowheads have no such
core. Each core's centroid is a circle's centre; where lines run into a circle the core can shift
by a few pixels, so the interval is +- (misfit + 5 px). The circle at eta = 10 is cut by the right
frame line, has no full core and is not read. Text labels ("Cusped
folds", "Smooth folds", "Valleys sulcify", the gs/eta_s annotation, "Flat", "Sulci", "Linear
instability") are blanked first. The point at the right frame line (eta = 10) is cut by the frame
and is read from the part inside the frame, so its centroid is biased to the left; its x is
reported as read.
"""
from pathlib import Path

SPEC = {
    "x": {"ticks": [2, 4, 6, 8], "at_axis": 0, "major_len": 20, "span_end": 2900},
    "y": {"ticks": [1.2, 1.4, 1.6, 1.8], "at_axis": 1.0, "major_len": 20, "span_start": 200},
    "ink": ["black", "blue"], "pad": 14, "core": 15, "area": [30, 800], "max_aspect": 1.6, "hole_max": 0, "pad_px": 5,
    "blank": [[1080, 760, 1560, 1050], [1750, 480, 2650, 650], [1900, 1060, 2900, 1180],
              [1900, 1500, 2850, 1650], [800, 1450, 1100, 1600], [650, 580, 1050, 720],
              [1150, 1620, 1700, 1920], [1500, 1650, 1640, 1800], [2320, 1180, 2400, 1400]],
}


def _tal():
    import importlib.util
    s = importlib.util.spec_from_file_location("tallinen2015_tal", Path(__file__).with_name("_tal.py"))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read(image, at):
    return _tal().read_markers(image, SPEC)
