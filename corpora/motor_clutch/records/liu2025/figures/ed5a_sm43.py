"""Extended Data Fig. 5(a) (PDF p. 70): the green curve, linear KD model with sigma_m = 43 um^-2.
Settings and method: _ed5.py and _fig.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("liu2025_ed5", Path(__file__).with_name("_ed5.py"))
E5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E5)


def read(image, at):
    return E5.read(image, at, "a", "green")


def debug(image):
    return E5.debug(image, "a")
