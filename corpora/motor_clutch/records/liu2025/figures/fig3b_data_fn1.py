"""Fig. 3(b) (PDF p. 8): measured cell traction of MEF Talin 1 KO, Talin 2 shRNA cells on
1 ug/ml fibronectin (blue downward triangles), data of ref. 13. Calibration and method as
fig3b_data_fn10 (loaded from it).
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_fig3b10", Path(__file__).with_name("fig3b_data_fn10.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    return B.read_kind(image, "down")
