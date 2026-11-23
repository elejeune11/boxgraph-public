"""Fig. S14E (PDF p. 38): distribution of spooling speeds |v_zyx - v_actn| (blue; counts), bar by bar.
x: the left and right spines are 0 and 300 (labels 0 and 300 under them); the four tick stubs on
the top line are 60 apart (the printed labels 100 and 200 sit at their own values, between stubs),
so they are matched to 60, 120, 180, 240. y: stubs on the right spine matched to 10..50.
Method and calibration in _hist.py and _kit.py (both pinned below); CONFIG holds the printed tick
labels matched to the tick marks found, the series colours, and which series is returned."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_hist.py": "c9f79082d7ea0024585807d8093e29ebc8135b8e7dbedc7b57e4f41f307374b3"}
CONFIG = {'x_tick_line': 'top', 'x_ticks': [60, 120, 180, 240], 'x_spines': [0, 300], 'y_tick_spine': 'right', 'y_ticks': [10, 20, 30, 40, 50], 'y_max_row': 1400, 'y_base_zero': True, 'colors': {'rel': [118, 185, 224], 'diff': [235, 168, 135]}, 'overlap': [188, 138, 122], 'tol': 35, 'keep': 'rel'}


def _load(name):
    p = HERE / name
    if hashlib.sha256(p.read_bytes()).hexdigest() != PINS[name]:
        raise RuntimeError(f"{name} changed; re-check this reading and update its pin")
    spec = importlib.util.spec_from_file_location("owen2017_" + p.stem.strip("_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _load("_hist.py").read(_load("_kit.py"), image, CONFIG)
