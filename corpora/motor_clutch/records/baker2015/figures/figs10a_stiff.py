"""Supp. Fig. 10a: proliferation on stiff networks (dark grey bars) at low, medium, high fibre density
(indices 1-3). y ticks 0-20 by 5. The legend swatch does not stand on the axis. See _kit.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_kit", Path(__file__).with_name("_kit.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)


def read(image, at):
    return K.bar_panel(image, [((50, 50, 50), 30)], [0, 5, 10, 15, 20], ink_thr=140.0)   # the error bars are grey (~125)
