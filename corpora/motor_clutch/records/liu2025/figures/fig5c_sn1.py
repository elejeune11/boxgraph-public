"""Fig. 5(c) (PDF p. 13): the red curve, the 1st saddle-node point of the linear KD model, read as
myosin density sigma_m (horizontal axis) at given Young's moduli E (vertical axis).

Shared code in _hd.py for the axes. x (horizontal): linear, the long ticks 10, 20, 30, 40, 50
(labelled 10, 30, 50); y (vertical): log, the long decade ticks 10^4 ... 10^8 (labelled 10^4,
10^6, 10^8). The reading is indexed by E: at each E, the row of that E is taken and the red run
along it is the curve; its centre column is converted to sigma_m. The interval: half the run's
width (the line seen along a row, wider where the curve is not vertical), the x misfit, a pixel,
and the curve's horizontal shift across the y misfit.
"""
import importlib.util
import math
from pathlib import Path

import numpy as np

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"marks": [(0, 10), (2, 30), (4, 50)], "major": 0.8},
    "y": {"scale": "log10", "marks": [(0, 1e4), (2, 1e6), (4, 1e8)], "major": 0.8},
}
RGB, TOL = (235, 20, 20), 90


def read_rows(image, at, rgb, tol):
    cal = H.calibrate(image, SPEC)
    ax, ay, sp = cal["x"], cal["y"], cal["sp"]
    m = H.colour(image, rgb, tol)
    m[:, : sp["c1"] + 2] = False
    m[sp["r0"] - 1:, :] = False
    src = H.source_px(image)
    out = []
    for E in at:
        row = ay.px(E)
        r = int(math.floor(row))
        runs = H._groups(np.nonzero(m[r])[0]) if 0 <= r < m.shape[0] else []
        runs = [g for g in runs if len(g) >= 2]
        if not runs:
            out.append({"x": float(E), "y": None, "note": "no pixel of this colour on this row"})
            continue
        g = max(runs, key=len)
        a, b = float(g[0]), float(g[-1] + 1)
        cen = 0.5 * (a + b)
        near = []
        for rr in (r - 3, r + 3):
            gs = [q for q in H._groups(np.nonzero(m[rr])[0]) if len(q) >= 2] if 0 <= rr < m.shape[0] else []
            if gs:
                q = min(gs, key=lambda q: abs(0.5 * (q[0] + q[-1] + 1) - cen))
                near.append(0.5 * (q[0] + q[-1] + 1))
        slope = abs(near[-1] - near[0]) / 6.0 if len(near) == 2 else 0.0
        pad = 0.5 * (b - a) + ax.misfit + max(1.0, src) + slope * (ay.misfit + src)
        v1, v2 = ax.val(cen - pad), ax.val(cen + pad)
        out.append({"x": float(E), "y": float(ax.val(cen)), "lo": float(min(v1, v2)), "hi": float(max(v1, v2)),
                    "px": [float(cen), float(row)],
                    "note": f"run {b - a:.0f} px along the row; x misfit {ax.misfit:.1f} px ({ax.n} ticks), "
                            f"y misfit {ay.misfit:.1f} px ({ay.n} ticks)"})
    return out


def read(image, at):
    return read_rows(image, at, RGB, TOL)
