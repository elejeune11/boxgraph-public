"""Fig. 5A: measured ridge wavelengths (green squares with error bars); see _fig5.py.
Seeds are pixel positions (column, row) near each marker, placed by eye on the 900 dpi crop;
the stem, caps and marker centre are measured from the image around each seed."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

SEEDS = [(580, 1455), (675, 1455), (920, 1300), (980, 1200), (1160, 1115), (1255, 1045)]


def read(image, at):
    xa, ya = _f.calibrate_5a(image)
    return _f.read_seeded(image, xa, ya, "green", SEEDS, _f.frame(image))
