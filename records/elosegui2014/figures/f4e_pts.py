"""Fig. 4e (PDF p. 5): light-blue circles (a5b1), the gels 0.7, 5, 14 and 29 kPa in order

Read by `read_markers` in the shared code _kit.py (method and intervals in its docstring). CONFIG
holds only what the code cannot find by itself: the printed tick labels, matched in order to the
tick marks found, the series colours, and which gel or group each found mark is, by its order.
The hash pins _kit.py: if it changes, re-check this reading and update KIT_SHA256.
"""
import hashlib
import importlib.util
from pathlib import Path

KIT = Path(__file__).with_name("_kit.py")
KIT_SHA256 = "44145b7d4e8bf9812ea90fabaa1f418c2ad8c4ee03eba55f0fa979e4016c8f7b"
CONFIG = {'color': (130, 195, 236), 'present': ['0.7', '5', '14', '29'], 'ylabels': [40, 60, 80, 100, 120]}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("elosegui2014_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_markers(image, at, CONFIG)
