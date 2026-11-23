"""Fig. 4f (PDF p. 6): composite metric, ECFN; x read from the image, gold points with s.e.m. bars.

Read by `read_points` in the shared code _kit.py (method and intervals in its docstring).
CONFIG holds only what the code cannot find by itself: the printed tick labels, matched in order
to the tick marks found, the axis and series colours, and which side the y axis is on. The hash
pins _kit.py: if it changes, re-check this reading and update KIT_SHA256.
"""
import hashlib
import importlib.util
from pathlib import Path

KIT = Path(__file__).with_name("_kit.py")
KIT_SHA256 = "177c1e1671569fcc71f81f34b8a02c55681be5c70c1c3f0731822a660a4d8705"
CONFIG = {'ylabels': [0, 0.2, 0.4, 0.6, 0.8, 1, 1.2], 'xlabels': [0.01, 0.1, 1, 10, 100, 1000], 'xscale': 'log10', 'xaxis_any_ink': True, 'open_frac': 0.8, 'rgb': [200, 150, 0]}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("bangasser2017_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_points(image, at, CONFIG)
