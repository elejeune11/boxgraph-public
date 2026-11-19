"""Fig. 11 (PDF p. 6): the blue spheres, ePD (onset of period doubling, finite element).

Reading by the shared code in _cao.py (see its docstring for the calibration, the tracing and the
intervals). Tick labels matched: x 1 (frame), 10, 100 (major ticks), log; y 0 (frame), 0.05-0.30 (major ticks), 0.35 (frame).
"""
import importlib.util
from pathlib import Path

SPEC = {'frame': 'black', 'x': {'log': True, 'lo': 1, 'ticks': [10, 100], 'major_len': 30}, 'y': {'lo': 0, 'hi': 0.35, 'ticks': [0.05, 0.1, 0.15, 0.2, 0.25, 0.3], 'major_len': 36}, 'ink': 'blue', 'area': [2500, 12000], 'blank': [[1940, 1630, 2100, 1790]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("cao2012_cao", Path(__file__).with_name("_cao.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_markers(image, SPEC)
