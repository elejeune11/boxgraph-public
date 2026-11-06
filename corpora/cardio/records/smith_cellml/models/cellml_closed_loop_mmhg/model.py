# Variant of cellml_closed_loop: the same equations and the same numbers, with the pressure unit
# the file declares ("kPa", lines 50-52) read as mmHg. Every pressure parameter goes in with the
# number written in the file, and every pressure comes out with that number in mmHg. The model is
# homogeneous in its pressure unit, so nothing else changes. 13 beats, as the file allows.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_cellml_closed_loop", os.path.join(_here, "..", "cellml_closed_loop", "model.py"))
_cl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cl)


def run(inputs, settings):
    return _cl.run(inputs, settings, cyclic=False)
