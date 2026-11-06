"""Single-colour curves on MATLAB-style panels (Figs. 3, 6, 7, 10-13). Everything is found in the image.

Calibration (_common.calibrate): the tick labels left of and under the box, matched to the printed
values given per panel below. Where a lone '0' sits under the lower-left corner (it could be the
first x or the lowest y label), it is left out (x_skip / y_stop) and only unambiguous labels are used.

A curve is the set of pixels of its colour (distance < 90 in RGB) inside the box. At each x, a
straight line is fitted to those pixels in a window of +-W columns (W given per panel, small
against the curve's bends); the value is that line at x and the interval is the spread of the
pixels about it (the line's thickness, or more where the curve is steep), plus the y misfit and
the x misfit times the local slope, plus 2 px.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
c_ = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(c_)

COLORS = {"blue": (0, 0, 255), "red": (255, 0, 0), "green": (0, 128, 0), "black": (0, 0, 0), "navy": (55, 55, 150),
          "cyan": (0, 190, 190), "purple": (185, 0, 255)}

_T6 = [500, 400, 300, 200, 100, 0, -100]
PANELS = {
    "6a_aorta": dict(x=[0.2, 0.4, 0.6, 0.8, 1.0], y=_T6, dpi=1500, x_skip=60),
    "6a_pulm": dict(x=[0.2, 0.4, 0.6], y=_T6, dpi=1500, x_skip=60),
    "10": dict(x=[0.1, 0.3, 0.5, 0.7, 0.9, 1.1], y=[16, 12, 8, 4], dpi=1200),
    "11": dict(x=[0.2, 0.4, 0.6], y=[40, 30, 20, 10, 0], dpi=1200, x_skip=60),
    "13p_ab": dict(x=[-50, 0, 50, 100], y=[140, 100, 60, 20], dpi=1500),
    "13p_c": dict(x=[-50, 0, 50, 100], y=[25, 20, 15, 10, 5], dpi=1500, y_stop=150),
    "13q_ac": dict(x=[-50, 0, 50, 100], y=_T6, dpi=1500),
    "13q_b": dict(x=[-50, 0, 50, 100], y=[3.0, 2.5, 2.0, 1.5, 1.0, 0.5], dpi=1500, y_stop=150),
    "3a": dict(x=[0.2, 0.4, 0.6, 0.8, 1.0], y=[500, 400, 300, 200, 100, 0, -100], dpi=1500, x_skip=60),
    "3b": dict(x=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6], y=[500, 400, 300, 200, 100, 0, -100], dpi=1500, x_skip=60),
    "7a_aorta": dict(x=[0, 0.2, 0.4, 0.6, 0.8, 1.0], y=[120, 110, 100, 90, 80], dpi=1500),
    "7a_pulm": dict(x=[0.2, 0.4, 0.6], y=[15, 10, 5], dpi=1500, x_skip=60, y_stop=60),
    "7d_sys": dict(x=[4, 3, 2, 1, 0], y=[120, 100, 80, 60, 40, 20, 0], dpi=1500),
    "7d_pulm": dict(x=[4, 3, 2, 1, 0], y=[8, 6, 4, 2, 0], dpi=1500),
}


def calibrate(image, panel):
    p = PANELS[panel]
    s = p["dpi"] / 1800.0
    return c_.calibrate(image, p["x"], p["y"], x_gap=40 * s, x_height=260 * s, x_merge=80 * s,
                        y_gap=25 * s, y_width=420 * s, margin=75 * s,
                        x_skip=p.get("x_skip"), y_stop=p.get("y_stop"))


def read(image, at, panel, color, half_window=12):
    cal = calibrate(image, panel)
    s = PANELS[panel]["dpi"] / 1800.0
    mask = c_.inside(cal, c_.color_mask(image, COLORS[color], 90), int(12 * s) + 2)
    return c_.read_color_curve(image, cal, at, mask, half_window)
