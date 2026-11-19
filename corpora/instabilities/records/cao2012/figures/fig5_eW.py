"""Fig. 5 (PDF p. 3): the single line, eW against lambda0_1s for mu_f/mu_s = 1.

Reading by the shared code in _cao.py (see its docstring for the calibration, the tracing and the
intervals). Tick labels matched: x 1 (frame), 2, 3, 4, 5, 6 (frame); y 0.3 (frame), 0.35, 0.4, 0.45, 0.5 (frame).
"""
import importlib.util
from pathlib import Path

SPEC = {'x': {'lo': 1, 'hi': 6, 'ticks': [2, 3, 4, 5]}, 'y': {'lo': 0.3, 'hi': 0.5, 'ticks': [0.35, 0.4, 0.45]}, 'seed': [2, 0]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("cao2012_cao", Path(__file__).with_name("_cao.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, SPEC)
