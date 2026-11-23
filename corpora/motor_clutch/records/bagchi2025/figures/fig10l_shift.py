"""Fig 10l (PDF p. 20): the six asterisks, one per alpha in the legend order (1: 0.08, 2: 0.04, 3: 0.02, 4: 0.01, 5: 0.006, 6: 0.003).
Read by _kit.run_spec with the settings of this reading in _specs.py (axis labels matched,
colour, marker kind, regions blanked)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_kit", os.path.join(os.path.dirname(__file__), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)


def read(image, at):
    return K.run_spec("fig10l_shift", image, at)
