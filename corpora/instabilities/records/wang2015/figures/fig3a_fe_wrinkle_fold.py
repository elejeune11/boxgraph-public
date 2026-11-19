"""Fig. 3A: the dotted wrinkle / fold boundary (1.3 < mu_f/mu_s < 12), read as eM at given ratios; see fig3a_fe_lines.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "fig3a_fe_lines", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig3a_fe_lines.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.wrinkle_upper(image, at)
