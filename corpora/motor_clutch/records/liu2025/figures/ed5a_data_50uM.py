"""Extended Data Fig. 5(a) (PDF p. 70): measured cell traction of MEF Talin 1 KO, Talin 2 shRNA
cells with 50 uM blebbistatin (light-blue downward triangles), data of ref. 13.

Calibration, exclusions and method as ed5a_data_0uM (loaded from it); light-blue fill, distinct
from the dark-blue model curve.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_ed5a0", Path(__file__).with_name("ed5a_data_0uM.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    return B.H.read_symbols(image, B.SPEC, (133, 210, 250), 45, "down", exclude=B.EXCLUDE, **B.KW)
