"""Fig. 6B (PDF p. 9): the end of every force-displacement line (top edge at 59 nN or right end at
11.95 um). Method in _ends.py; calibration as in fig6b_steepest.py (_kit.calibrate, ticks 2..12 um
and 10..60 nN, zeros pinned at the axis lines). The secant stiffness of a line is y/x of its end
(the line from u = 2 um, which starts off the origin, is the exception; see figures.md).
"""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).parent
PINS = {"_kit.py": "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9",
        "_ends.py": "d2b1f50a1d0104c621c28610f544f6034c9cf6def55df4a0967186ab5bb278a2"}


def _load(name):
    p = HERE / name
    if hashlib.sha256(p.read_bytes()).hexdigest() != PINS[name]:
        raise RuntimeError(f"{name} changed; re-check this reading and update its pin")
    spec = importlib.util.spec_from_file_location("owen2017_" + p.stem.strip("_"), p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    k, e = _load("_kit.py"), _load("_ends.py")
    d = k.dark_mask(image, 128)
    X, Y, info = k.calibrate(image, [2, 4, 6, 8, 10, 12], [10, 20, 30, 40, 50, 60], dark=d, x_pin=0, y_pin=0)
    return e.ends(k, X, Y, d, 59.0, 11.95, int(Y.pix(59)) + 6, info["xrow"], info["ycol"])
