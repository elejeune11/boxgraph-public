"""Fig. 5A: measured fold wavelengths (magenta crosses with error bars); see _fig5.py.
Seeds are pixel positions (column, row) near each marker, placed by eye on the 900 dpi crop;
the stem, caps and marker centre are measured from the image around each seed."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

SEEDS = [(765, 1160), (1105, 930),
         (1295, 755, "two crosses overlapping"), (1315, 745, "two crosses overlapping"),
         (1455, 750), (1520, 590), (1650, 540),
         (1685, 605, "cross hidden behind a wrinkle and a period-double marker"),
         (1760, 540), (1985, 460, "cross hidden behind wrinkle markers")]


def read(image, at):
    xa, ya = _f.calibrate_5a(image)
    return _f.read_seeded(image, xa, ya, "magenta", SEEDS, _f.frame(image))
