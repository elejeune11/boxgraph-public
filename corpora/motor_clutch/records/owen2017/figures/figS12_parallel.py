"""Fig. S12 (PDF p. 36): empirical CDF of the distance between alpha-actinin-1 puncta moving in parallel (cos theta > 0.95; blue line). Inner stubs matched to 20..180 um and 0.2..1.0, zeros pinned at the axis lines. Read only where the line is clear of the zoom inset and of the orange line.
Method and calibration in _curve.py and _kit.py (both pinned below); CONFIG holds the printed tick
labels matched to the tick marks found, the series colours, and which series is returned."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_curve.py": "19f9225dd83831c4aa8d68c19585277b2d2cc891d0ad723e7769194251cda55f"}
CONFIG = {'xlabels': [20, 40, 60, 80, 100, 120, 140, 160, 180], 'x_pin': 0, 'ylabels': [0.2, 0.4, 0.6, 0.8, 1.0], 'y_pin': 0, 'line': [0, 114, 189], 'line_tol': 60}


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
