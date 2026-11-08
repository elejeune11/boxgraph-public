"""Fig. 5 (PDF p. 9), Right Brachial Artery: backward wave intensity: the bottom edge of the black ink (negative, or zero).

Reading by the shared code in _wave.py (see its docstring). y labels matched [2, 1.5, 1, 0.5, 0, -0.5] (x10^6 W/m^2/s^2: the label factor of the axis title is applied); x: time 0 at the left y axis and
the ticks of this panel's own x axis matched to 0.2, 0.4, 0.6, 0.8 s (printed under the wave intensity panel).
"""
import importlib.util
from pathlib import Path

SPEC = {'x': [0, 0.2, 0.4, 0.6, 0.8], 'y': [2, 1.5, 1, 0.5, 0, -0.5], 'envelope': 'lower', 'scale': 1000000.0}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2015_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
