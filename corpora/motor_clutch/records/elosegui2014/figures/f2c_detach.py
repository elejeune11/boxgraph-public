"""Fig. 2c (bottom) (PDF p. 3): the bars and error bars; conditions 1-8 left to right are myo ctrl with no ab, avb6 ab, a5b1 ab, avb6 + a5b1 ab, then myo b6 with the same four; conditions 3, 4 and 8 have no bar drawn and are not read

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
CONFIG = {'fills': [(35, 31, 32), (130, 195, 236), (240, 161, 148)],
 'groups': ['1', '2', '5', '6', '7'],
 'missing_note': {'3': 'no bar is drawn for this condition',
                  '4': 'no bar is drawn for this condition',
                  '8': 'no bar is drawn for this condition'},
 'ylabels': [0, 2, 4, 6, 8, 10, 12, 14]}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("elosegui2014_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_bars(image, at, CONFIG)
