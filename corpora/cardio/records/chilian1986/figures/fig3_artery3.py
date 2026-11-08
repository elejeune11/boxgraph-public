"""Fig. 3 (p. 6): the 3rd open marker from the top when covered; with oil the 4th visible open marker from the bottom (its exposed marker is hidden). See _fig3.py for the method and intervals."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("_fig3", os.path.join(os.path.dirname(os.path.abspath(__file__)), "_fig3.py"))
_f = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_f)


def read(image, at):
    return _f.read_vessel(image, at, 'open', {1: 3, 3: -4}, {2: 'hidden under the filled (vein) marker at about 155 um'})
