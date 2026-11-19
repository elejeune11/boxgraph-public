"""Fig. 4B top right (PDF p. 4): fold spacing over endoderm thickness, simulation (red open circles, dashed line).

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
    "color": "red",
    "kind": "open"
}


def read(image, at):
    return S.read_markers(image, at, CONFIG)
