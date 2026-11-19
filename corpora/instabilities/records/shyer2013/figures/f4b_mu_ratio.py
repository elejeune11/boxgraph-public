"""Fig. 4B bottom right (PDF p. 4): modulus ratio mu_e/mu_m (purple filled down-triangles, right axis, ticks 0-20 on the right spine).

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
            5,
            10,
            15
        ],
        "at_bottom": 0,
        "at_top": 20
    },
    "color": "purple",
    "kind": "filled",
    "shape": "tri_down",
    "bars": False
}


def read(image, at):
    return S.read_markers(image, at, CONFIG)
