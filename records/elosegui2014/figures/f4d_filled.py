"""Fig. 4d (PDF p. 5): filled light-blue circles (myo ctrl, a5b1) at 0.7, 2, 14 and 29 kPa, the ones visible; x is the gel each marker belongs to, taken in order from the left among the gels printed in Fig. 1a (0.25, 0.7, 2, 2.8, 5, 14, 29 kPa); those at 0.25, 2.8 and 5 kPa are hidden under open circles and not read

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
CONFIG = {'color': (130, 195, 236), 'present': ['0.7', '2', '14', '29'], 'ylabels': [0, 50, 100, 150, 200]}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("elosegui2014_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_markers(image, at, CONFIG)
