"""Fig. 2 (PDF p. 2): the lower solid line, eW of the exact analysis (labelled eW).

Reading by the shared code in _cao.py (see its docstring for the calibration, the tracing and the
intervals). Tick labels matched: x 1 (frame), 10, 100, 1000 (frame), log; y 0 (frame), 0.1-0.5, 0.6 (frame).
"""
import importlib.util
from pathlib import Path

SPEC = {'x': {'log': True, 'lo': 1, 'hi': 1000, 'ticks': [10, 100]}, 'y': {'lo': 0, 'hi': 0.6, 'ticks': [0.1, 0.2, 0.3, 0.4, 0.5]}, 'seed': [1.2, 0]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("cao2012_cao", Path(__file__).with_name("_cao.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, SPEC)
