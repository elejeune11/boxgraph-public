"""Fig. 1B (PDF p. 4): the gray curve 'EN measured' (Senzaki et al.'s normalized elastance). See _fig1b.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig1b", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig1b.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)


def read(image, at):
    return _k.read(image, at, "gray")
