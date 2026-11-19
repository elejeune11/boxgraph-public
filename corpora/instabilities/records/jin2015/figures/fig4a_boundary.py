# Fig. 4(a): the black boundary curve labelled e_m^Uni=0.44, e_m^PE=0.35 (the only black line). See _fig3.py.
import importlib.util
import pathlib

_s = importlib.util.spec_from_file_location("jin_fig3", pathlib.Path(__file__).resolve().parent / "_fig3.py")
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read_contour(image, at, "4a", 5, 0)
