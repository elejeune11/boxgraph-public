"""Fig. 3d and 3e (PDF p. 4), read by _kit.py.

3d: cell traction (Pa, ticks 0-160); 3e: actin flow (nm/s, ticks 0-120); both against substrate Young's
modulus (kPa, log ticks 0.1-100). Red: control (filled discs, s.e.m. bars) and the model with talin
unfolding (solid line); blue: talin 2 shRNA (filled discs) and the model without talin unfolding (solid
line). Blue is drawn over red: below about 4 kPa the two lines coincide and the blue one covers the red
one, which is then read on the blue line drawn over it (the reading's note says where). Both lines are
traced from 40 kPa, near their right ends, where the red one is the upper (3d) or lower (3e) of the two;
for each line, the columns that trace missed come from a trace started at 0.4 kPa.
"""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("elosegui2016_kit", Path(__file__).with_name("_kit.py"))
kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kit)

PANELS = {"d": {"ylabels": [0, 40, 80, 120, 160], "red_branch": "top"},
          "e": {"ylabels": [0, 40, 80, 120], "red_branch": "bottom"}}
RED, BLUE = 355, 225
R_MARKER = 32   # px at 1400 dpi


def line(image, at, panel, which):
    img = np.asarray(image)
    P = PANELS[panel]
    cal = kit.calibrate(img, P["ylabels"])
    red, blue = kit.color_mask(img, RED), kit.color_mask(img, BLUE)
    if which == "blue":
        blue_branch = "bottom" if P["red_branch"] == "top" else "top"
        path = kit.trace(blue, cal, 40.0, branch=blue_branch, max_run=30)
        left = kit.trace(blue, cal, 0.4, branch="top", max_run=30)
        path.update({c: r for c, r in left.items() if c not in path})
        return kit.read_curve(img, cal, path, at)
    path = kit.trace(red | blue, cal, 40.0, branch=P["red_branch"], max_run=30)
    left = kit.trace(red | blue, cal, 0.4, branch="top", max_run=30)
    path.update({c: r for c, r in left.items() if c not in path})
    redpath = kit.trace(red, cal, 40.0, branch=P["red_branch"], max_run=30)
    redpath.update(kit.trace(red, cal, 0.4, branch="top", max_run=30))
    out = kit.read_curve(img, cal, path, at)
    for r in out:
        if r.get("px") and not any(c in redpath for c in range(int(r["px"][0]) - 3, int(r["px"][0]) + 4)):
            r["note"] += "; red line hidden under the blue line here, read on the blue line drawn over it"
    return out


def points(image, panel, which):
    img = np.asarray(image)
    cal = kit.calibrate(img, PANELS[panel]["ylabels"])
    red, blue = kit.color_mask(img, RED), kit.color_mask(img, BLUE)
    if which == "red":   # blue is drawn over red: red discs crossed by blue bars or lines are still found
        return kit.read_points(img, cal, red, R=R_MARKER, cover=blue)
    return kit.read_points(img, cal, blue, R=R_MARKER)
