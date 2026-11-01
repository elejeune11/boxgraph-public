"""Fig. 2e (PDF p. 3): the bars and error bars, conditions 1-4: myo ctrl no ab, myo ctrl avb6 ab, myo b6 no ab, myo b6 avb6 ab

Read by `read_bars` in the shared code _kit.py (method and intervals in its docstring). CONFIG
holds only what the code cannot find by itself: the printed tick labels, matched in order to the
tick marks found, the series colours, and which gel or group each found mark is, by its order.
The hash pins _kit.py: if it changes, re-check this reading and update KIT_SHA256.
"""
import hashlib
import importlib.util
from pathlib import Path

KIT = Path(__file__).with_name("_kit.py")
KIT_SHA256 = "44145b7d4e8bf9812ea90fabaa1f418c2ad8c4ee03eba55f0fa979e4016c8f7b"
CONFIG = {'fills': [(35, 31, 32), (130, 195, 236)],
 'groups': ['1', '2', '3', '4'],
 'ylabels': [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2]}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("elosegui2014_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_bars(image, at, CONFIG)
