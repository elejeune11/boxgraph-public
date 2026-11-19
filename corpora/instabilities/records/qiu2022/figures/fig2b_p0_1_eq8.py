"""Fig. 2(b) (PDF p. 4): the yellow dashed line (Eq. 8), labelled 0.1 (third curve).

Read by the shared code in _fig2.py (see its docstring).
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": "b", "kind": "curve", "color": "yellow", "line": "dashed"}


def read(image, at):
    spec = importlib.util.spec_from_file_location("qiu2022_fig2", Path(__file__).with_name("_fig2.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
