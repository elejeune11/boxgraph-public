"""Fig. 3(D): the line for F = 2 (K' = 1, tau = 10, omega' = 200); see _fig3.py."""
import importlib.util
from pathlib import Path

BODY = Path(__file__).with_name("_fig3.py")
COLOURS = {1: (150, 185, 225), 2: (250, 155, 115), 5: (5, 245, 155)}


def read(image, at):
    sp = importlib.util.spec_from_file_location("alonsomatilla2023_fig3", BODY)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod.read_line(image, at, 2, (650, 506), 2480, [(1650, 60, 2400, 620)], colours=COLOURS)
