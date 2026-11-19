"""Fig. 7 (PDF p. 4): the solid line for uniaxial lambda0_1s = 1 (lowest solid line at mu_f/mu_s = 7).

Reading by the shared code in _cao.py (see its docstring for the calibration, the tracing and the
intervals). Tick labels matched: x 1 (frame), 10, 100, 1000 (frame), log; y 0.001 (frame), 0.01, 0.1, 1 (frame), log.
"""
import importlib.util
from pathlib import Path

SPEC = {'x': {'log': True, 'lo': 1, 'hi': 1000, 'ticks': [10, 100]}, 'y': {'log': True, 'lo': 0.001, 'hi': 1, 'ticks': [0.01, 0.1]}, 'seed': [7, 0], 'blank': [[620, 2000, 1580, 2460], [1880, 1620, 3000, 1800]]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("cao2012_cao", Path(__file__).with_name("_cao.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, SPEC)
