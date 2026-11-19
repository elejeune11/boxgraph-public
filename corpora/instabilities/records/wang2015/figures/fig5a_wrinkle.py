"""Fig. 5A: measured wrinkle wavelengths (blue triangles with error bars); see _fig5.py.
Seeds are pixel positions (column, row) near each marker, placed by eye on the 900 dpi crop;
the stem, caps and marker centre are measured from the image around each seed."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)

SEEDS = [(1345, 895), (1672, 675, "triangle mostly hidden by the theory line and other markers"), (1805, 565), (1838, 605), (1868, 540),
         (1950, 540, "overlapping triangles of the same colour"),
         (1972, 555, "overlapping triangles of the same colour"),
         (2025, 440, "overlapping triangles of the same colour"), (2197, 330)]


def read(image, at):
    xa, ya = _f.calibrate_5a(image)
    return _f.read_seeded(image, xa, ya, "blue", SEEDS, _f.frame(image))
