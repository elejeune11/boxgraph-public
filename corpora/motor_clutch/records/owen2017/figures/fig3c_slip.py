"""Fig. 3C (PDF p. 5): histogram of slip speeds |v_fib - v_pax| (blue; counts), bar by bar. The rose
plot inset lies behind the bars (its wedges are a lighter blue, outside the colour tolerance).
Method and calibration in _hist.py and _kit.py (both pinned below); CONFIG holds the printed tick
labels matched to the tick marks found, the series colours, and which series is returned."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_hist.py": "c9f79082d7ea0024585807d8093e29ebc8135b8e7dbedc7b57e4f41f307374b3"}
CONFIG = {'x_tick_line': 'top', 'x_ticks': [50, 100, 150], 'x_spines': [0, 200], 'y_tick_spine': 'right', 'y_ticks': [50, 100], 'y_max_row': 1200, 'y_base_zero': True, 'colors': {'slip': [105, 165, 215]}, 'tol': 45}


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
