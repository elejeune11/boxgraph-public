"""Fig. 3(A), K' = 0.01: the red line, tau = 10; see _fig3.py."""
import importlib.util
from pathlib import Path

BODY = Path(__file__).with_name("_fig3.py")


def read(image, at):
    sp = importlib.util.spec_from_file_location("alonsomatilla2023_fig3", BODY)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod.read_line(image, at, 10, (1928, 543), 2500, [], (1, 0.8, 0.6, 0))
