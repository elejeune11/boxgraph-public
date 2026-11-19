"""Fig. 4 (PDF p. 3): the lowest line at mu_f/mu_s = 2 (leader '2').

Reading by the shared code in _cao.py (see its docstring for the calibration, the tracing and the
intervals). Tick labels matched: x 1 (frame), 2, 3, 4, 5 (frame); y 0 (frame), 0.1-0.4, 0.5 (frame).
"""
import importlib.util
from pathlib import Path

SPEC = {'x': {'lo': 1, 'hi': 5, 'ticks': [2, 3, 4]}, 'y': {'lo': 0, 'hi': 0.5, 'ticks': [0.1, 0.2, 0.3, 0.4]}, 'seed': [1.98, 0], 'blank': [[520, 2400, 2600, 2760]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("cao2012_cao", Path(__file__).with_name("_cao.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, SPEC)
