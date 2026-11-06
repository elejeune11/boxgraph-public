"""Fig. 6D-E of gong2018 (PDF p. 8): cell spreading area on elastic (grey) and
viscoelastic (red) alginate substrates at initial moduli 1.4, 3.4 and 9 kPa;
D: experiments (mean +/- SD, error bars), E: model predictions (bars only).
Read by _bars.py (see its docstring): y from the outward ticks of the y axis
(0 to 2,000 um^2 in D; 0 to 1,500 in E); x from the category labels.
"""
import importlib.util
from pathlib import Path

CATS = [1.4, 3.4, 9]
PANELS = {
    "d": {"y_labels": [2000, 1500, 1000, 500, 0], "ticks": "out", "tick_len": 60, "axis_max_col": 1100,
          "categories": CATS, "bars": True, "gap": 4, "contrast": 15, "line_w": 8, "src_px": 8},
    "e": {"y_labels": [1500, 1000, 500, 0], "ticks": "out", "tick_len": 60, "axis_max_col": 1100,
          "categories": CATS, "src_px": 8},
}
COLORS = {"grey": {"color": [81, 81, 81], "tol": 14}, "red": {"color": [236, 57, 57], "tol": 50},
          # Fig. 6E: grey bars a little darker, viscoelastic bars a darker red
          "grey_e": {"color": [64, 64, 64], "tol": 20}, "red_e": {"color": [192, 0, 0], "tol": 60}}


def read(image, panel, color):
    spec = importlib.util.spec_from_file_location("gong2018_bars", Path(__file__).with_name("_bars.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_bars(image, {**PANELS[panel], **COLORS[color]})
