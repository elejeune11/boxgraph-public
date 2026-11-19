"""Fig. 4B bottom left (PDF p. 4): circumferential compression ratio, measured (blue filled down-triangles, solid line), with 1 SD error bars.

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
            0.2,
            0.4,
            0.6,
            0.8,
            1.0
        ],
        "at_bottom": 0
    },
    "color": "blue",
    "kind": "filled",
    "shape": "tri_down",
    "tall": "upper",
    "pick": "highest",
    "bars": True,
    "r_open": 6
}


def read(image, at):
    return S.read_markers(image, at, CONFIG)
