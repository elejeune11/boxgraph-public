"""Fig. 2(a) (PDF p. 4): the black crosses (onset of wrinkling predicted by Eq. 11), one on each curve.

x is the curve's printed pressure label (matched to its colour, blue to green from the lowest label up);
y is the horizontal-axis position (curvature) of the point. Read by the shared code in _fig2.py.
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": "a", "kind": "cross"}


def read(image, at):
    spec = importlib.util.spec_from_file_location("qiu2022_fig2", Path(__file__).with_name("_fig2.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
