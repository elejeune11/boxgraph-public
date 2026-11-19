"""Fig. 6 (left) (PDF p. 4): the solid kh line for lambda0_1s = 2 (third solid line from the bottom).

Reading by the shared code in _cao.py (see its docstring for the calibration, the tracing and the
intervals). Tick labels matched: x 10 (frame), 100, 1000 (frame), log; y 0 (frame), 0.2-1.0, 1.2 (frame).
"""
import importlib.util
from pathlib import Path

SPEC = {'x': {'log': True, 'lo': 10, 'hi': 1000, 'ticks': [100]}, 'y': {'lo': 0, 'hi': 1.2, 'ticks': [0.2, 0.4, 0.6, 0.8, 1.0]}, 'seed': [11, 'near', 0.66], 'blank': [[760, 2560, 2160, 2840], [1840, 880, 3320, 1400]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("cao2012_cao", Path(__file__).with_name("_cao.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, SPEC)
