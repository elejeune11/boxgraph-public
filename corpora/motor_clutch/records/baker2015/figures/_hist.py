"""Supp. Figs 7 and 9: fibre-diameter histograms, read bin by bin with _kit.histogram (outlined bins,
a fitted Gaussian drawn over them). Each reading file gives the bins' fill colour and the printed
tick labels of its panel."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)


def read_hist(image, fill, yticks, xticks, tol=40):
    return K.histogram(image, fill, tol, yticks, xticks)
