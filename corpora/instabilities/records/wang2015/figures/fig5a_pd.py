"""Fig. 5A: measured half wavelengths of period-doubles (red diamonds with error bars); see _fig5.py.
Seeds are pixel positions (column, row) near each marker, placed by eye on the 900 dpi crop;
the stem, caps and marker centre are measured from the image around each seed."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

SEEDS = [(635, 1300), (835, 1075), (905, 1040), (1200, 905), (1400, 800), (1570, 742),
         (1705, 688, "diamond partly behind a wrinkle marker")]


def read(image, at):
    xa, ya = _f.calibrate_5a(image)
    return _f.read_seeded(image, xa, ya, "red", SEEDS, _f.frame(image))
