"""Fig. 14(b) (PDF p. 9): critical strain for wrinkling against mu_f/mu_s (log axis), one curve per prestretch.

Reading by the shared code in _wang.py (calibration, tracing, intervals in its docstring).
Tick labels matched: x 10^0 (frame), 10^1 (the one long tick inward from the bottom frame; the
shorter minor ticks are dropped by length), 10^2 (frame); y 0 (frame), 0.1 to 0.4, 0.5 (frame).
Curves by colour: solid red lambda_p = 1, dashed blue 1.5, crosses on a magenta line 3 (orange
dotted 2 and green dash-dot 2.5 are interleaved with each other and with the others, and are not read).
"""
import importlib.util
from pathlib import Path

BASE = {"x": {"lo": 1, "hi": 100, "ticks": [10], "major_len": 20, "log": True},
        "y": {"lo": 0, "hi": 0.5, "ticks": [0.1, 0.2, 0.3, 0.4]}}


def _shared():
    spec = importlib.util.spec_from_file_location("wang2014_wang", Path(__file__).with_name("_wang.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(image, at, **curve):
    return _shared().read_curve(image, at, dict(BASE, **curve))
