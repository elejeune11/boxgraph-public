"""Fig. 4f (PDF p. 5): the model line, read at the column of each visible filled circle (0.7, 14, 29 kPa)

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
CONFIG = {'at_markers': {'color': (130, 195, 236), 'present': ['0.7', '14', '29']},
 'blank_also': [{'color': (130, 195, 236),
                 'open': True,
                 'present': ['0.25', '0.7', '5', '14', '29'],
                 'quad_min': 0.15,
                 'ring_min': 0.45}],
 'color': (130, 195, 236),
 'min_len': 11,
 'open_px': 4,
 'seed': 'auto',
 'ylabels': [0, 2, 3, 4, 5, 6, 7]}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("elosegui2014_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_curve(image, at, CONFIG)
