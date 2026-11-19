"""Fig. S6(b) (PDF p. 20): the eight blue open circles, G/G0 against opening angle (simulation, ABAQUS model). The scan is rotated by about 0.1 degree and straightened first; the light-gray axes are found with a lighter dark threshold.

Shared reading code in _shyer.py (calibration, markers, error bars, bars, lines)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("shyer2013_shared", Path(__file__).with_name("_shyer.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

CONFIG = {
    "x_labels": {
        "values": [
            50,
            100,
            150,
            200,
            250
        ],
        "at_left": 0,
        "at_right": 300
    },
    "y_labels": {
        "axis": "left",
        "values": [
            1.0,
            1.5
        ],
        "at_bottom": 0.5
    },
    "dark": 215,
    "dark_chroma": 40,
    "spine_frac": 0.4,
    "min_hole": 4,
    "color": "blue",
    "kind": "open"
}


def read(image, at):
    return S.read_markers_deskewed(image, at, CONFIG)
