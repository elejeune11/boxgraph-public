"""Fig. 5 (PDF p. 8): area against pressure at the thoracic aorta I midpoint, the upper branch of the dashed loop marked 8 phi (visco-elastic model with eight times the measured silicone viscosity).

Reading by the shared code in _fig5.py (see its docstring for the calibration, how the curves or
markers are told apart and the intervals).
"""
import importlib.util
from pathlib import Path


def read(image, at):
    spec = importlib.util.spec_from_file_location("alastruey2011_fig5", Path(__file__).with_name("_fig5.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, {"curve": "upper8", "x": [11, 12, 13, 14, 15], "y": [6.2, 6, 5.8, 5.6]})
