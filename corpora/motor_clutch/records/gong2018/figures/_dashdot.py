"""Shared code for the dash-dotted mean lines of Figs. 1D and 3C of gong2018.

A dash-dotted line marks the time average of a spreading-speed trace.  It is drawn
thinner than the solid traces of the same colour.  For one series:

  1. mask the series colour inside the plot box (minus the legend, given by box);
  2. remove the solid strokes: an opening with a vertical bar `thick_px` tall keeps
     only strokes at least that thick (the traces), which are then grown by
     `grow_px` and taken away;
  3. what is left, split into connected pieces, keeps the pieces that look like
     dashes or dots (no taller than `max_h` px, at least as wide as tall);
  4. a straight line row = a + b col fitted through the piece pixels (the lines
     are drawn very slightly tilted) gives the row at the middle of the line's
     extent; that row is the value.

The reading's x is the legend value of the series (typed in the stub, as matched
by colour to the legend), so the datum is indexed by the quantity the legend
names.  Axes: inward tick marks matched to the printed labels (_axes.py).
Interval: half the line's tilt over its extent, half its thickness, one source
pixel of the upsampled image, the calibration misfit and half a pixel.
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


def read_lines(image, axes, series, exclude, src_px=8):
    c = _load("_common")
    xa, ya, box = _load("_axes").calibrate(image, axes)
    c0, r0, c1, r1 = (int(v) for v in box)
    out = []
    for s in series:
        m = c._mask(image, s["color"], s["tol"])
        keep = np.zeros_like(m)
        # away from the spines and their tick marks
        mg = axes.get("margin", axes.get("tick_px", 16) + 4)
        keep[r0 + mg:r1 - mg, c0 + mg:c1 - mg] = True
        for ea, eb, ec, ed in exclude:
            keep[eb:ed, ea:ec] = False
        m &= keep
        if s.get("thick_px"):
            # the solid trace: of the series colour, or of `solid` when the mean line has its own
            sm = c._mask(image, s["solid"], s["tol"]) if s.get("solid") else m
            thick = ndi.binary_opening(sm, structure=np.ones((s["thick_px"], 1), bool))
            thick = ndi.binary_dilation(thick, iterations=s.get("grow_px", 3))
            m &= ~thick
        lab, n = ndi.label(m)
        sel = np.zeros_like(m)
        for i, sl in enumerate(ndi.find_objects(lab), start=1):
            h = sl[0].stop - sl[0].start
            w = sl[1].stop - sl[1].start
            if h <= s["max_h"] and w >= h and (lab[sl] == i).sum() >= s.get("min_area", 12):
                sel[sl] |= lab[sl] == i
        rows, cols = np.nonzero(sel)
        if len(rows) < 30:
            out.append({"x": s["x"], "y": None, "note": "no dash-dotted line found"})
            continue
        # the line is the row band holding most of the pieces' pixels: start from the
        # most common row, then fit and drop pixels far from the fit, twice
        hist = np.bincount(rows)
        r_mode = int(np.argmax(np.convolve(hist, np.ones(9), mode="same")))
        ok = np.abs(rows - r_mode) <= s["max_h"]
        rows, cols = rows[ok], cols[ok]
        for _ in range(2):
            b, a = np.polyfit(cols + 0.5, rows + 0.5, 1)
            ok = np.abs(rows + 0.5 - (a + b * (cols + 0.5))) <= s["max_h"] / 2 + 1
            rows, cols = rows[ok], cols[ok]
        sel = np.zeros_like(m)
        sel[rows, cols] = True
        b, a = np.polyfit(cols + 0.5, rows + 0.5, 1)
        ca, cb = cols.min() + 0.5, cols.max() + 0.5
        cm = (ca + cb) / 2
        row = a + b * cm
        # thickness of the line: rows per dash column, in the dashes
        thick_rows = np.median(sel[:, int(ca):int(cb) + 1].sum(axis=0)[sel[:, int(ca):int(cb) + 1].any(axis=0)])
        tilt = abs(b) * (cb - ca) / 2
        e = tilt + thick_rows / 2 + src_px + 0.5 + max(ya.residual_px, 0.5)
        lo, hi = sorted((ya.to_value(row + e), ya.to_value(row - e)))
        out.append({"x": s["x"], "y": ya.to_value(row), "lo": lo, "hi": hi, "px": [cm, row],
                    "px_lo": row - e, "px_hi": row + e,
                    "note": (f"{s['what']}: dash-dotted line over columns {ca:.0f}-{cb:.0f} "
                             f"(t = {xa.to_value(ca):.2f} to {xa.to_value(cb):.2f}), tilt {tilt:.1f} px each way")})
    return out
