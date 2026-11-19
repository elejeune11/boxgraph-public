# Fig. 3(a): the contour labelled e_m^Uni=0.02, e_m^PE=0.015, line 4 from the bottom at H_s/H_f = 3. See _fig3.py.
import importlib.util
import pathlib

_s = importlib.util.spec_from_file_location("jin_fig3", pathlib.Path(__file__).resolve().parent / "_fig3.py")
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read_contour(image, at, "3a", 3, 4)
