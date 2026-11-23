"""Fig. S1(a) (PDF p. 49): the solid red curve, linear WT model, density of engaged (talin-based)
molecular clutches against E.

Calibration as s1a_linear_kd (loaded from it). In the upper part of the panel two red lines run
side by side: the dotted talin WT curve (folded talin) above and the solid linear WT curve below;
the solid one is the lowest red run there (rows above the 10 tick; the dash-dotted unfolded-talin
curve lies far below).
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_s1a", Path(__file__).with_name("s1a_linear_kd.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    cal = B.H.calibrate(image, SPEC)
    sp = cal["sp"]
    ten = cal["y"].px(10.0)
    box = (sp["c1"] + 2, 0, sp["x_to"] + 3, int(ten))
    return B.H.curve(image, (230, 0, 0), 90, cal["x"], cal["y"], at, box, pick="bottom", exclude=B.LEGEND)
