"""Fig. S9B (PDF p. 33), right: fractional velocity localization error of alpha-actinin-1 tracks, one dot per cell and lag time. x stubs 2..40 min; y stubs -0.3..0.6 (the x-axis line is -0.4).
Method and calibration in _curve.py and _kit.py (both pinned below); CONFIG holds the printed tick
labels matched to the tick marks found, the series colours, and which series is returned."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_curve.py": "19f9225dd83831c4aa8d68c19585277b2d2cc891d0ad723e7769194251cda55f"}
CONFIG = {'xlabels': [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40], 'x_pin': 0, 'ylabels': [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], 'y_pin': -0.4, 'marker': [0, 114, 189]}


def _load(name):
    p = HERE / name
    if hashlib.sha256(p.read_bytes()).hexdigest() != PINS[name]:
        raise RuntimeError(f"{name} changed; re-check this reading and update its pin")
    spec = importlib.util.spec_from_file_location("owen2017_" + p.stem.strip("_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _load("_curve.py").scatter(_load("_kit.py"), image, CONFIG)
