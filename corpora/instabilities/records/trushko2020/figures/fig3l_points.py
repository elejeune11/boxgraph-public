"""Fig. 3L (PDF p. 7): pressure at buckling (Pa) of 1% alginate capsules, the red points over the
box plot, each at x = its rank. Shared code and calibration: _box.py."""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("trushko2020__box", Path(__file__).with_name("_box.py"))
M = importlib.util.module_from_spec(_s)
_s.loader.exec_module(M)


def read(image, at):
    return M.read_group(image, "3L", (225, 20, 25), 70.0)
