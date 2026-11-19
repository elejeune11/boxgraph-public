# Fig. 2: the blue curve labelled G_f/G_s=50, H_s/H_f=100; line 1 from the bottom at L/Hf = 100. See _fig2.py.
import importlib.util
import pathlib

_s = importlib.util.spec_from_file_location("jin_fig2", pathlib.Path(__file__).resolve().parent / "_fig2.py")
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read(image, at, 100, 1)
