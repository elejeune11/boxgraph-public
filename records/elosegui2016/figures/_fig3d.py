"""Fig. 3d (PDF p. 4): cell traction (Pa, ticks 0-160) against substrate Young's modulus (kPa, log).
Red: control (filled discs) and the model with talin unfolding (solid line); blue: talin 2 shRNA (filled
discs) and the model without talin unfolding. The blue line is drawn over the red one where they coincide
(E below about 4 kPa). Reading by _kit.py."""
import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("elosegui2016_kit", Path(__file__).with_name("_kit.py"))
kit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kit)

YLABELS = [0, 40, 80, 120, 160]
RED, BLUE = 355, 225


def setup(image):
    img = np.asarray(image)
    cal = kit.calibrate(img, YLABELS)
    return img, cal


def line(image, at, which):
    img, cal = setup(image)
    red = kit.color_mask(img, RED)
    blue = kit.color_mask(img, BLUE)
    if which == "blue":
        path = kit.trace(blue, cal, 0.5, branch="top", max_run=30)
        return kit.read_curve(img, cal, path, at)
    # red: traced from the right end, where it is alone; where the blue line covers it, the blue run is used
    path = kit.trace(red | blue, cal, 30.0, branch="top", max_run=30)
    redpath = kit.trace(red, cal, 30.0, branch="top", max_run=30)
    out = kit.read_curve(img, cal, path, at)
    for r in out:
        if r.get("px") and not any(c in redpath for c in range(int(r["px"][0]) - 3, int(r["px"][0]) + 4)):
            r["note"] += "; red line hidden under the blue line here, read on the blue line drawn over it"
    return out


def points(image, which):
    img, cal = setup(image)
    red, blue = kit.color_mask(img, RED), kit.color_mask(img, BLUE)
    if which == "red":   # blue is drawn over red: red discs crossed by blue bars or lines are still found
        return kit.read_points(img, cal, red, R=32, cover=blue)
    return kit.read_points(img, cal, blue, R=32)
