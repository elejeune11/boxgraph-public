"""Fig. 5k: the median line of each box (1 soft, 2 stiff, 3 soft-weld), with the whisker ends as its bar."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig5k", Path(__file__).with_name("_fig5k.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return [med for med, _ in F.boxes(image)]
