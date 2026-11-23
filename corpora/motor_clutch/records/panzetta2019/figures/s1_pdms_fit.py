"""Fig. S1, left (PDF p. 11): tensile stress against strain of PDMS; the red line, which the legend
labels "y = 930.32x" (the linear fit). The measured average curve (pale blue markers) lies under the
red line and shows only at its two ends, so it is not read.

Read by the shared code in _fig.py: axes calibrated from the printed labels' centres (x 0 ... 0.6,
y 0 ... 500 kPa), the red line traced by colour and continuity; the legend's red sample (top left)
is blanked."""
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")

SPEC = {
    "color": (215, 25, 30),
    "others": [(160, 170, 230), (0, 0, 0), (255, 255, 255)],
    "trace": True,
    "tol": 90,
    "gap": 40,
    "y_below": -40,
    "blank": [(0, 0, 900, 300)],
    "x": {"labels": [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]},
    "y": {"labels": [500, 400, 300, 200, 100]},
}


def read(image, at):
    spec = importlib.util.spec_from_file_location("panzetta2019_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
