"""Fig 10m (PDF p. 20): the seven asterisks: 1-6 one per alpha as in Fig 10l, 7 Connected Ligand (right-hand axis).
Read by _kit.run_spec with the settings of this reading in _specs.py (axis labels matched,
colour, marker kind, regions blanked)."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_kit", os.path.join(os.path.dirname(__file__), "_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)


def read(image, at):
    return K.run_spec("fig10m_eff", image, at)
