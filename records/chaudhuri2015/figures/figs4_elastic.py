"""Supp. Fig. 4, grey bars (elastic): 3T3 cell spreading area for 150 and 1500 uM RGD at 1.4 kPa and 150 and 1500 uM RGD at 3.4 kPa (indices 1-4). The panel is an embedded bitmap.
Fill colour sampled from the crop; y tick values listed bottom to top (labelled or not).
See _kit.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)

FILL, TOL = (76, 68, 68), 22
TICKS = [0, 500, 1000, 1500]


def read(image, at):
    out, _ = K.bar_series(image, FILL, TOL, TICKS, ink_thr=55, ink_up_thr=140, cal_px=4.0)
    return out
