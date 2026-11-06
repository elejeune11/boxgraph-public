"""Fig. 2b, G' (norm.) of the ionically crosslinked gel: the red filled squares, with error bars. See _fig2b.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_fig2b", Path(__file__).with_name("_fig2b.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_series(image, 'red', 'Gp')
