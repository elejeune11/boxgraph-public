"""Fig. 6a-i (PDF p. 7), read by _kit.py.

Each panel: cell traction (Pa, ticks 0, 40, 80, 120, 160) against substrate Young's modulus (kPa, log
ticks 0.1, 1, 10, 100). One colour per panel (red a, d, g; blue b; green e, h; black c, f, i): control
cells as filled markers, talin 2 shRNA cells as open circles, both with s.e.m. bars; the model with talin
unfolding as a solid line and without as a dashed line (caption: 'Solid and dashed lines show model
predictions with and without talin unfolding'). A grey line (detection level) and a blue dashed vertical
line (reference threshold) are not of the panel's colour, except in panel b, where the axes and the
vertical line are blue (the axes are found in black or blue there; the vertical line is never taken for
a curve: lines are traced only through runs no taller than a steep line's, and dashes must be wider than
tall).

Solid line: traced from 38 kPa, where it is the upper of the two lines, leftwards and rightwards; where
that trace stops short of the left end, the columns left of it come from a trace started at 0.4 kPa.
Dashed line: its dashes are the components of the panel's colour as thick as the line, elongated and not
lying on the solid line (_kit.dashes, chained from the right); where the two lines coincide (low
rigidities) the dashes merge into the solid line, so to the left of the leftmost dash the dashed line is
read on the solid line, but only if that dash starts on the solid line (within 40 px); otherwise the
positions left of it are not read. Gaps between dashes are bridged by interpolation (the note says so,
and the interval grows by half the jump).
Markers: filled markers of radius about 35 px and open circles of radius about 42 px at 1650 dpi. The
legend (top left: E below 6 kPa and traction above 125 Pa, where no data or lines are plotted) is left out.
"""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("elosegui2016_kit", Path(__file__).with_name("_kit.py"))
kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kit)

YLABELS = [0, 40, 80, 120, 160]
HUE = {"red": 0, "blue": 225, "green": 115}
PANEL_COLOUR = {"a": "red", "d": "red", "g": "red", "b": "blue", "e": "green", "h": "green",
                "c": "black", "f": "black", "i": "black"}
R_FILLED, R_OPEN = 35, 42
SEED = 38.0
LEGEND_X, LEGEND_Y = 6.0, 125.0   # kPa, Pa


def _setup(image, panel):
    img = np.asarray(image)
    c = PANEL_COLOUR[panel]
    m = kit.dark_mask(img) if c == "black" else kit.color_mask(img, HUE[c])
    cal = kit.calibrate(img, YLABELS, axis_extra=m if panel == "b" else None)
    legend = np.zeros(m.shape, bool)
    legend[:int(round(cal["ay"] * LEGEND_Y + cal["by"])), :int(round(kit.col_of(cal, LEGEND_X)))] = True
    return img, m, cal, legend


def line(image, at, panel, which):
    img, m, cal, legend = _setup(image, panel)
    solid = kit.trace(m & ~legend, cal, SEED, branch="top", max_run=50, max_jump=30)
    if solid:
        # where the trace from the right stopped short, continue with a trace from the left end (0.4 kPa,
        # where only the one line is drawn), for the columns left of where the first trace ended
        left = kit.trace(m & ~legend, cal, 0.4, branch="top", max_run=50, max_jump=30)
        lo = min(solid)
        solid.update({c: r for c, r in left.items() if c < lo})
    if which == "talin":
        return kit.read_curve(img, cal, solid, at)
    dash = kit.dashes(m, cal, exclude=legend, avoid=solid)
    if not dash:
        return [{"x": float(x), "y": None, "note": "no dash found"} for x in at]
    first = min(dash)
    near = [c for c in solid if abs(c - first) <= 10]
    joins = bool(near) and min(abs(sum(solid[c]) / 2 - sum(dash[first]) / 2) for c in near) <= 40
    path = dict(dash)
    if joins:   # the first dash leaves the solid line: to its left the two lines are one
        path.update({c: r for c, r in solid.items() if c < first - 5})
    out = kit.read_curve(img, cal, path, at)
    for r in out:
        if r.get("px") and r["px"][0] < first - 5:
            r["note"] += "; left of the first separate dash: the dashed line lies on the solid line here"
        elif r.get("y") is None and kit.col_of(cal, r["x"]) < first:
            r["note"] = ("the dashed line cannot be told apart here (its first separate dash, at "
                         f"{kit.x_of(cal, first):.1f} kPa, does not start on the solid line)")
    return out


def points(image, panel, which):
    img, m, cal, legend = _setup(image, panel)
    hollow = which == "shrna"
    out = kit.read_points(img, cal, m & ~legend, R=R_OPEN if hollow else R_FILLED, hollow=hollow)
    return out
