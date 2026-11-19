"""Fig. 2B (PDF p. 2): the light-blue bars, circumferential compression ratio (muscle over separated mesenchyme) at E8-E12, read on the labelled left axis (the right axis carries the same tick rows but no labels).

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
            1.5,
            2.0,
            2.5
        ]
    }
}


def read(image, at):
    return S.read_gray_bars(image, at, CONFIG)
