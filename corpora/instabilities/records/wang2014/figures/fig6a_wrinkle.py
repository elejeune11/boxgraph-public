"""Fig. 6(a) (PDF p. 5): the thick red line 'Wrinkling' (lambda_p = 1), critical strain against mu_f/mu_s.

Reading by the shared code in _wang.py (see its docstring for calibration, tracing and intervals).
Tick labels matched: x 0 (frame), 2, 4, 6, 8, 10 (frame); y 0 (frame), 0.05 to 0.3 and 0.4 (the
0.35 tick is hidden under the dashed crease line, which starts at the frame). The legend's
red sample line is blanked; the trace starts on the red line nearest 0.26 at mu_f/mu_s = 3.
"""
import importlib.util
from pathlib import Path

SPEC = {"x": {"lo": 0, "hi": 10, "ticks": [2, 4, 6, 8]},
        "y": {"lo": 0, "ticks": [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4]},
        "ink": "red", "w": 24.0, "seed": [3.0, 0.26], "blank": [[1530, 560, 1900, 670]]}


def _shared():
    spec = importlib.util.spec_from_file_location("wang2014_wang", Path(__file__).with_name("_wang.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(image, at):
    return _shared().read_curve(image, at, SPEC)
