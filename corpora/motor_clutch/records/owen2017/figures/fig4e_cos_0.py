"""Fig. 4E (PDF p. 7): counts of alpha-actinin-1 puncta pairs against distance between the puncta, in the
cos(theta) = 0 row of the density map (puncta moving at right angles). Method and calibration in _heat.py and _kit.py (both pinned)."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_heat.py": "0c5bb0b373b797ebf4cd319f39b9bf19fae0fd0543fa0330865c4d991d5aeea6"}
CONFIG = {'rows': 21, 'row': 10, 'xticks': 11}


def _load(name):
    p = HERE / name
    if hashlib.sha256(p.read_bytes()).hexdigest() != PINS[name]:
        raise RuntimeError(f"{name} changed; re-check this reading and update its pin")
    spec = importlib.util.spec_from_file_location("owen2017_" + p.stem.strip("_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _load("_heat.py").read(_load("_kit.py"), image, CONFIG, at)
