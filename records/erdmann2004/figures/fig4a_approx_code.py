"""Fig. 4(a), the dotted curve T = ln[0.61(N0/f)]: every dash that stands clear of the solid lines (separate blobs of 300-4000 px, the topmost one cut by the frame margin, linked into a chain of two or more; a lone dash is not taken).

Calibration and tracing are in _axes.py (same folder); this file says which panel and
which curve.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("erdmann2004_axes", os.path.join(os.path.dirname(__file__), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def read(image, at):
    return A.read_dashes(image, "4a", "all", 300, 4000, allow_touch=True, min_chain=2)
