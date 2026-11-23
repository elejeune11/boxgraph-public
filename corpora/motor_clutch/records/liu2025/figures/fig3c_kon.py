"""Fig. 3(c) (PDF p. 8): the blue points, best-fitting molecular-clutch formation rate k0on of the
talin WT model against fibronectin concentration (left axis).

Shared code in _hd.py. x: log axis, the long ticks 1, 10, 100. Three y axes: left (blue, k0on,
log, long ticks 0.01, 0.1, 1, 10), the first right-hand axis (red, r in nm, log, long ticks 0.1,
1, 10, ticks pointing right) and the second right-hand axis (green, sigma_m, linear, ticks 0, 30,
60, 90, pointing right). Each series is calibrated on its own axis line, chosen by the columns it
stands in. Points: blobs of the series colour, opened with a disk wider than the connecting lines
(which go) and narrower than the dots (which stay).
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

X = {"scale": "log10", "marks": [(0, 1), (1, 10), (2, 100)], "major": 0.8, "region": (300, 1800)}
AXES = {
    "left": {"x": X, "y": {"scale": "log10", "marks": [(0, 0.01), (1, 0.1), (2, 1), (3, 10)], "major": 0.8}},
    "red": {"x": X, "y": {"scale": "log10", "marks": [(0, 0.1), (1, 1), (2, 10)], "major": 0.8},
            "side": "right", "ycols": (1750, 1950)},
    "green": {"x": X, "y": {"marks": [(0, 0), (1, 30), (2, 60), (3, 90)], "major": 0.8},
              "side": "right", "ycols": (2300, 2500)},
}
SPEC = AXES["left"]


def read_series(image, axis, rgb):
    spec = dict(AXES[axis])
    cal_x = H.calibrate(image, AXES["left"])  # x ticks and the plot box from the left axis and the x axis
    sp = cal_x["sp"]
    spec["box"] = lambda s: (sp["c1"] + 2, sp["y_from"], 1830, sp["r0"] - 1)
    spec["spines"] = lambda s: {"r0": sp["r0"], "r1": sp["r1"], "x_from": sp["x_from"], "x_to": sp["x_to"]}
    return H.read_symbols(image, spec, rgb, 80, "circle", mode="fill", open_px=4, min_area=60)


def read(image, at):
    return read_series(image, "left", (20, 20, 240))
