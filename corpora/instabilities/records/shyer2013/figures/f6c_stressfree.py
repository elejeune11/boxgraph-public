"""Fig. 6C middle (PDF p. 6): the dotted line, the stress-free thickness of the endoderm-mesenchyme composite (over he). Read as the lowest red ink run in a band at each x.

Shared reading code in _shyer.py (calibration, markers, error bars, bars, lines)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("shyer2013_shared", Path(__file__).with_name("_shyer.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

CONFIG = {
    "x_labels": {
        "values": [
            12.5,
            13.5,
            14.5,
            15.5
        ]
    },
    "y_labels": {
        "axis": "right",
        "values": [
            2,
            4,
            6
        ],
        "at_bottom": 0,
        "at_top": 8
    },
    "color": "red",
    "run": -1,
    "half_band": 14
}


def read(image, at):
    return S.read_line(image, at, CONFIG)
