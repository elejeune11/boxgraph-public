"""Fig. 2 (PDF p. 8): the dash-dot red line, lambda_q2 (the lower red line). See _fig2_lines.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig2_lines", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig2_lines.py"))
_l = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_l)


def read(image, at):
    return _l.read_line(image, at, "red", 1)
