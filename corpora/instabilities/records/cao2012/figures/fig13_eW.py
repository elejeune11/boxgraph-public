"""Fig. 13 (PDF p. 6): the black line, eW theoretical solution.

Reading by the shared code in _cao.py (see its docstring for the calibration, the tracing and the
intervals). Tick labels matched: x 1 (frame), 10, 100, 1000 (major ticks), log; y 0.00-0.20 (major ticks), 0.25 (frame).
"""
import importlib.util
from pathlib import Path

SPEC = {'frame': 'black', 'x': {'log': True, 'lo': 1, 'ticks': [10, 100, 1000], 'major_len': 36}, 'y': {'hi': 0.25, 'ticks': [0.0, 0.05, 0.1, 0.15, 0.2], 'major_len': 30}, 'w': 16, 'seed': [6, 'near', 0.18], 'blank': [[1960, 460, 3600, 640]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("cao2012_cao", Path(__file__).with_name("_cao.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, SPEC)
