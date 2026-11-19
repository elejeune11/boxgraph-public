"""Fig. 4B top right (PDF p. 4): the thin dotted line, the stress-free thickness of the endoderm-mesenchyme composite (over he). Read as the lowest pink ink run in a band at each x.

Shared reading code in _shyer.py (calibration, markers, error bars, bars, lines)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("shyer2013_shared", Path(__file__).with_name("_shyer.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

CONFIG = {
    "x_labels": {
        "values": [
            8,
            10,
            12,
            14
        ]
    },
    "y_labels": {
        "axis": "right",
        "values": [
            5,
            10
        ],
        "at_bottom": 0,
        "at_top": 15
    },
    "color": "pink",
    "run": -1,
    "half_band": 12
}


def read(image, at):
    return S.read_line(image, at, CONFIG)
