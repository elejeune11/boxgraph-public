"""Fig. 6(b): red circles, the delaminated-buckling/wrinkling boundary (lambda_p = 1). Shared code in _fig6b.py."""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("wang2014_fig6b", Path(__file__).with_name("_fig6b.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read(image, at, "6b", "red")
