"""Fig. 3D top right (PDF p. 3): the light-blue bars DMSO, AG, FK, length ratio of E15 segments cultured 48 h (control over drug).

Shared reading code in _shyer.py (calibration, markers, error bars, bars, lines)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("shyer2013_shared", Path(__file__).with_name("_shyer.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

CONFIG = {
    "y_labels": {
        "values": [
            0.5,
            1.0,
            1.5
        ]
    }
}


def read(image, at):
    return S.read_gray_bars(image, at, CONFIG)
