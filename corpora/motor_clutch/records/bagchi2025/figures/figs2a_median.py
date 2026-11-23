"""S2a Fig (PDF p. 44): the red median lines of the two box plots (1: RF, 2: AF), average velocity.
Read by _kit.run_spec with the settings of this reading in _specs.py (axis labels matched,
colour, marker kind, regions blanked)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_kit", os.path.join(os.path.dirname(__file__), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)


def read(image, at):
    return K.run_spec("figs2a_median", image, at)
