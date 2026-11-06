# Variant of cellml_closed_loop with two corrections: the pressure unit the file declares
# ("kPa", lines 50-52) read as mmHg, and the driver's tau taken as the remainder of time over the
# period, which the file's documentation (line 27) says its 13 if statements stand for, so the
# model can run to a periodic steady state. Everything else as in cellml_closed_loop.
import importlib.util
import os

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "_cellml_closed_loop", os.path.join(_here, "..", "cellml_closed_loop", "model.py"))
_cl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cl)


def run(inputs, settings):
    return _cl.run(inputs, settings, cyclic=True)
