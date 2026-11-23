"""Fig 9a (PDF p. 18): cell spring stiffness, blue curve (Disconnected Ligands). See _fig9.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_fig9", os.path.join(os.path.dirname(__file__), "_fig9.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_panel(image, at, "a", "blue", seed=(4, 9.7))
