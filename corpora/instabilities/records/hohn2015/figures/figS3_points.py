"""Fig. S3 (PDF p. 7): the coloured markers, one per embryo, percentage change of surface area
before expansion. The x axis carries no values: each marker's x is its rank when the markers are
sorted by value (1 = largest decrease). See _figS3.py for calibration and marker finding.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("hohn2015_figS3", Path(__file__).with_name("_figS3.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    m = _mod()
    cal, found = m.markers(image)
    pad = 1.0 + cal["misfit"]
    vals = sorted(found, key=lambda f: -f[0])  # lowest on the page (most negative) first
    out = []
    for k, (row, col, top, bot) in enumerate(vals, start=1):
        y = m.value(cal, row)
        a, b = m.value(cal, row - pad), m.value(cal, row + pad)
        out.append({"x": float(k), "y": y, "lo": min(a, b), "hi": max(a, b), "px": [col, row],
                    "px_lo": row - pad, "px_hi": row + pad,
                    "note": f"marker rows {top}-{bot}; calibration marks {len(cal['marks'])}, misfit {cal['misfit']:.2f} px"})
    return out
