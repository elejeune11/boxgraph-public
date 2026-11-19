"""Fig. 3(h) (PDF p. 4), second reading: the dashed horizontal line Delta beta^(c) (in units of
d/delta) against lambda/delta. Calibration by _fig3_core.py (see its docstring); labelled y ticks
0.4, 0.2 and 0, from the top. The dashes are the thin dark runs off the thick curve and the axes,
pooled over +-60 columns around each position so that the gaps are bridged.
"""
import importlib.util
from pathlib import Path


def _mod():
    spec = importlib.util.spec_from_file_location("haas2015_fig3_core", Path(__file__).with_name("_fig3_core.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(image, at):
    return _mod().read_dashed(image, at, [0.4, 0.2, 0.0], "dashed line, thin runs off the curve")
