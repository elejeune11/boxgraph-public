"""Fig. 8 (PDF p. 5): the dark red hexagons, ePD (onset of period doubling, finite element).

Reading by the shared code in _cao.py (see its docstring for the calibration, the tracing and the
intervals). Tick labels matched: x 1 (frame), 10 (major tick), 100 (frame), log; y 0 (frame), 0.05-0.25 (major ticks), 0.30 (frame).
"""
import importlib.util
from pathlib import Path

SPEC = {'frame': 'black', 'x': {'log': True, 'lo': 1, 'hi': 100, 'ticks': [10], 'major_len': 30}, 'y': {'lo': 0, 'hi': 0.3, 'ticks': [0.05, 0.1, 0.15, 0.2, 0.25], 'major_len': 30}, 'ink': 'red', 'area': [2500, 12000], 'blank': [[520, 2160, 720, 2360]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("cao2012_cao", Path(__file__).with_name("_cao.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_markers(image, SPEC)
