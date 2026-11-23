"""Fig. 3(c) (PDF p. 8): the red points, best-fitting adhesion-site radius r of the talin WT model
against fibronectin concentration (first right-hand axis, log, nm). Method as fig3c_kon (loaded
from it), on the red axis.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_fig3ck", Path(__file__).with_name("fig3c_kon.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.AXES["red"]


def read(image, at):
    return B.read_series(image, "red", (240, 20, 20))
