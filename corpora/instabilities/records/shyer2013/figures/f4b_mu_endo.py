"""Fig. 4B bottom right (PDF p. 4): shear modulus of the endoderm (red filled circles, left axis), with 1 SD error bars.

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
            10
        ]
    },
    "y_labels": {
        "axis": "right",
        "values": [
            200,
            400,
            600
        ],
        "at_bottom": 0,
        "at_top": 800
    },
    "color": "red",
    "kind": "filled",
    "bars": True,
    "bar_color": "pink"
}


def read(image, at):
    return S.read_markers(image, at, CONFIG)
