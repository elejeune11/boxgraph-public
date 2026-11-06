"""Supp. Fig. 5b: the open black squares, cell spreading area against G'/G'', with error bars.
x ticks every 100 from 0 to 600 (labels 0, 200, 400, 600); y ticks every 500 um^2 from 0 to 2000.
See _figs5.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_figs5", Path(__file__).with_name("_figs5.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_panel(image, [0, 100, 200, 300, 400, 500, 600], [0, 500, 1000, 1500, 2000])
