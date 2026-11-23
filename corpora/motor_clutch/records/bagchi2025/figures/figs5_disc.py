"""S5 Fig (PDF p. 47): the cyan-filled stars, Disconnected Ligand (1: low density, rho_l = 0.7; 2: high density, rho_l = 1).
Read by _kit.run_spec with the settings of this reading in _specs.py (axis labels matched,
colour, marker kind, regions blanked)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_kit", os.path.join(os.path.dirname(__file__), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)


def read(image, at):
    return K.run_spec("figs5_disc", image, at)
