"""Fig. 3 (PDF p. 7): the literature PWV data points (filled diamonds) with their SD bars. See _fig3.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig3.py"))
_k = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_k)


def read(image, at):
    return _k.read_markers(image)
