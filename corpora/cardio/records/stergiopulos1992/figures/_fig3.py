"""Fig. 3 (p. 6): Q/Qn against % stenosis. Shared by the three readings of this panel.

Calibration (_figlib.calibrate): x from the inward tick marks found next to the labels 20, 40, 60, 80
and the frame's left and right lines (the labels 0 and 100 sit at the frame corners); y from the inward
ticks next to the labels 3, 2, 1 that are found and the frame's top and bottom lines (labels 4 and 0 at
the corners); the small rotation of the scan is measured on the frame lines and taken out.
"""

import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage

_spec = importlib.util.spec_from_file_location("_figlib", Path(__file__).with_name("_figlib.py"))
fl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fl)

XV = [0, 20, 40, 60, 80, 100]
YV = [4, 3, 2, 1, 0]


def _solid(d, fr, X, Y):
    r_lo, r_hi = fr["top"][1] + 3, fr["bottom"][0] - 2
    c0 = int(X.px(1.5))
    w = fl.line_width(d, c0, int(Y.px(1.1)), int(Y.px(0.9)))
    tr = fl.trace(d, c0, Y.px(1.0), int(X.px(99.0)), r_lo, r_hi, max_jump=10, width=w, prefer="low")
    return tr, w


def _dashed(d, fr, X, Y):
    r_lo, r_hi = fr["top"][1] + 3, fr["bottom"][0] - 2
    c0 = int(X.px(1.5))
    rs = fl.runs(d[:, c0], int(Y.px(4.0)) + 6, int(Y.px(3.7)))
    r0 = (rs[0][0] + rs[0][1] - 1) / 2.0
    # line width: the median thickness of the dashes between 5 and 40 %
    th = [b - a for c in range(int(X.px(5.0)), int(X.px(40.0)), 3)
          for a, b in fl.runs(d[:, c], int(Y.px(4.0)) + 6, int(Y.px(3.7)))]
    w = int(np.median(th))
    tr = fl.trace(d, c0, r0, int(X.px(97.0)), r_lo, r_hi, max_jump=8, width=w, prefer=None, max_gap=80,
                  monotone="down")  # the dashed line only falls; the label pointer rises to the right
    return tr, w


def read_curve(image, at, which):
    d = fl.dark(image)
    fr, X, Y, cal = fl.calibrate(d, XV, YV)
    tr, w = (_solid if which == "solid" else _dashed)(d, fr, X, Y)
    return fl.read_trace(tr, w, at, cal)


def read_dots(image):
    """The dotted line: separate round dots above the solid line, each read at its centre."""
    d = fl.dark(image)
    fr, X, Y, cal = fl.calibrate(d, XV, YV)
    tr, w = _solid(d, fr, X, Y)
    m = d.copy()
    m[:, : int(X.px(55.0))] = False
    m[:, int(X.px(99.0)):] = False
    m[: int(Y.px(1.15)), :] = False
    m[int(Y.px(0.5)):, :] = False
    # remove the solid line, with a margin of two pixels
    for c, (r, _thick) in tr.items():
        m[int(r - w / 2 - 2): int(r + w / 2 + 3), c] = False
    lab, n = ndimage.label(m)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        blob = lab[sl] == i + 1
        area = int(blob.sum())
        h, wd = blob.shape
        if area < 40 or h > 3 * w or wd > 3 * w or h < 0.6 * w:
            continue
        if not 0.7 <= h / wd <= 1.4:  # dots are round; the dashes of the steep dashed line are not
            continue
        rr, cc = np.nonzero(blob)
        r = sl[0].start + rr.mean()
        c = sl[1].start + cc.mean()
        if abs(cal.yval(c, r) - 1.0) > 0.1:  # the dotted line runs along Q/Qn = 1
            continue
        half = 0.5 * h + Y.misfit_px
        x = round(X.val(cal.cs(c, r)), 2)
        out.append(fl.reading(x, r, c, half, cal, f"dot of {area} px; {cal.note()}"))
    out.sort(key=lambda o: o["x"])
    return out
