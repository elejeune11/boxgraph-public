"""Fig. 4A (PDF p. 7), rose inset: angles between the alpha-actinin-1 and the adjacent fibrin velocity vectors
(four cells), counts per wedge. Rings labelled 500 and 1000. The inset sits over the speed histogram, so the
search is restricted to the inset (CONFIG["region"], on the Fig. 4A crop of the existing readings).
Both ring labels are printed. Method and calibration in _rose_k.py and _kit.py (both pinned below); _rose.py,
used for Fig. 4B, took a stray grey run near the centre for a ring here.
The wedges are read from their navy outlines."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_rose_k.py": "c1bec146059dbe7a839254aecb191f44b9fb89e669c22832f03494d0a84f3f28"}
CONFIG = {'rings': [500, 1000], 'fill': [195, 215, 240], 'outline': [75, 92, 118], 'outline_tol': 30, 'cross_frac': [0.35, 0.4, 0.45], 'region': [610, 340, 1500, 1240]}


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
