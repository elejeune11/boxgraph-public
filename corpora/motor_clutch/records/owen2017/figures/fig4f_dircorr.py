"""Fig. 4F (PDF p. 7): directional correlation (median cosine of the angle between velocities of alpha-actinin-1 puncta pairs) against distance between puncta; blue line inside its SE band. y stubs every 0.05 matched to 0.05..0.4 (labels printed every 0.1); the x-axis line is -0.05; the grey zero line is not used.
Method and calibration in _curve.py and _kit.py (both pinned below); CONFIG holds the printed tick
labels matched to the tick marks found, the series colours, and which series is returned."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_curve.py": "19f9225dd83831c4aa8d68c19585277b2d2cc891d0ad723e7769194251cda55f"}
CONFIG = {'dark': 175, 'xlabels': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 'x_pin': 0, 'ylabels': [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4], 'y_pin': -0.05, 'line': [85, 150, 195], 'line_tol': 45, 'band': [208, 230, 250], 'band_tol': 28}


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
