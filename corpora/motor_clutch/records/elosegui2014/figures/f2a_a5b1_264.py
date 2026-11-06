"""Fig. 2a (PDF p. 3): the bold blue curve (a5b1, 264 nM, marked in bold as the caption says), association and dissociation phases; 30 s and 90 s (injection start and end, where the curve is vertical) are not read

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
 'max_jump': 20,
 'min_len': 14,
 'seed': [1573, 214],
 'xlabels': [0, 20, 40, 60, 80, 100, 120, 140],
 'xmode': 'ticks',
 'ylabels': [20, 40, 60, 80]}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("elosegui2014_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_curve(image, at, CONFIG)
