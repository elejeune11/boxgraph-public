"""Fig. 5F (p. 6): PIV flow ratio q/q_in per branch (1 Bottom, 2 Middle, 3 Top): the error bar's midpoint
(the mean of the N = 3 constructs) with its ends (+-1 SD, caption). See _fig5f.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig5f", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5f.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_errorbar(image, at)
