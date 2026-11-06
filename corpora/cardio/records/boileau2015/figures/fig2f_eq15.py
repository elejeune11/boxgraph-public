"""Fig. 2(f) STM (PDF p. 8): the thick black line, Eq. 15's peak decay. See _fig2.py for the method."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)


def read(image, at):
    return _k.read_thick(image, at)
