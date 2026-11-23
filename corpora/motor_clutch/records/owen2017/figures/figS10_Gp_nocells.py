"""Fig. S10 (PDF p. 34), upper panel: storage modulus G' of the gels without cells (orange markers).
Method and calibration in _s10.py and _kit.py (both pinned below); CONFIG holds the printed tick
labels matched to the tick marks found, the series colours, and which series is returned."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_s10.py": "36a6cc8cbef09fb5c1bb5a8a86c619ebd0ddbc11bc5f9a7b5a74c792a9499be1"}
CONFIG = None


def _load(name):
    p = HERE / name
    if hashlib.sha256(p.read_bytes()).hexdigest() != PINS[name]:
        raise RuntimeError(f"{name} changed; re-check this reading and update its pin")
    spec = importlib.util.spec_from_file_location("owen2017_" + p.stem.strip("_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _load("_s10.py").read(_load("_kit.py"), image, 'upper', 'orange')
