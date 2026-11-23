"""Fig. S1(B): the crimson line, F = 0.5; see _figs1b.py."""
import importlib.util
from pathlib import Path

BODY = Path(__file__).with_name("_figs1b.py")


def read(image, at):
    sp = importlib.util.spec_from_file_location("alonsomatilla2023_figs1b", BODY)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod.read_F(image, at, "0.5")
