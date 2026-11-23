"""Fig. S4, right (PDF p. 36): the red line, tau = 10: bound fraction against beta_c (K' = 1,
F = 1, omega' = 200); read with the Fig. 3 body, _fig3.py."""
import importlib.util
from pathlib import Path

BODY = Path(__file__).with_name("_fig3.py")
COLOURS = {1: (140, 220, 240), 2: (150, 80, 20), 5: (70, 170, 110), 10: (250, 70, 10)}


def read(image, at):
    sp = importlib.util.spec_from_file_location("alonsomatilla2023_fig3", BODY)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod.read_line(image, at, 10, (700, 630), 2950, [(2200, 150, 2900, 700)], colours=COLOURS)
