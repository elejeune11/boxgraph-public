"""Fig. S6(a) (PDF p. 20): the green filled squares of the 'Without Eigenstrain' curve, reaction force against displacement (simulation). Squares hidden under the eight opening-angle curves (below about 130 um) are not found and not read; the legend's sample square is excluded by its layout box.

Shared reading code in _shyer.py (calibration, markers, error bars, bars, lines)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("shyer2013_shared", Path(__file__).with_name("_shyer.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

CONFIG = {
    "x_labels": {
        "values": [
            20,
            40,
            60,
            80,
            100,
            120,
            140,
            160
        ],
        "at_left": 0,
        "at_right": 180
    },
    "y_labels": {
        "axis": "left",
        "values": [
            0.02,
            0.04,
            0.06,
            0.08,
            0.1,
            0.12
        ],
        "at_bottom": 0,
        "at_top": 0.14
    },
    "dark": 215,
    "dark_chroma": 40,
    "spine_frac": 0.4,
    "r_open": 5,
    "min_filled": 8,
    "color": "green",
    "kind": "filled",
    "exclude": [
        [
            200,
            960,
            360,
            1100
        ]
    ]
}


def read(image, at):
    return S.read_markers_deskewed(image, at, CONFIG)
