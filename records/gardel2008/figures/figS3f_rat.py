"""Fig. S3 F (PDF p. 10): correlation coefficient r_AT of the low F-actin speed data
(v_ACT < v0) against the threshold v0, one red triangle per v0.

Matched labels: x -5, 0, 5, ..., 45 (-5 and 45 at the frame edges where they lie on the tick
grid), long ticks every 5, short ticks halfway; y -0.4 ... 0.4 on the long ticks (0.4 under the
topmost), short ticks halfway. The ticks are grey. The triangle's centre is taken as the centre
of the largest disk inside it (its incentre); see _dots.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_dots", Path(__file__).with_name("_dots.py"))
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)


def read(image, at):
    mask = D.L.hue_mask(image, "red", min_sat=60)
    return D.read_markers(image, mask, (-5.0, 45.0), 5.0, (0.0, 0.0), 0.2, what="red triangle",
                          shape="triangle", y_first_major=0.4, tick_level=180, open_r=8, margin=3)
