"""Supplementary Fig. 2E (PDF p. 16): averaged MSD, blue curve (100 kPa); read where its s.e.m. bars stand (the run in that column is the bar: its middle is the mean).

Read by `read_curve` in the shared code _kit.py (method and intervals in its docstring).
CONFIG holds only what the code cannot find by itself: the printed tick labels, matched in order
to the tick marks found, the axis and series colours, and which side the y axis is on. The hash
pins _kit.py: if it changes, re-check this reading and update KIT_SHA256.
"""
import hashlib
import importlib.util
from pathlib import Path

KIT = Path(__file__).with_name("_kit.py")
KIT_SHA256 = "177c1e1671569fcc71f81f34b8a02c55681be5c70c1c3f0731822a660a4d8705"
CONFIG = {'ylabels': [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000], 'xlabels': [0, 100, 200, 300, 400], 'rgb': [40, 40, 170], 'tol': 100, 'remove_markers': False, 'start': 'bottom', 'max_jump': 200, 'near': 3, 'merge': 8}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2017_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_curve(image, at, CONFIG)
