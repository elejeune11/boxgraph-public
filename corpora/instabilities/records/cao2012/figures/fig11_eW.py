"""Fig. 11 (PDF p. 6): the green line, eW theoretical solution.

Reading by the shared code in _cao.py (see its docstring for the calibration, the tracing and the
intervals). Tick labels matched: x 1 (frame), 10, 100 (major ticks), log; y 0 (frame), 0.05-0.30 (major ticks), 0.35 (frame).
"""
import importlib.util
from pathlib import Path

SPEC = {'frame': 'black', 'x': {'log': True, 'lo': 1, 'ticks': [10, 100], 'major_len': 30}, 'y': {'lo': 0, 'hi': 0.35, 'ticks': [0.05, 0.1, 0.15, 0.2, 0.25, 0.3], 'major_len': 36}, 'ink': [0, 118, 48], 'tol': 60, 'w': 16, 'seed': [5, 0], 'blank': [[1840, 1120, 2120, 1280]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("cao2012_cao", Path(__file__).with_name("_cao.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, SPEC)
