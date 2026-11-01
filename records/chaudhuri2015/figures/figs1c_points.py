"""Supp. Fig. 1c: mean 1-s spreading velocity against simulation time step, the blue points
(asterisks with error bars; a few points are drawn as 'x'). The panel is an embedded bitmap
with a box frame and inward ticks.

- x axis (log10): the long (decade) ticks rising from the bottom frame line, 10^-4 ... 10^-1
  (the 10^-5 and 10^0 decades fall on the frame corners); the short minor ticks are dropped.
- y axis: the ticks pointing right from the left frame line, every 5 from 5 to 40 (0 and 45
  fall on the frame corners).
- points: blue pixels, closed so an asterisk and its error bar form one blob. A blob's centre
  is the point; its vertical extent (the error bar, or the asterisk where the bar is shorter)
  is reported as the error bar. Two points closer than a marker width merge into one blob; such
  blobs are reported with their full extent as the interval and say so.
"""
import importlib.util
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

BLUE = (76, 76, 140)


def read(image, at):
    ink = K.dark(image, 70)
    yl, xl = K.frame(ink)
    t = K.ticks_x(ink, (xl[0], xl[1]), (xl[2] - 15, xl[3] + 15), side="above", min_len=10, max_len=120)
    longest = max(n for _, n in t)
    cols = sorted(p for p, n in t if n >= 0.75 * longest and xl[2] + 20 < p < xl[3] - 20)
    xax = K.Axis(cols, [1e-4, 1e-3, 1e-2, 1e-1], log=True, what=f"decade ticks {cols}")
    ty = K.ticks_y(ink, (yl[0], yl[1]), (yl[2] - 15, yl[3] + 15), side="right", min_len=10, max_len=120)
    rows = sorted([p for p, n in ty if yl[2] + 20 < p < yl[3] - 20], reverse=True)
    yax = K.Axis(rows, [5, 10, 15, 20, 25, 30, 35, 40], what=f"y ticks {rows}")
    m = K.near(image, BLUE, 70)
    # only the inside of the box frame (its lines and minor ticks are dark and bluish in the bitmap)
    H, W = ink.shape
    top = min(h[0] for h in K.hlines(ink, int(0.5 * W)))
    right = max(v[1] for v in K.vlines(ink, int(0.5 * H)))
    keep = np.zeros_like(m)
    keep[top + 30: xl[0] - 30, yl[1] + 30: right - 30] = True
    m &= keep
    m = ndi.binary_closing(m, structure=np.ones((9, 9), bool))
    lab, n = ndi.label(m)
    objs = [(sl, int((lab[sl] == i + 1).sum())) for i, sl in enumerate(ndi.find_objects(lab))]
    objs = [(sl, a) for sl, a in objs if a >= 150]
    widths = [sl[1].stop - sl[1].start for sl, _ in objs]
    wmed = float(np.median(widths))
    out = []
    for sl, a in sorted(objs, key=lambda o: o[0][1].start):
        c0, c1 = sl[1].start, sl[1].stop - 1
        r0, r1 = sl[0].start, sl[0].stop - 1
        col = (c0 + c1) / 2.0
        blob = lab[sl] > 0
        # the point's row: centre of the widest rows (the asterisk), not of the whole bar
        wid = blob.sum(axis=1)
        core = np.nonzero(wid >= 0.6 * wid.max())[0]
        row = r0 + (core.min() + core.max()) / 2.0
        m_px = 4.0 + yax.misfit
        y = float(yax.to_val(row))
        merged = (c1 - c0 + 1) > 1.6 * wmed
        if merged:
            lo, hi = float(yax.to_val(r1 + m_px)), float(yax.to_val(r0 - m_px))
            note = "two or more points merged in one blob: the interval is the blob's full height"
        else:
            lo, hi = float(yax.to_val(row + (core.max() - core.min()) / 2 + m_px)), \
                float(yax.to_val(row - (core.max() - core.min()) / 2 - m_px))
            note = "centre of the asterisk; interval its half-height plus bitmap and calibration"
        r = {"x": float(xax.to_val(col)), "y": y, "lo": min(lo, y), "hi": max(hi, y), "px": [col, row],
             "px_lo": row + m_px, "px_hi": row - m_px,
             "note": note + f"; y misfit {yax.misfit:.1f} px, x misfit {xax.misfit:.1f} px"}
        if not merged:
            r.update({"bar_lo": float(yax.to_val(r1)), "bar_hi": float(yax.to_val(r0)),
                      "bar_lo_outer": float(yax.to_val(r1 + m_px)), "bar_hi_outer": float(yax.to_val(r0 - m_px)),
                      "px_bar": [col, r0, r1]})
        out.append(r)
    return out
