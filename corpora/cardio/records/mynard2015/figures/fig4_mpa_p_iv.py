"""Fig. 4 (PDF p. 8), Main Pulmonary Artery, in vivo pressure waveform (left panel of the pair).

Reading by the shared code in _wave.py (see its docstring). The crop holds the in vivo and the model panel
of this row; y labels matched [20, 15, 10, 5] (mmHg), beside the in vivo axis; x: time 0 at the y axis and the
ticks of this panel's own x axis matched to 0.2, 0.4, 0.6, 0.8 s.
"""
import importlib.util
from pathlib import Path

SPEC = {'x': [0, 0.2, 0.4, 0.6, 0.8], 'y': [20, 15, 10, 5], 'axis': 0, 'label_axis': 0}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2015_wave", Path(__file__).with_name("_wave.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
