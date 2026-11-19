"""Fig. 7(a): brown stars, experiments where wrinkling was observed (lambda_p = 2). Shared code in _fig7a.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("wang2014_fig7a", Path(__file__).with_name("_fig7a.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_mode(image, "brown")
