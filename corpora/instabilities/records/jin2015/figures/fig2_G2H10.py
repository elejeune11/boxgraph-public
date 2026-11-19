# Fig. 2: the blue curve labelled G_f/G_s=2, H_s/H_f=10; line 3 from the bottom at L/Hf = 15. See _fig2.py.
import importlib.util
import pathlib

_s = importlib.util.spec_from_file_location("jin_fig2", pathlib.Path(__file__).resolve().parent / "_fig2.py")
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read(image, at, 15, 3)
