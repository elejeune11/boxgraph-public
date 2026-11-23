"""Supp. Fig. 11 (PDF p. 35), rose 15 of 18 (row 3, column 5, reading order): angles between
alpha-actinin-1 puncta velocity and the protrusion axis in one cell, counts per wedge. Two rings; the outer
ring is labelled 200 on the page, the inner one is taken as 100 (MATLAB polar rings at equal steps from 0).
Method and calibration in _rose_k.py and _kit.py (both pinned below)."""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_rose_k.py": "c1bec146059dbe7a839254aecb191f44b9fb89e669c22832f03494d0a84f3f28"}
CONFIG = {'rings': [100, 200], 'fill': [188, 212, 244], 'bin_deg': 18}
# bin_deg 18: MATLAB rose's default 20 bins; the outline crossings of roses 1-5 give 18 deg by themselves,
# while sparse roses (few wedges) let the automatic choice pick a wrong division (8.8 or 19 deg).


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
