"""Fig. 3G (PDF p. 5), line plot: mean angle between paxillin plaque velocity and the protrusion axis in 5-um bins against distance from the protrusion tip; markers with the 95% confidence band. x stubs 0..50 every 5; y stubs 40..130 every 10 (labels printed every 20).
Method and calibration in _curve.py and _kit.py (both pinned below); CONFIG holds the printed tick
labels matched to the tick marks found, the series colours, and which series is returned."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_curve.py": "19f9225dd83831c4aa8d68c19585277b2d2cc891d0ad723e7769194251cda55f"}
CONFIG = {'dark': 130, 'xlabels': [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50], 'ylabels': [40, 50, 60, 70, 80, 90, 100, 110, 120, 130], 'marker': [0, 100, 190], 'marker_tol': 60, 'band': [204, 226, 241], 'band_tol': 30}


def _load(name):
    p = HERE / name
    if hashlib.sha256(p.read_bytes()).hexdigest() != PINS[name]:
        raise RuntimeError(f"{name} changed; re-check this reading and update its pin")
    spec = importlib.util.spec_from_file_location("owen2017_" + p.stem.strip("_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _load("_curve.py").markers_band(_load("_kit.py"), image, CONFIG)
