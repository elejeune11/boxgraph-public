"""Fig 9c (PDF p. 18): threshold division strain, red curve (Connected Ligands). See _fig9.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_fig9", os.path.join(os.path.dirname(__file__), "_fig9.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_panel(image, at, "c", "red", seed=[(16, 0.62), (21, 0.6), (30, 0.675)])
