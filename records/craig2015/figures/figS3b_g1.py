"""Supplemental figure 3(b) (PDF p. 22): the green curve, gamma = 1 (legend).

Calibrated by _s3b.py (this panel has no top frame line; see its docstring), read by the kit's read_curve.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("craig2015_s3b", Path(__file__).with_name("_s3b.py"))
_s3b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_s3b)


def read(image, at):
    return _s3b.read_curve(image, at, color=(0, 128, 0))
