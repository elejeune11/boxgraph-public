"""Fig. 3c (PDF p. 4): the model curve (light blue) of cell traction; x from the centres of the printed labels 0.1, 1, 10, 100 under Fig. 3e (shared x axis), which are not on one log scale

Read by `read_curve` in the shared code _kit.py (method and intervals in its docstring). CONFIG
holds only what the code cannot find by itself: the printed tick labels, matched in order to the
tick marks found, the series colours, and which gel or group each found mark is, by its order.
The hash pins _kit.py: if it changes, re-check this reading and update KIT_SHA256.
"""
import hashlib
import importlib.util
from pathlib import Path

KIT = Path(__file__).with_name("_kit.py")
KIT_SHA256 = "44145b7d4e8bf9812ea90fabaa1f418c2ad8c4ee03eba55f0fa979e4016c8f7b"
CONFIG = {'color': (130, 195, 236),
 'seed': [993, 1456],
 'xlabel_rows': [6235, 6420],
 'xlabels': [0.1, 1, 10, 100],
 'xmode': 'labels',
 'xscale': 'log10',
 'ylabels': [0, 50, 100, 150, 200],
 'yrows': [30, 1800]}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("elosegui2014_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_curve(image, at, CONFIG)
