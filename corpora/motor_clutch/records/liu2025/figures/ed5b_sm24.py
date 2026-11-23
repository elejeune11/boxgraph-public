"""Extended Data Fig. 5(b) (PDF p. 70): the solid blue curve, linear WT model with sigma_m = 24 um^-2.
Settings and method: _ed5.py and _fig.py. The dotted talin WT curves are drawn lighter and lie below the solid ones; the top run is taken."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("liu2025_ed5", Path(__file__).with_name("_ed5.py"))
E5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E5)


def read(image, at):
    return E5.read(image, at, "b", "blue")


def debug(image):
    return E5.debug(image, "b")
