"""Fig. 4(g) (PDF p. 10): the two yellow markers on the force-extension traces of talin with
vinculin VD1 bound (cycles 1-3, ref. 22), at 5 and 10 pN: the points from which the text takes
the ~110 nm extension difference. Method as fig4g_novd1 (loaded from it), above the 300 nm level.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_fig4gn", Path(__file__).with_name("fig4g_novd1.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    return B.read_part(image, False)
