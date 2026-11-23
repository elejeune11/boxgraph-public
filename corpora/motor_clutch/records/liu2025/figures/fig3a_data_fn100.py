"""Fig. 3(a) (PDF p. 8): measured cell traction of MEF WT cells on 100 ug/ml fibronectin (green
upward triangles), data of ref. 13. Calibration and method as fig3a_data_fn10 (loaded from it).
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_fig3a10", Path(__file__).with_name("fig3a_data_fn10.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    return B.read_kind(image, "up")
