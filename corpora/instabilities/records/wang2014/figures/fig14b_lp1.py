"""Fig. 14(b): the solid red line, lambda_p = 1 (top curve at mu_f/mu_s = 1). Shared code in _fig14b.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("wang2014_fig14b", Path(__file__).with_name("_fig14b.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, at, ink="red", w=8.0, seed=[1.5, 0.37])
