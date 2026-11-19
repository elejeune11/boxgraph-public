# Fig. 5(f): where the green wrinkle branch leaves the flat line, labelled e_m; the strain read on the horizontal axis. See _fig5.py.
import importlib.util
import pathlib

_s = importlib.util.spec_from_file_location("jin_fig5", pathlib.Path(__file__).resolve().parent / "_fig5.py")
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read(image, at, "f")
