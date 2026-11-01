"""Fig. S5A and S5C of gong2018 (PDF p. 17): cell spreading area (axis in units of
10^4 um^2, the labels are multiplied by 1e4 to give um^2) on elastic (grey) and
viscoelastic (red) HA substrates at long-term moduli 0.3, 1 and 3.3 kPa.
A: experiments, mean +/- SD (caption); C: model predictions (bars only).
Read by _bars.py (see its docstring): y from the outward ticks of the y axis
(0 to 1); x from the category labels.  The legend squares are smaller than a bar
and are dropped by the bar size threshold.
"""
import importlib.util
from pathlib import Path

CATS = [0.3, 1, 3.3]
PANELS = {
    "a": {"y_labels": [1, 0.8, 0.6, 0.4, 0.2, 0], "y_mult": 1e4, "ticks": "out", "tick_len": 40,
          "axis_max_col": 900, "categories": CATS, "bars": True, "gap": 4, "contrast": 30, "line_w": 10,
          "src_px": 8},
    "c": {"y_labels": [1, 0.8, 0.6, 0.4, 0.2, 0], "y_mult": 1e4, "ticks": "out", "tick_len": 40,
          "axis_max_col": 900, "categories": CATS, "src_px": 8},
}
COLORS = {"grey": {"color": [90, 90, 90], "tol": 25}, "red": {"color": [192, 0, 0], "tol": 60},
          "grey_c": {"color": [64, 64, 64], "tol": 25}}


def read(image, panel, color):
    spec = importlib.util.spec_from_file_location("gong2018_bars", Path(__file__).with_name("_bars.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_bars(image, {**PANELS[panel], **COLORS[color]})
