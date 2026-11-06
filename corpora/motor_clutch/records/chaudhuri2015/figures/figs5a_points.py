"""Supp. Fig. 5a: the filled black squares, cell spreading area against G'' (Pa), with error bars.
x ticks every 500 Pa from 0 to 3000 (labels 0, 1000, 2000, 3000); y ticks every 500 um^2 from 0 to
2000. See _figs5.py for the method."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_figs5", Path(__file__).with_name("_figs5.py"))
F = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(F)


def read(image, at):
    return F.read_panel(image, [0, 500, 1000, 1500, 2000, 2500, 3000], [0, 500, 1000, 1500, 2000])
