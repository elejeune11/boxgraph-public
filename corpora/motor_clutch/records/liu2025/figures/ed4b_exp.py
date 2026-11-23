"""Extended Data Fig. 4(b) (PDF p. 68): measured retrograde actin flow on DOPC, DPPC and glass
substrates (bars 1-3 under 'Experiment': magenta, blue, green; data of ref. 73, mean +- SD),
with their error bars. Method and calibration as ed4b_maxwell (loaded from it); only the columns
right of the second dashed separator are searched. x is the bar's position (1 DOPC, 2 DPPC,
3 glass).
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_ed4bm", Path(__file__).with_name("ed4b_maxwell.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    # the error bars over the dark-blue bar blend with it in this coarse raster: dark of any hue
    return B.read_part(image, (0.66, 1.0), B.EXP, [1, 2, 3], 125, err=True, smax=140, thr=100)
