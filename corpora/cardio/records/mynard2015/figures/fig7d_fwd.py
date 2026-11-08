"""Fig. 7(d) (PDF p. 10), path via the abdomen/liver: peak forward wave intensity (black circles).

Reading by the shared code in _fig7.py (see its docstring). Tick labels matched:
x [10, 20, 30, 40, 50, 60] cm (the 60 label is partly cut; at least five ticks must match);
y [7, 6, 5, 4, 3, 2, 1, 0] (log10 W/m^2/s^2).
"""
import importlib.util
from pathlib import Path

SPEC = {"curve": "forward", "x": [10, 20, 30, 40, 50, 60], "y": [7, 6, 5, 4, 3, 2, 1, 0]}


def read(image, at):
    spec = importlib.util.spec_from_file_location("mynard2015_fig7", Path(__file__).with_name("_fig7.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
