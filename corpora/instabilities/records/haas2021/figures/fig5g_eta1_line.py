"""Fig. 5(g) (PDF p. 13): the grey vertical line labelled |eta| = 1 (the constriction limit).

Read as k (columns) at given d (rows), by the shared code in _fig5g.py. Line colour (102, 102, 102),
sampled from the rendered page; it is broken where the labels w0* < w and w* > w are written.
"""
import importlib.util
from pathlib import Path

COLOR = (102, 102, 102)


def read(image, at):
    spec = importlib.util.spec_from_file_location("haas2021_fig5g", Path(__file__).with_name("_fig5g.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_vertical_line(image, at, COLOR)
