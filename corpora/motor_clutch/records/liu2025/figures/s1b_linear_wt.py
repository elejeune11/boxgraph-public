"""Fig. S1(b) (PDF p. 49): the solid red curve, linear WT model, mean tension of an engaged
(talin-based) molecular clutch against E.

Calibration as s1b_linear_kd (loaded from it). Three red lines: the dash-dotted talin WT curve
(unfolded talin), which rises above 2 pN from about 7 kPa, the solid linear WT curve, and the
dotted talin WT curve (folded talin) below it. Only rows below the 1.7 pN level are searched and
the solid curve is the top red run there; positions where the dash-dotted line crosses it
(about 2-5 kPa) are not read.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_s1b", Path(__file__).with_name("s1b_linear_kd.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    cal = B.H.calibrate(image, SPEC)
    sp = cal["sp"]
    box = (sp["c1"] + 2, int(cal["y"].px(1.7)), sp["x_to"] + 3, sp["r0"] - 1)
    return B.H.curve(image, (230, 0, 0), 90, cal["x"], cal["y"], at, box, pick="top", exclude=B.LEGEND)
