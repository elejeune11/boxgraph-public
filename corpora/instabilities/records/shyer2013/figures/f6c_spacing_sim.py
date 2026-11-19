"""Fig. 6C middle (PDF p. 6): mouse fold spacing over endoderm thickness, simulation (red open circles, dashed line).

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
    "kind": "open"
}


def read(image, at):
    return S.read_markers(image, at, CONFIG)
