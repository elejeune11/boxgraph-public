"""Fig. 2a (p. 5): the light blue open circles (REAVER), every one. See _fig2a.py. Three circles overlap
near x = 21 um, the upper one half hidden behind two pink squares; each is found by its ring."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig2a", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2a.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    cal = _f.calibrate(image)
    cents, R = _f.ring_centres(image, "blue")
    return _f.to_readings(cal, cents, 4, f"blue ring (radius {R} px)")
