# Fig. 4(a): the blue plus (supercritical) markers. See _fig4a.py.
import importlib.util
import pathlib

_s = importlib.util.spec_from_file_location("jin_fig4a", pathlib.Path(__file__).resolve().parent / "_fig4a.py")
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read(image, at, "plus")
