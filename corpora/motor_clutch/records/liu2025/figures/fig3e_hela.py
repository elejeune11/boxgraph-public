"""Fig. 3(e) (PDF p. 8): measured density of myosin II stacks in HeLa cells at 1, 10 and 100 ug/ml
fibronectin (the light-green boxes, mean +- s.e.m.; N = 11, 13, 16 cells). Method and
calibration as fig3e_nih3t3 (loaded from it), with the light-green fill.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_fig3en", Path(__file__).with_name("fig3e_nih3t3.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    # the green points' light anti-aliased rims match the fill: a box row must be mostly fill
    return B.read_kind(image, "hela", caps=False, min_frac=0.45)
