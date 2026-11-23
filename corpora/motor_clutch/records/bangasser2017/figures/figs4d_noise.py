"""Supplementary Fig. 4D (PDF p. 19): noise floor of the ECFN measurement, grey points; x read from the image (axis printed in Pa).

Read by `read_points` in the shared code _kit.py (method and intervals in its docstring).
CONFIG holds only what the code cannot find by itself: the printed tick labels, matched in order
to the tick marks found, the axis and series colours, and which side the y axis is on. The hash
pins _kit.py: if it changes, re-check this reading and update KIT_SHA256.
"""
import hashlib
import importlib.util
from pathlib import Path

KIT = Path(__file__).with_name("_kit.py")
KIT_SHA256 = "60ad67a5c61e368c57b6a1e99db0dd4bc6713c8ec0a9fe863922e037a670ad84"
CONFIG = {'ylabels': [0, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006], 'xlabels': [0, 0.5, 1, 1.5], 'rgb': [150, 150, 150], 'tol': 30}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2017_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_points(image, at, CONFIG)
