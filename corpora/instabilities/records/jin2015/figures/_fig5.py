# Fig. 5(a)-(f) (p. 5) of jin2015: normalized energy U/U0 against strain for points A-F. The
# minimal critical strain e_m of the wrinkle analysis is marked on the strain axis: by a small
# green diamond on the flat line in (a), (b); by the left end of the green wrinkle branch, where
# the label e_m stands, in (c)-(e); by where the green wrinkle branch leaves the flat line in (f).
# The value read is the strain (horizontal axis), calibrated from the panel's own ticks on the
# bottom and top edges (linear; the labels seen under the ticks are given below). The x of the
# returned reading is the panel's Gf/Gs, passed in `at` (the panel prints it: "Point A, Gf/Gs=1.4").
import importlib.util
import pathlib

import numpy as np

_spec = importlib.util.spec_from_file_location("jin_helpers", pathlib.Path(__file__).resolve().parent / "_jin.py")
J = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(J)

# strain labels under the interior ticks, left to right, as printed on each panel
TICKS = {
    "a": [0.25, 0.3, 0.35, 0.4, 0.45],
    "b": [0.34, 0.35, 0.36, 0.37, 0.38, 0.39],
    "c": [0.26, 0.28, 0.3, 0.32, 0.34, 0.36],
    "d": [0.23, 0.235, 0.24, 0.245],
    "e": [0.205, 0.21, 0.215, 0.22, 0.225, 0.23],
    "f": [0.1, 0.15, 0.2, 0.25, 0.3, 0.35],
}


def calibrate(image, panel):
    box, half = J.frame(image)
    tk = J.merge_ticks(J.ticks(image, box, half, "bottom"), J.ticks(image, box, half, "top"))
    return box, half, J.lin_axis_from_ticks(tk, TICKS[panel])


def _components(mask):
    from scipy.ndimage import label
    lab, n = label(mask)
    return [np.nonzero(lab == i) for i in range(1, n + 1)]


def _flat_row(image, box):
    """Row of the red flat line (U/U0 = 1): the row with most red pixels."""
    red = J.hue_mask(image, "red")
    c0, r0, c1, r1 = [int(v) for v in box]
    counts = red[r0:r1, c0:c1].sum(axis=1)
    rows = np.nonzero(counts > 0.5 * counts.max())[0]
    return r0 + float(rows.mean()), (rows.max() - rows.min() + 1) / 2.0


def read(image, at, panel):
    box, half, xax = calibrate(image, panel)
    c0, r0, c1, r1 = box
    green = J.hue_mask(image, "green")
    green[:, :int(c0 + half + 2)] = False
    green[:, int(c1 - half - 1):] = False
    green[:int(r0 + half + 2), :] = False
    green[int(r1 - half - 1):, :] = False
    flat, fh = _flat_row(image, box)
    cal = f"strain axis from {xax.n} ticks, misfit {xax.misfit_px:.1f} px; "
    comps = [c for c in _components(green) if len(c[0]) >= 30]
    if not comps:
        return [{"x": at[0], "y": None, "note": "no green mark found"}]
    if panel in ("a", "b"):  # the diamond: the green blob on the flat line
        rows, cols = min(comps, key=lambda c: abs(c[0].mean() - flat))
        col, row = float(cols.mean()), float(rows.mean())
        w = (cols.max() - cols.min() + 1) / 4.0 + xax.misfit_px + 1.0  # a quarter of the marker width
        how = f"centre of the green diamond ({cols.max() - cols.min() + 1} px wide)"
    else:
        rows, cols = max(comps, key=lambda c: len(c[0]))  # the wrinkle branch
        if panel != "f":  # its left end
            left = cols.min()
            sel = cols <= left + 3
            col, row = float(left), float(rows[sel].mean())
            w = 3.0 + xax.misfit_px + 1.0
            how = "left end of the green wrinkle branch"
        else:  # where it leaves the flat line. The red flat line is drawn over the green branch, whose
            # lower edge shows below it: take the centre of the visible green in each column, its
            # baseline over the left third of the box, and find where it drops away from that baseline
            ys, xs = np.nonzero(green)
            centre = {int(c): float(ys[xs == c].mean()) for c in np.unique(xs)}
            cs = sorted(centre)
            left = [centre[c] for c in cs if c < c0 + (c1 - c0) / 3.0]
            base = float(np.median(left))
            th = 2 * fh  # one thickness of the flat line
            off = [c for c in cs if centre[c] - base > th]
            on = [c for c in cs if abs(centre[c] - base) <= 1.5 and (not off or c < off[0])]
            if not off or not on:
                return [{"x": at[0], "y": None, "note": "departure of the green branch not found"}]
            c_on, c_off = on[-1], off[0]
            col, row = (c_on + c_off) / 2.0, base
            w = (c_off - c_on) / 2.0 + xax.misfit_px + 1.0
            how = (f"where the green wrinkle branch leaves the flat line: last column within 1.5 px of its "
                   f"baseline ({c_on}) to first column {th:.0f} px (a line thickness) below it ({c_off})")
    v, lo, hi = xax.to_val(col), xax.to_val(col - w), xax.to_val(col + w)
    return [{"x": at[0], "y": v, "lo": min(lo, hi), "hi": max(lo, hi), "px": [col, row], "note": cal + how}]
