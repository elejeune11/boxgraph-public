"""Supp. Fig. 2 (PDF p. 25), left column, row 2: displacement normal to the cell surface of example cell 1 against distance from
the protrusion tip (median, dark line; SD band). Printed y labels [1, 0, -1, -2].
Method and calibration in _s2.py and _kit.py (both pinned below)."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_s2.py": "cd9c080903605ab244bcd8998b7535630b4da27739968c846b50727421be4eda"}
CONFIG = {'panel': [150, 540, 790, 1085], 'xpanel': [150, 3160, 790, 3720], 'yticks': [[1, 1], [2, 0], [3, -1], [4, -2]]}


def _load(name):
    p = HERE / name
    if hashlib.sha256(p.read_bytes()).hexdigest() != PINS[name]:
        raise RuntimeError(f"{name} changed; re-check this reading and update its pin")
    spec = importlib.util.spec_from_file_location("owen2017_" + p.stem.strip("_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _load("_s2.py").read(_load("_kit.py"), image, CONFIG, at)
