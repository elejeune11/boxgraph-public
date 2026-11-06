"""Fig. 5 (PDF p. 10): the dashed black least-squares line (labelled log(l) = 0.04733 log(r) + 0.6309),
read between the red markers. Code in _fig5.py and _common.py."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig5.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.dashed_line(image, at)
