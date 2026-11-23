"""Fig. 2D (PDF p. 4), right: median magnitude of the fibrin displacement |u| at the cell surface against distance from the protrusion tip (blue line, 1 SD band). Axis labels printed: 0 and 5 um; the x axis runs from 80 (left) to 0 um (right).
Method and calibration in _curve.py and _kit.py (both pinned below); CONFIG holds the printed tick
labels matched to the tick marks found, the series colours, and which series is returned."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_curve.py": "19f9225dd83831c4aa8d68c19585277b2d2cc891d0ad723e7769194251cda55f"}
CONFIG = {'region': [0, 0, 2066, 720], 'dark': 205, 'xlabels': [60, 40, 20, 0], 'x_pin': 80, 'ymarks': [['axis', 0], ['top_stub', 5]], 'ytop': 5, 'y_step': 1, 'line': [95, 155, 200], 'line_tol': 45, 'band': [203, 227, 242], 'band_tol': 24}


def _load(name):
    p = HERE / name
    if hashlib.sha256(p.read_bytes()).hexdigest() != PINS[name]:
        raise RuntimeError(f"{name} changed; re-check this reading and update its pin")
    spec = importlib.util.spec_from_file_location("owen2017_" + p.stem.strip("_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _load("_curve.py").read(_load("_kit.py"), image, CONFIG, at)
