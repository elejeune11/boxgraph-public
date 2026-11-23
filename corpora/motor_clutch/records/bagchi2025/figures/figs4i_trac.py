"""S4i Fig (PDF p. 46): the Traction (right axis) bar: x = 1 the top of the red segment (Connected Ligand), x = 2 the top of the blue segment (Disconnected Ligand) drawn above it.
Read by _kit.run_spec with the settings of this reading in _specs.py (axis labels matched,
colour, marker kind, regions blanked)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_kit", os.path.join(os.path.dirname(__file__), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)


def read(image, at):
    return K.run_spec("figs4i_trac", image, at)
