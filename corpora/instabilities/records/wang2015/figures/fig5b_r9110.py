"""Fig. 5B: measured wrinkle amplitudes for mu_f/mu_s = 9110 (brown right-pointing triangles with error bars); see _fig5.py.
Seeds are pixel positions (column, row) near each marker, placed by eye on the 900 dpi crop;
the stem, caps and marker centre are measured from the image around each seed."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

SEEDS = [(960, 580), (1205, 680), (1808, 835, "triangle on the theory line")]


def read(image, at):
    xa, ya = _f.calibrate_5b(image)
    return _f.read_seeded(image, xa, ya, "brown", SEEDS, _f.frame(image))
