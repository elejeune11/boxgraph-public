"""Fig. 2(c) (PDF p. 5): the solid green curve, linear KD model, cell traction P against E.

Read by the shared code in _fig.py. x: log axis; the major ticks below the left segment of the
broken axis are the decades 10^2 (at the spine) to 10^6, labelled 10^2, 10^4, 10^6 on every
other one; the lone labelled tick right of the break is 10^11 (read only at that tick).
y: labelled ticks 0, 60, 120, 180.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("liu2025_fig", Path(__file__).with_name("_fig.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)

SPEC = {
    "x": {"scale": "log10", "region": (14, 148), "marks": [(0, 1e2), (2, 1e4), (4, 1e6)]},
    "y": {"marks": [(0, 0), (1, 60), (2, 120), (3, 180)]},
    "rgb": ((0, 170, 0), (90, 255, 90)),
    "pick": "top",
    "blank": [(20, 0, 70, 50), (115, 60, 220, 125)],  # the two legends (crop pixels: c0, r0, c1, r1)
}


def _col_1e11(cal, img):
    m = F.dark(img)
    runs = F._ticks_x(m, cal["sp"], (190, img.shape[1]))
    maj = F._majors(runs, 0.75)
    return max(maj)


def read(image, at):
    spec = dict(SPEC)
    spec["x_at_col"] = {1e11: lambda cal: _col_1e11(cal, image)}
    return F.read_curve(image, spec, at)


def debug(image):
    cal = F.calibrate(image, SPEC)
    return {"sp": cal["sp"], "xt": cal["xt"], "yt": cal["yt"], "xmis": cal["x"]["misfit"], "ymis": cal["y"]["misfit"],
            "col_1e11": _col_1e11(cal, image)}
