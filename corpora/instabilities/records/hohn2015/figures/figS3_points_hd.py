"""Fig. S3 (PDF p. 7) at high resolution: the coloured markers, one per embryo, percentage change
of surface area before expansion; x is the marker's rank by value (1 = largest decrease).

Calibration and marker finding as in _figS3.py. At high resolution a marker partly covered by a
neighbouring marker shows a shorter coloured part than the others; its centre is then not the
middle of what is visible. The full marker height is the median height of the markers; for a
marker shorter than 90% of it, the centre lies between (top + half height) and (bottom - half
height), and the 95% interval spans both, widened by 1 px and the calibration misfit.
"""
import importlib.util
from pathlib import Path

import numpy as np


def _mod():
    spec = importlib.util.spec_from_file_location("hohn2015_figS3", Path(__file__).with_name("_figS3.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    m = _mod()
    cal, found = m.markers(image)
    full = float(np.median([bot - top for _, _, top, bot in found]))
    pad = 1.0 + cal["misfit"]
    vals = sorted(found, key=lambda f: -f[0])  # lowest on the page (most negative) first
    out = []
    for k, (row, col, top, bot) in enumerate(vals, start=1):
        note = f"marker rows {top}-{bot}"
        lo_px, hi_px = row - pad, row + pad
        if bot - top < 0.9 * full:
            c1, c2 = top + full / 2, bot - full / 2
            row = (c1 + c2) / 2
            lo_px, hi_px = min(c1, c2) - pad, max(c1, c2) + pad
            note += f" (partly covered: {bot - top} px of {full:.0f}; centre between rows {min(c1, c2):.1f} and {max(c1, c2):.1f})"
        y = m.value(cal, row)
        a, b = m.value(cal, lo_px), m.value(cal, hi_px)
        out.append({"x": float(k), "y": y, "lo": min(a, b), "hi": max(a, b), "px": [col, row],
                    "px_lo": lo_px, "px_hi": hi_px,
                    "note": f"{note}; calibration marks {len(cal['marks'])}, misfit {cal['misfit']:.2f} px"})
    return out
