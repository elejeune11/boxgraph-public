"""Shared reading code for Fig. 2 (p. 3), middle and bottom: model waveforms in the basal
condition against time. Middle: systemic arterial pressure (continuous line) and left ventricle
pressure (dashed); bottom: cardiac output (flow out of the left ventricle).

Each panel is a frame with inward tick marks. The crop is straightened first. Calibration: x, the
frame's left side (label 0) and the inward ticks on the bottom side (0.5, 1, 1.5 s); y, the
frame's bottom side (0) and the inward ticks on the left side (the other labels; for the middle
panel the frame's top side is 150). The continuous line is the one long piece of ink inside the
frame; the dashes of the dashed line are short pieces, left out.
"""
import importlib.util
import os

import numpy as np

_spec = importlib.util.spec_from_file_location(
    "_u98", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_u98.py"))
u = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(u)

PANELS = {"mid": dict(y_ticks=[50, 100], y_top=150), "bot": dict(y_ticks=[200, 400, 600], y_top=None)}


def read_curve(image, at, name):
    spec = PANELS[name]
    img, angle, back = u.straighten(image)
    m = u.ink(img)
    H, W = m.shape
    v = u.long_lines(m, 1, int(0.6 * H))
    h = u.long_lines(m, 0, int(0.6 * W))
    left, right, top, bottom = v[0], v[-1], h[0], h[-1]
    xt = [c for c, n in u.tick_marks(m, bottom[:2], 0, -1, length=(8, 80)) if left[1] + 40 < c < right[0] - 10]
    yt = [r for r, n in u.tick_marks(m, left[:2], 1, +1, length=(8, 80)) if top[1] + 10 < r < bottom[0] - 40]
    xs = u.evenly(xt, 3)
    ys = u.evenly(yt, len(spec["y_ticks"]))
    xcal = u.Cal([((left[0] + left[1]) / 2.0, 0.0)] + list(zip(xs, [0.5, 1.0, 1.5])))
    ym = [((bottom[0] + bottom[1]) / 2.0, 0.0)] + list(zip(ys, spec["y_ticks"][::-1]))
    if spec["y_top"] is not None:
        ym.append(((top[0] + top[1]) / 2.0, spec["y_top"]))
    ycal = u.Cal(ym)
    inside = np.zeros_like(m)
    inside[top[1] + 12: bottom[0] - 12, left[1] + 12: right[0] - 12] = \
        m[top[1] + 12: bottom[0] - 12, left[1] + 12: right[0] - 12]
    solid = np.zeros_like(m)
    for b in u.blobs(inside):
        if b["w"] > 300:
            solid[b["r0"]:b["r1"], b["c0"]:b["c1"]] |= b["mask"]
    out = u.read_line(solid, xcal, ycal, at)
    note = (f"tilt {angle:.2f} deg straightened; calibration misfit x {xcal.misfit:.1f} px, "
            f"y {ycal.misfit:.1f} px")
    for d in out:
        d["note"] = (d.get("note", "") + " " + note).strip()
    return u.unrotate(out, back)
