"""Fig. 9, bottom: the hatched bars (No Emax): model percent change with the Emax effectors removed (see _fig9.py). x: 1 SAP, 2 CO, 3 HR, 4 R."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "_fig9", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig9.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_series(image, "bottom", 3)
