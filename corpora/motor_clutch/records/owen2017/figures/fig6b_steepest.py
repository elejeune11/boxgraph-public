"""Fig. 6B (PDF p. 9): the steepest force-displacement line (leftmost line, reaching 60 nN first).

Calibration by _kit.calibrate: inner tick stubs above the x axis matched to 2..12 um, x = 0 pinned
at the y-axis line; stubs right of the y axis matched to 10..60 nN, y = 0 pinned at the x-axis
line. Dark = grey < 128 (black lines on white, raster figure).
At each displacement the steepest line is the topmost dark run in the column below the 60 nN
row (all other lines lie below it for u < 2.5 um). Interval as in _kit.curve_value.
"""
import hashlib
import importlib.util
from pathlib import Path

KIT = Path(__file__).with_name("_kit.py")
KIT_SHA256 = "9be2505d0d93dc75e53e7d92a60b0ced8cd3161ce9047573b3cab50e10d3e2c9"


def _kit():
    if hashlib.sha256(KIT.read_bytes()).hexdigest() != KIT_SHA256:
        raise RuntimeError("_kit.py changed; re-check this reading and update KIT_SHA256")
    spec = importlib.util.spec_from_file_location("owen2017_kit", KIT)
    kit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kit)
    return kit


def read(image, at):
    k = _kit()
    d = k.dark_mask(image, 128)
    X, Y, info = k.calibrate(image, [2, 4, 6, 8, 10, 12], [10, 20, 30, 40, 50, 60], dark=d, x_pin=0, y_pin=0)
    r0 = int(Y.pix(60)) + 4
    r1 = int(info["xrow"] - info["hx"] - 2)
    return [k.curve_value(X, Y, d, float(x), lambda rs: rs[0], r0=r0, r1=r1, note="topmost line")
            for x in at]
