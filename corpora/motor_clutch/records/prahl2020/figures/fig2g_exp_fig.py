"""Fig. 2G (PDF p. 5): black circles: experiment, pooled control (n = 403 cells), mean MSD with SEM bars

Read by `read_coloured_points` in the shared code _kit.py (method and intervals in its docstring and the
reader's). CONFIG holds only what the code cannot find by itself: the printed tick labels, matched
in order to the tick marks found (`yevery`: labels on every k-th tick, as seen on the axis), the
series colour where there is one, and the number of groups on a categorical axis. The hash pins
_kit.py: if it changes, re-check this reading and update KIT_SHA256.
"""
import hashlib
import importlib.util
from pathlib import Path

KIT = Path(__file__).with_name("_kit.py")
KIT_SHA256 = "3cff527e5ed31382487f1f9d6c43d99b88db1a1796d94775da37b05433755678"
CONFIG = {'ylabels': [0, 5000, 10000, 15000], 'xlabels': [0, 20, 40, 60, 80, 100, 120, 140, 160, 180], 'rgb': [0, 0, 0], 'tol': 80, 'open': 15}


def read(image, at):
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("prahl2020_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit.read_coloured_points(image, at, CONFIG)
