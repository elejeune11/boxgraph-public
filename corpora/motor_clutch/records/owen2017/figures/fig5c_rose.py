"""Fig. 5C (PDF p. 8): rose plot of the angle between paxillin and colocalized alpha-actinin-1 velocities, wedge by wedge. Rings matched to 5..20 (labels 5, 10, 15, 20 printed).
Method and calibration in _rose.py and _kit.py (both pinned below); CONFIG holds the printed tick
labels matched to the tick marks found, the series colours, and which series is returned."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_rose.py": "c1ec4cde03f1ee3bc45cf36f0227d4c345da8f4afda8034832c559eb9012a8ea"}
CONFIG = {'rings': [5, 10, 15, 20], 'fill': [198, 222, 243], 'outline': [70, 100, 150]}


def _load(name):
    p = HERE / name
    if hashlib.sha256(p.read_bytes()).hexdigest() != PINS[name]:
        raise RuntimeError(f"{name} changed; re-check this reading and update its pin")
    spec = importlib.util.spec_from_file_location("owen2017_" + p.stem.strip("_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _load("_rose.py").read(_load("_kit.py"), image, CONFIG)
