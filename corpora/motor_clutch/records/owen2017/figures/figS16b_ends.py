"""Fig. S16B (PDF p. 40, kappa = 2 x 10^-8): the end of every force-displacement line.
Method in _ends.py. Calibration by _kit.calibrate: inner stubs above the x axis matched to
2..12 um with x = 0 pinned at the y-axis line; stubs right of the y axis matched to 1..6 nN with
y = 0 pinned at the x-axis line (a stray candidate just above the x axis, where the lines leave the
origin, is not evenly spaced and is dropped). All lines end at the right (none reaches 6 nN).
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
    X, Y, info = k.calibrate(image, [2, 4, 6, 8, 10, 12], [1, 2, 3, 4, 5, 6], dark=d, x_pin=0, y_pin=0)
    return e.ends(k, X, Y, d, 5.9, 11.95, int(Y.pix(5.9)) + 6, info["xrow"], info["ycol"])
