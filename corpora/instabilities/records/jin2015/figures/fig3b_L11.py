# Fig. 3(b): the contour labelled 11, line 1 from the bottom at H_s/H_f = 12. See _fig3.py.
import importlib.util
import pathlib

_s = importlib.util.spec_from_file_location("jin_fig3", pathlib.Path(__file__).resolve().parent / "_fig3.py")
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read_contour(image, at, "3b", 12, 1)
