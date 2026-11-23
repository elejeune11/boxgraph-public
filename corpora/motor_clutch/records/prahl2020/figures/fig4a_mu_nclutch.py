"""Fig. 4A (PDF p. 7): simulated motility coefficient (open diamonds, SEM bars) at nclutch = 8, 25, 75, 250, 750

Read by `read_errorbar_points` in the shared code _kit.py (method and intervals in its docstring and the
reader's). CONFIG holds only what the code cannot find by itself: the printed tick labels, matched
in order to the tick marks found (`yevery`: labels on every k-th tick, as seen on the axis), the
series colour where there is one, and the number of groups on a categorical axis. The hash pins
_kit.py: if it changes, re-check this reading and update KIT_SHA256.
"""
import hashlib
import importlib.util
from pathlib import Path

KIT = Path(__file__).with_name("_kit.py")
KIT_SHA256 = "370bfb264a7e9a74958aa28d7ea1ee1659c8cf16beed1fbd9b0186368ad0bd59"
CONFIG = {'ylabels': [0, 4, 8, 12, 16, 20], 'yevery': 2, 'xlabels': [1, 10, 100, 1000], 'xscale': 'log10'}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("prahl2020_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_errorbar_points(image, at, CONFIG)
