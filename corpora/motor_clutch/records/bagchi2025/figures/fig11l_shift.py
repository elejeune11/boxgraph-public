"""Fig 11l (PDF p. 21): the five asterisks, one per k_s range in the legend order (1: 0.06-12.3, 2: 1.23-12.3, 3: 3.08-12.3, 4: 6.17-12.3, 5: 9.26-12.3 nN/um).
Read by _kit.run_spec with the settings of this reading in _specs.py (axis labels matched,
colour, marker kind, regions blanked)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_kit", os.path.join(os.path.dirname(__file__), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)


def read(image, at):
    return K.run_spec("fig11l_shift", image, at)
