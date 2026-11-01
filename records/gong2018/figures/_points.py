"""Shared code for filled markers with vertical error bars in the figures of
gong2018.

For one series (one colour):
  1. mask the colour inside the plot box, away from the spines by `margin` px and
     outside excluded boxes (the legend);
  2. an opening by a disk of radius `open_r` (wider than the error bars and the
     line, narrower than the filled marker) keeps the markers; each blob of at
     least `min_area` px is a marker, at the centre of its bounding box (the
     plotted point of a MATLAB marker); `center_px` allows for a marker whose
     drawn centre is not its bounding-box centre (a triangle); with `x_from_bar`
     the column is instead that of the marker's own error bar;
  3. the error bar: in the unopened mask, the columns within `bar_half` px of the
     marker's centre; from the marker, the colour is followed up and down,
     bridging gaps of up to `gap` rows (another curve drawn across the bar); the
     last rows reached are the bar's ends (the outer edges of the caps).  The
     ends are taken at the middle of the cap, half the bar's line width
     inside the outer edge; `bar_lo_outer`/`bar_hi_outer` widen the bar by that
     line width, one source pixel and the calibration misfit.

x and y come from the calibration (_axes.py); `x_transform: pow10` turns an axis
printed as log10 of the quantity into the quantity.
Interval of the value (95%): one source pixel of the upsampled image, half a
pixel, the calibration misfit, plus `center_px`.
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi


def _load(name):
    spec = importlib.util.spec_from_file_location(f"gong2018{name}", Path(__file__).with_name(f"{name}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mask(image, color, tol):
    f = image.astype(float)
    return np.sqrt(((f - np.asarray(color, float)) ** 2).sum(axis=2)) <= tol


def _follow(prof, start, step, gap):
    """Last index reached from `start` moving by `step` through True, bridging gaps."""
    i, last, miss = start, start, 0
    while 0 <= i + step < len(prof):
        i += step
        if prof[i]:
            last, miss = i, 0
        else:
            miss += 1
            if miss > gap:
                break
    return last


def read_points(image, axes, s, exclude=(), calib=None):
    xa, ya, box = calib or _load("_axes").calibrate(image, axes)
    c0, r0, c1, r1 = (int(v) for v in box)
    m = mask(image, s["color"], s["tol"])
    keep = np.zeros_like(m)
    mg = s.get("margin", 4)
    keep[r0 + mg:r1 - mg, c0 + mg:c1 - mg] = True
    for ea, eb, ec, ed in exclude:
        keep[eb:ed, ea:ec] = False
    m &= keep
    r = s["open_r"]
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    mo = ndi.binary_opening(m, structure=np.hypot(yy, xx) <= r)
    lab, n = ndi.label(mo)
    src = s.get("src_px", 8)
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), start=1):
        if (lab[sl] == i).sum() < s["min_area"]:
            continue
        rows = np.nonzero((lab == i).any(axis=1))[0]
        cols = np.nonzero((lab == i).any(axis=0))[0]
        col = (cols.min() + cols.max() + 1) / 2
        row = (rows.min() + rows.max() + 1) / 2
        if s.get("x_from_bar"):
            # a marker not centred on its point (a triangle): the error bar marks the
            # point's column; it is the column, under the marker's span, with the most
            # colour in the band just above and below the marker
            band = np.r_[max(rows.min() - 60, 0):rows.min() - 4, rows.max() + 5:min(rows.max() + 61, m.shape[0])]
            counts = m[band][:, cols.min():cols.max() + 1].sum(axis=0)
            if counts.max() > 20:
                hits = np.nonzero(counts >= 0.6 * counts.max())[0]
                col = cols.min() + (hits.min() + hits.max() + 1) / 2
        e = src + 0.5 + s.get("center_px", 0)
        ey = e + max(ya.residual_px, 0.5)
        x = xa.to_value(col)
        if s.get("x_transform") == "pow10":
            x = 10.0 ** x
        lo, hi = sorted((ya.to_value(row + ey), ya.to_value(row - ey)))
        rec = {"x": x, "y": ya.to_value(row), "lo": lo, "hi": hi, "px": [col, row], "px_lo": row - ey,
               "px_hi": row + ey, "note": f"marker, bounding box rows {rows.min()}-{rows.max()}"}
        if s.get("bars"):
            h = s.get("bar_half", 3)
            prof = m[:, int(col) - h:int(col) + h + 1].any(axis=1)
            top = _follow(prof, int(rows.min()), -1, s.get("gap", 3))
            bot = _follow(prof, int(rows.max()), +1, s.get("gap", 3))
            w = s.get("bar_w", 6)
            if top >= rows.min() - 2 and bot <= rows.max() + 2:
                # no bar outside the marker: hidden in it, reported as at most the marker
                top, bot = rows.min(), rows.max() + 1
                rec["note"] += "; no error bar outside the marker (at most the marker)"
                t_mid, b_mid = float(top), float(bot)
            else:
                t_mid, b_mid = top + w / 2, bot + 1 - w / 2
                rec["note"] += f"; error bar rows {top}-{bot}"
            ew = w / 2 + src + max(ya.residual_px, 0.5)
            rec["bar_hi"] = ya.to_value(t_mid)
            rec["bar_lo"] = ya.to_value(b_mid)
            rec["bar_hi_outer"] = ya.to_value(t_mid - ew)
            rec["bar_lo_outer"] = ya.to_value(b_mid + ew)
        out.append(rec)
    return sorted(out, key=lambda p: p["x"])
