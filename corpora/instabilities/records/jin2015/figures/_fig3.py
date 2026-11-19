# Fig. 3 (p. 3), and the boundary curves of Figs. 4(a) and 5(g), of jin2015: black contour lines
# in the (Hs/Hf, Gf/Gs) plane, log-log. Axes are calibrated from the panel's own ticks (long
# ticks at the decades labelled on the panel, minor ticks matched to k*10^n). A contour is picked
# by its order from the bottom (0 = lowest) among the black lines crossing a clean column
# (`seed_x`, away from the labels), followed column by column from there, and read at `at`.
import importlib.util
import pathlib

import numpy as np

_spec = importlib.util.spec_from_file_location("jin_helpers", pathlib.Path(__file__).resolve().parent / "_jin.py")
J = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(J)

# per panel: frame/tick darkness threshold, x decade labels and range, y decade labels and range,
# and the sides that carry ticks for x and y
PANELS = {
    "3a": {"thr": 130, "x": ([0.1, 1.0, 10.0, 100.0], -2, 3), "y": ([100.0, 10.0], 0, 3)},
    "3b": {"thr": 130, "line_thr": 170, "x": ([0.1, 1.0, 10.0, 100.0], -2, 3), "y": ([100.0, 10.0], 0, 3)},
    # Fig. 4(a): the y axis has ticks only at its labels 40, 20, 10, 7, 5, 3 (top to bottom)
    "4a": {"thr": 130, "x": ([0.1, 1.0, 10.0], -2, 2), "y_labels": [40.0, 20.0, 10.0, 7.0, 5.0, 3.0]},
    "5g": {"thr": 130, "x": ([0.1, 1.0, 10.0], -2, 2), "y": ([10.0], 0, 2)},
}


def _ticks(image, box, half, a, b, thr):
    ta, tb = J.ticks(image, box, half, a, thr=thr), J.ticks(image, box, half, b, thr=thr)
    if ta and tb:
        m = J.merge_ticks(ta, tb)
        if len(m) >= 4:
            return m
    return ta if len(ta) >= len(tb) else tb


def calibrate(image, panel):
    cfg = PANELS[panel]
    box, half = J.frame(image, thr=cfg["thr"])
    xt = _ticks(image, box, half, "bottom", "top", cfg["thr"])
    yt = _ticks(image, box, half, "left", "right", cfg["thr"])
    if "y_labels" in cfg:
        pos = sorted(p for p, _ in yt)
        if len(pos) != len(cfg["y_labels"]):
            raise ValueError(f"found {len(pos)} y ticks at {pos}, expected {len(cfg['y_labels'])}")
        yax = J.Axis(pos, cfg["y_labels"], True)
    else:
        yax = J.log_axis(yt, *cfg["y"])
    return box, half, J.log_axis(xt, *cfg["x"]), yax


def black(image, box, half, inset=24, thr=100):
    m = J.dark(image, thr)
    c0, r0, c1, r1 = [int(round(v)) for v in box]
    h = int(half) + inset
    m[:, :c0 + h] = False
    m[:, c1 - h:] = False
    m[:r0 + h, :] = False
    m[r1 - h:, :] = False
    return m


def read_contour(image, at, panel, seed_x, order, mask=None, max_jump=14):
    box, half, xax, yax = calibrate(image, panel)
    m = black(image, box, half, thr=PANELS[panel].get("line_thr", 100)) if mask is None else mask(image, box, half)
    c0, r0, c1, r1 = box
    margin = int(half) + 24
    col = xax.to_pix(seed_x)
    runs = J.curve_rows(m, col, r0 + margin, r1 - margin)
    runs = sorted(runs, key=lambda t: -t[0])  # bottom first
    if len(runs) <= order:
        return [{"x": x, "y": None, "note": f"only {len(runs)} lines at the seed column"} for x in at]
    seed_row = runs[order][0]
    from scipy.ndimage import label
    lab, _ = label(m, structure=np.ones((3, 3)))
    k = lab[int(round(seed_row)), int(round(col))]
    line = lab == k  # the contour: the connected black line through the seed
    tag = (f"line {order} from the bottom at H_s/H_f = {seed_x:g} (its connected component); x axis from "
           f"{xax.n} ticks (misfit {xax.misfit_px:.1f} px), y axis from {yax.n} ticks (misfit {yax.misfit_px:.1f} px);")

    def span(c, w=2):
        rows = np.nonzero(line[:, max(int(round(c)) - w, 0):int(round(c)) + w + 1].any(axis=1))[0]
        return (float(rows.min()), float(rows.max())) if len(rows) else None

    out = []
    for x in at:
        c = xax.to_pix(x)
        s = span(c)
        if s is None:
            out.append({"x": x, "y": None, "note": f"{tag} the line does not reach this x"})
            continue
        a, b = span(c - 12), span(c + 12)
        slope = abs(((a[0] + a[1]) - (b[0] + b[1])) / 2.0 / 24.0) if a and b else 0.0
        row = (s[0] + s[1]) / 2.0
        h = (s[1] - s[0]) / 2.0
        w = h + yax.misfit_px + slope * xax.misfit_px + 1.0
        lo, hi = yax.to_val(row + w), yax.to_val(row - w)
        out.append({"x": x, "y": yax.to_val(row), "lo": min(lo, hi), "hi": max(lo, hi), "px": [c, row],
                    "px_lo": row - w, "px_hi": row + w,
                    "note": f"{tag} line spans {s[1] - s[0] + 1:.0f} px in this column (5 px wide)"})
    return out
