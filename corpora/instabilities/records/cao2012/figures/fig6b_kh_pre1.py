"""Fig. 6 (right) (PDF p. 4): the kh line for lambda0_1s = 1 (lowest line from the bottom at mu_f/mu_s = 4.7).

Reading by the shared code in _cao.py (see its docstring for the calibration, the tracing and the
intervals). Tick labels matched: x 1 (frame), 2, 3, 4, 5 (frame); y 0.5 (frame), 0.6-0.9, 1 (frame).
"""
import importlib.util
from pathlib import Path

SPEC = {'x': {'lo': 1, 'hi': 5, 'ticks': [2, 3, 4]}, 'y': {'lo': 0.5, 'hi': 1, 'ticks': [0.6, 0.7, 0.8, 0.9]}, 'seed': [4.7, 0], 'blank': [[1560, 600, 3000, 800]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("cao2012_cao", Path(__file__).with_name("_cao.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, SPEC)
