"""Fig. 4B top left (PDF p. 4): muscle (tube) circumference of the simulation (blue open circles, dashed line).

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
            0.5,
            1,
            1.5,
            2
        ],
        "at_bottom": 0
    },
    "color": "blue",
    "kind": "open"
}


def read(image, at):
    return S.read_markers(image, at, CONFIG)
