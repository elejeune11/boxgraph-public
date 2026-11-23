"""Fig. 3G (PDF p. 5), rose inset: angles between paxillin plaque velocity and the protrusion axis (nine cells),
counts per wedge; 0 deg anterograde, 180 deg retrograde. Three rings, labelled 40 and "60 tracks"; the inner
one is 20 (equal steps from 0, checked by the three-ring fit through the centre). The search is kept inside
the inset (CONFIG["region"]), away from the line plot's confidence band at the top right. The axis line is mid
grey (found with threshold 150; outlines by colour). Method and calibration in _rose_k.py and _kit.py (both pinned below)."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_rose_k.py": "c1bec146059dbe7a839254aecb191f44b9fb89e669c22832f03494d0a84f3f28"}
CONFIG = {'rings': [20, 40, 60], 'fill': [186, 212, 244], 'outline': [105, 125, 150], 'outline_tol': 35, 'axis_dark': 150,
          'cross_frac': [0.5, 0.6, 0.7], 'region': [40, 120, 1010, 1085]}


def _load(name):
    p = HERE / name
    if hashlib.sha256(p.read_bytes()).hexdigest() != PINS[name]:
        raise RuntimeError(f"{name} changed; re-check this reading and update its pin")
    spec = importlib.util.spec_from_file_location("owen2017_" + p.stem.strip("_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _load("_rose_k.py").read(_load("_kit.py"), image, CONFIG)
