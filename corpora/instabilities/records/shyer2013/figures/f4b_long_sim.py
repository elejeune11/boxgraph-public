"""Fig. 4B bottom left (PDF p. 4): longitudinal compression ratio, simulation (red open down-triangles, dashed line).

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
    "color": "red",
    "kind": "open",
    "shape": "tri_down",
    "fallback_kind": "filled",
    "pick": "lowest",
    "r_open": 6,
    "min_hole": 6,
    "ring_search": False,
    "fallback_at": [
        12
    ]
}


def read(image, at):
    return S.read_markers(image, at, CONFIG)
