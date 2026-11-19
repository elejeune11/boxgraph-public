"""Fig. 14(b): the magenta line with crosses, lambda_p = 3 (leader '3'). Shared code in _fig14b.py.

The crosses sit on the line, so where a cross is drawn the run is fused and the interval covers it.
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("wang2014_fig14b", Path(__file__).with_name("_fig14b.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, at, ink="magenta", w=8.0, seed=[1.5, 0.31])
