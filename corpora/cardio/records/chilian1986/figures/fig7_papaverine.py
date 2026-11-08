"""Fig. 7 (p. 8): the papaverine points (open circles) with their SE bars: 1 large arterioles,
2 medium arterioles, 3 small venules, 4 medium venules. See _fig7.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig7", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig7.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_series(image, at, "open")
