"""Calculated phase diagrams of the initial modes (PDF p. 5), x = Gamma/(mu_s H_f), y = mu_f/mu_s:
Fig. 6(b) (lambda_p = 1), Fig. 7(a) (lambda_p = 2, log x axis) and Fig. 7(b) (lambda_p = 3).
Red circles joined by a red line: the boundary between delaminated buckling and wrinkling; blue
squares joined by a blue line: the boundary between delaminated buckling and creasing
(finite-element results).

Calibration (shared code in _wang.py): the black frame; ticks inward from the bottom and left
frame lines matched to the printed labels, the frame lines at the end labels:
  6(b), 7(b): x 0.4, 0.8, 1.2, 1.6 (0 and 2 at the frame); y 3, 6, 9, 12 (0 and 15 at the frame);
  7(a): x decade ticks 10^-1, 10^0, 10^1 (minor ticks dropped by length; 10^2 at the right
  frame); y 3, 6, 9, 12 (0 and 15 at the frame); the legend box is blanked.
Markers by read_hollow_markers in _wang.py (filled, opened, distance peaks); r_open, r_min and
sep are set from the marker sizes of each panel (blue squares in 7(a) and 7(b) are smaller).
"""
import importlib.util
from pathlib import Path

LIN = {"x": {"lo": 0, "hi": 2, "ticks": [0.4, 0.8, 1.2, 1.6]},
       "y": {"lo": 0, "hi": 15, "ticks": [3, 6, 9, 12]}}
LOG = {"x": {"hi": 100, "ticks": [0.1, 1, 10], "major_len": 20, "log": True},
       "y": {"lo": 0, "hi": 15, "ticks": [3, 6, 9, 12]}, "blank": [[1385, 150, 2685, 600]]}
PANELS = {
    ("6b", "red"): dict(LIN, ink="red", r_open=14, r_min=20, sep=24),
    ("6b", "blue"): dict(LIN, ink="blue", r_open=12, r_min=16, sep=20),
    ("7a", "blue"): dict(LOG, ink="blue", r_open=9, r_min=13, sep=16),
    ("7b", "blue"): dict(LIN, ink="blue", r_open=9, r_min=13, sep=16),
}


def read(image, at, panel, colour):
    spec = importlib.util.spec_from_file_location("wang2014_wang", Path(__file__).with_name("_wang.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_hollow_markers(image, PANELS[(panel, colour)])
