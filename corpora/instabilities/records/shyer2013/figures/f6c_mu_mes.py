"""Fig. 6C right (PDF p. 6): shear modulus of the mouse mesenchyme at E14.5 (blue filled circle, left axis), with its 1 SD error bar.

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
        "axis": "left",
        "values": [
            50,
            100
        ],
        "at_bottom": 0,
        "at_top": 150
    },
    "color": "blue",
    "kind": "filled",
    "bars": True,
    "bar_lw": 3
}


def read(image, at):
    return S.read_markers(image, at, CONFIG)
