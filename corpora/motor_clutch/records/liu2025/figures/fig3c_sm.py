"""Fig. 3(c) (PDF p. 8): the green points, best-fitting myosin II density sigma_m of the talin WT
model against fibronectin concentration (second right-hand axis, linear, um^-2). Method as
fig3c_kon (loaded from it), on the green axis.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_fig3ck", Path(__file__).with_name("fig3c_kon.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.AXES["green"]


def read(image, at):
    return B.read_series(image, "green", (20, 220, 20))
