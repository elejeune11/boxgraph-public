"""Fig 9a-c (PDF p. 18): the red (connected ligands) and blue (disconnected ligands)
profiles. Axis labels matched per panel below; the legend's two line samples are
blanked before tracing. Reader: _panel.py in this folder."""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("bagchi2025_panel", os.path.join(os.path.dirname(__file__), "_panel.py"))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

PANELS = {
    # x labels, y labels, x corner, y corner, legend box (data units)
    "a": ([10, 20, 30, 40], [0, 5, 10], 0, None, (19, 26, 11.5, 15.5)),
    "b": ([10, 20, 30, 40], [0.5, 1, 1.5, 2, 2.5, 3], 0, 0, (19.5, 25, 2.45, 3.1)),
    "c": ([10, 20, 30, 40], [0.55, 0.6, 0.65, 0.7], 0, 0.5, (19.5, 25, 0.69, 0.76)),
}
HUES = {"red": (330, 20, 60), "blue": (205, 250, 35)}   # hue range and least saturation


def read_panel(image, at, panel, colour, seed):
    xl, yl, xc, yc, legend = PANELS[panel]
    cal = P.calibrate(image, xl, yl, x_corner=xc, y_corner=yc)
    lo, hi, smin = HUES[colour]
    mask = P.hue_mask(image, lo, hi, smin=smin)
    return P.read_curve(image, at, cal, mask, seed=seed, legend=legend)
