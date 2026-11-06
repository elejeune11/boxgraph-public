"""Fig. 4l (PDF p. 5): the thin orange model line (b6), read at the columns of the orange circles at 14 and 29 kPa; at lower stiffness it runs under the thick blue line

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
CONFIG = {'at_markers': {'color': (240, 161, 148),
                'others': [(130, 195, 236)],
                'present': ['0.25', '0.7', '14', '29'],
                'r_from': (130, 195, 236),
                'under': True},
 'color': (240, 161, 148),
 'min_len': 1,
 'open_px': 0,
 'seed': 'auto',
 'ylabels': [0, 1, 2, 3, 4, 5, 6, 7]}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("elosegui2014_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_curve(image, at, CONFIG)
