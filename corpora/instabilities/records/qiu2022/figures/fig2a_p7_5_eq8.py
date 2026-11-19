"""Fig. 2(a) (PDF p. 4): the purple dashed line (Eq. 8), labelled 7.5 (fourth curve).

Read by the shared code in _fig2.py (see its docstring).
"""
import importlib.util
from pathlib import Path

SPEC = {"panel": "a", "kind": "curve", "color": "purple", "line": "dashed"}


def read(image, at):
    spec = importlib.util.spec_from_file_location("qiu2022_fig2", Path(__file__).with_name("_fig2.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
