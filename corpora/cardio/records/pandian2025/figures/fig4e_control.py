"""Fig. 4e (p. 8): the black filled circles (Control), t = 1 ... 7 s. See _fig4e.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig4e", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig4e.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_series(image, at, "black")
