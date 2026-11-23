"""Fig. 5(c) (PDF p. 13): the blue curve, the 2nd saddle-node point of the linear KD model, read as
myosin density sigma_m at given Young's moduli E. Method and calibration as fig5c_sn1 (loaded
from it), with the blue colour.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_fig5c1", Path(__file__).with_name("fig5c_sn1.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    return B.read_rows(image, at, (20, 20, 235), 90)
