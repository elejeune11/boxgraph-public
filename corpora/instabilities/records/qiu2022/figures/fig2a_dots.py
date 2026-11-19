"""Fig. 2(a) (PDF p. 4): the coloured dots (onset of wrinkling computed numerically), one on each curve.

x is the curve's printed pressure label (matched to its colour, blue to green from the lowest label up);
y is the horizontal-axis position (curvature) of the point. Read by the shared code in _fig2.py.
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": "a", "kind": "dot"}


def read(image, at):
    spec = importlib.util.spec_from_file_location("qiu2022_fig2", Path(__file__).with_name("_fig2.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
