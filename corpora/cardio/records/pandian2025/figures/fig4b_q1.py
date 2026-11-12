"""Fig. 4b (p. 8): the dotted line just below the dashed one in each violin (lower quartile; x = 1 control,
2 IL-1beta). See _fig4bc.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig4bc", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig4bc.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_quartile(image, at, "4b", "lower")
