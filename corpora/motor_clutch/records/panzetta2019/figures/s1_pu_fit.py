"""Fig. S1, right (PDF p. 11): shear stress against shear strain of PU on log-log axes; the red line,
which the legend labels "y = 185.07x". The caption says the average curve is plotted; only the red
line is visible (the curve, if drawn, lies under it).

Read by the shared code in _fig.py: both axes calibrated from the printed labels' centres on log10
scales (x 0.0001 ... 1, y 0.1 ... 100 kPa), the red line traced by colour and continuity; the
legend's red sample (top) is blanked."""
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_fig.py")

SPEC = {
    "color": (215, 25, 30),
    "others": [(0, 0, 0), (255, 255, 255)],
    "trace": True,
    "tol": 90,
    "gap": 40,
    "y_below": -40,
    "blank": [(0, 0, 1250, 300)],
    "x": {"labels": [0.0001, 0.001, 0.01, 0.1, 1], "scale": "log10"},
    "y": {"labels": [100, 10, 1], "scale": "log10"},   # "0.1" sits on the x axis' first label
}


def read(image, at):
    spec = importlib.util.spec_from_file_location("panzetta2019_fig", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_spec(image, at, SPEC)
