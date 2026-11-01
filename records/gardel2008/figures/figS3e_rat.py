"""Fig. S3 E (PDF p. 10): correlation coefficient r_AT of the high F-actin speed data
(v_ACT > v0) against the threshold v0, one blue square per v0.

Matched labels: x 5, 10, ..., 25 on the long ticks (0 and 30 at the frame edges where they lie
on the tick grid); y -0.4, -0.2, 0.0, 0.2, 0.4 on the long ticks (0.4 under the topmost), short
ticks halfway. The ticks are grey. Squares chain where v0 steps are small; see _dots.py.
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("gardel_dots", Path(__file__).with_name("_dots.py"))
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)


def read(image, at):
    mask = D.L.hue_mask(image, "blue", min_sat=60)
    return D.read_markers(image, mask, (0.0, 30.0), 5.0, (0.0, 0.0), 0.2, what="blue square", shape="square",
                          y_first_major=0.4, tick_level=180, open_r=8)
