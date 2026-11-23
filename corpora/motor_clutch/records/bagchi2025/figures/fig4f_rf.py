"""Fig 4f (PDF p. 11): the blue open circles, strain rate at the midline, RF (axis in units of 10^-5 1/s; the same plot as Fig 1l).
Read by _kit.run_spec with the settings of this reading in _specs.py (axis labels matched,
colour, marker kind, regions blanked)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_kit", os.path.join(os.path.dirname(__file__), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)


def read(image, at):
    return K.run_spec("fig4f_rf", image, at)
