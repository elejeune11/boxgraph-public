"""Fig. 4(c) (PDF p. 10): measured cell traction of vinculin-KO MEF cells (green left-pointing
triangle), data of refs. 13, 21. Calibration and method as fig4c_data_vd1 (loaded from it); the
position of a left-pointing triangle is its fill's centroid.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_fig4cv", Path(__file__).with_name("fig4c_data_vd1.py"))
B = importlib.util.module_from_spec(_s)
_s.loader.exec_module(B)
SPEC = B.SPEC


def read(image, at):
    return B.H.read_symbols(image, SPEC, (70, 215, 70), 60, "left", exclude=B.EXCLUDE, mode="fill", min_area=40)
