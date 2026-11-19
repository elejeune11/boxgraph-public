"""Fig. 6C right (PDF p. 6): modulus ratio mu_e/mu_m at E14.5 (purple filled down-triangle, right axis 0-2.0, whose short ticks are on the right spine).

Shared reading code in _shyer.py (calibration, markers, error bars, bars, lines)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("shyer2013_shared", Path(__file__).with_name("_shyer.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

CONFIG = {
    "x_labels": {
        "values": [
            14.5
        ]
    },
    "y_labels": {
        "axis": "right",
        "values": [
            0.5,
            1.0,
            1.5,
            2.0
        ],
        "at_bottom": 0
    },
    "tick_len": [
        2,
        45
    ],
    "color": "purple",
    "kind": "filled",
    "shape": "tri_down",
    "bars": False,
    "bar_lw": 3
}


def read(image, at):
    return S.read_markers(image, at, CONFIG)
