# Fig. 7(a): the green solid curve labelled H_s/H_f=0.2 (neo-Hookean wrinkle analysis)
# Calibration and tracing: see _fig7.py and _jin.py (axes from the panel's own ticks).
import importlib.util
import pathlib

_s = importlib.util.spec_from_file_location("jin_fig7", pathlib.Path(__file__).resolve().parent / "_fig7.py")
F = importlib.util.module_from_spec(_s)
_s.loader.exec_module(F)


def read(image, at):
    return F.read_line(image, at, "a", "green", seed_col_frac=0.97)
