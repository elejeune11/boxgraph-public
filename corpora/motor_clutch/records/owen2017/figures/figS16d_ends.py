"""Fig. S16D (PDF p. 40, kappa = 2 x 10^-5): the end of every force-displacement line.
Method in _ends.py. Calibration by _kit.calibrate: inner stubs above the x axis matched to
4..12 um (the 2 um stub is hidden where the lines leave the axis) with x = 0 pinned at the y-axis
line; stubs right of the y axis matched to 100..600 nN with y = 0 pinned at the x-axis line.
Lines end at the top (590 nN row) or at 11.95 um.
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
    X, Y, info = k.calibrate(image, [4, 6, 8, 10, 12], [100, 200, 300, 400, 500, 600], dark=d, x_pin=0, y_pin=0)
    return e.ends(k, X, Y, d, 590.0, 11.95, int(Y.pix(590)) + 6, info["xrow"], info["ycol"])
