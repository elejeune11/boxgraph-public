"""Figs. 8 and 9 (PDF p. 18): four coloured curves per panel, gamma = 0.25 (blue, dotted), 0.5 (green,
dashed), 0.75 (red, dash-dotted) and 1.0 (cyan, solid), as the caption gives the line styles; the
colours are those of the PDF.

Calibration (_common.calibrate): the tick labels left of and under the box, matched to the printed
values; panels (b) and (c) of Fig. 8 and both panels of Fig. 9 print a common factor (x 10^4 or
x 10^5) above the axis, which is applied to the label values.

The curves are drawn as straight segments between computed points (kinks at xi = 2.4, 2.6, 2.8).
At each x, a straight line is fitted through the curve's colour pixels on each side (columns
c-W .. c-4 and c+4 .. c+W), so a kink at c gives its vertex and gaps between dashes or dots do not
matter; both fits are evaluated at c. The value is their mean; the interval spans both, widened by
the line's half thickness, the x misfit times the local slope, the y misfit and 2 px. Near the frame only the inner side is used.
"""
import importlib.util
import os

import numpy as np

_spec = importlib.util.spec_from_file_location("_common", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_common.py"))
c_ = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(c_)

COLORS = {"blue": (0, 0, 255), "green": (25, 205, 25), "red": (250, 0, 0), "cyan": (0, 185, 185)}

PANELS = {
    # x labels left to right, y labels top to bottom (times the printed factor), dpi of the crop
    "8a": dict(x=[2.4, 2.6, 2.8, 3.0], y=[1.25, 1.20, 1.15, 1.10, 1.05], dpi=1800),
    "8b": dict(x=[2.4, 2.6, 2.8, 3.0], y=[2.0e5, 1.5e5, 1.0e5, 0.5e5, 0.0], dpi=1800),
    "8c": dict(x=[1.05, 1.10, 1.15, 1.20, 1.25], y=[3.0e5, 2.0e5, 1.0e5, 0.0], dpi=1800),
    "9a": dict(x=[2.4, 2.6, 2.8, 3.0], y=[8.0e4, 6.0e4, 4.0e4, 2.0e4, 0.0], dpi=1200),
    "9b": dict(x=[1.05, 1.10, 1.15, 1.20, 1.25], y=[2.0e5, 1.5e5, 1.0e5, 0.5e5, 0.0], dpi=1200),
}


def calibrate(image, panel):
    p = PANELS[panel]
    s = p["dpi"] / 1800.0
    return c_.calibrate(image, p["x"], p["y"], x_gap=40 * s, x_height=260 * s, x_merge=80 * s,
                        y_gap=25 * s, y_width=420 * s, margin=75 * s)


def _side_fit(mask, c0, c1):
    cs, rs = [], []
    for cc in range(c0, c1 + 1):
        rr = np.where(mask[:, cc])[0]
        cs += [cc] * len(rr)
        rs += list(rr)
    if len(set(cs)) < 6:
        return None
    cs, rs = np.asarray(cs, float), np.asarray(rs, float)
    k, m = np.polyfit(cs, rs, 1)
    res = rs - (k * cs + m)
    return k, m, 0.5 * (np.percentile(res, 98) - np.percentile(res, 2)), float(np.ptp(res))


def read(image, at, panel, color, half_window=None):
    cal = calibrate(image, panel)
    s = PANELS[panel]["dpi"] / 1800.0
    W = int(half_window or 160 * s)
    inset = int(12 * s) + 2
    mask = c_.inside(cal, c_.color_mask(image, COLORS[color], 90), inset)
    left, right = int(cal["left"]) + inset, int(cal["right"]) - inset
    out = []
    for x in at:
        c = cal["col_of"](x)
        ci = int(round(c))
        fits = []
        if ci - W >= left:
            fits.append(("left", _side_fit(mask, ci - W, ci - 4)))
        if ci + W <= right:
            fits.append(("right", _side_fit(mask, ci + 4, ci + W)))
        if not fits:
            fits = [("left", _side_fit(mask, max(left, ci - W), ci - 4)), ("right", _side_fit(mask, ci + 4, min(right, ci + W)))]
        good = [(n, f) for n, f in fits if f is not None and f[3] < 12 * f[2] + 30]
        if not good:
            out.append({"x": x, "y": None, "note": f"no clean run of the {color} curve beside column {ci}"})
            continue
        rows = [f[0] * c + f[1] for _, f in good]
        thick = max(f[2] for _, f in good) + max(abs(f[0]) for _, f in good) * cal["xmis"]
        rc = float(np.mean(rows))
        lo, hi, plo, phi = c_.interval(cal, min(rows) - thick, max(rows) + thick)
        out.append({"x": x, "y": cal["val_of"](rc), "lo": lo, "hi": hi, "px": [c, rc], "px_lo": plo, "px_hi": phi,
                    "note": f"{'+'.join(n for n, _ in good)} fit(s) over {W} columns, rows {', '.join(f'{r:.1f}' for r in rows)}, "
                            f"half thickness {thick:.1f} px; " + c_.note(cal)})
    return out
