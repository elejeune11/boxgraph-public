"""Fig. 5k: the lower edge of each box (1 soft, 2 stiff, 3 soft-weld)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig5k", Path(__file__).with_name("_fig5k.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return [q["q1"] for _, q in F.boxes(image)]
