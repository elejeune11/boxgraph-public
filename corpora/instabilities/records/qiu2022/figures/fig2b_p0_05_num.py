"""Fig. 2(b) (PDF p. 4): the red solid line (numerical minimization of Eq. 2), labelled 0.05 (second curve).

Read by the shared code in _fig2.py (see its docstring).
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": "b", "kind": "curve", "color": "red", "line": "solid"}


def read(image, at):
    spec = importlib.util.spec_from_file_location("qiu2022_fig2", Path(__file__).with_name("_fig2.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
