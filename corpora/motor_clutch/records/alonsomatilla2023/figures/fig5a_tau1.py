"""Fig. 5(A) (PDF p. 10): the orange line, tau = 1; see _fig5a.py."""
import importlib.util
from pathlib import Path

BODY = Path(__file__).with_name("_fig5a.py")


def read(image, at):
    sp = importlib.util.spec_from_file_location("alonsomatilla2023_fig5a", BODY)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod.read_tau(image, at, 1)
