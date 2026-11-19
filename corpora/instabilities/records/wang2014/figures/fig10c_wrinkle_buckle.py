"""Fig. 10(c) (PDF p. 7): the blue line, critical strain for delaminated buckling from the wrinkled
state against Gamma/(mu_s H_f), mu_f/mu_s = 10, lambda_p = 1 (finite-element result).

Reading by the shared code in _wang.py (calibration, tracing and intervals in its docstring).
Tick labels matched: x 0.6 (frame), 0.8, 1 (ticks inward from the bottom frame), 1.2 (frame);
y 0.1 (frame), 0.12 to 0.18, 0.2 (frame).
"""
import importlib.util
from pathlib import Path

SPEC = {"x": {"lo": 0.6, "hi": 1.2, "ticks": [0.8, 1.0]},
        "y": {"lo": 0.1, "hi": 0.2, "ticks": [0.12, 0.14, 0.16, 0.18]},
        "ink": "blue", "w": 20.0, "seed": [0.9, 0.15]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("wang2014_wang", Path(__file__).with_name("_wang.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, SPEC)
