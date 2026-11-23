"""Fig. 4(f) (PDF p. 10): measured force-loading rates of molecular clutches (bars 1-4 under
'Experiment': 1 MEF WT, 2 MEF vinI997A, 3 MEF Vcl KO, 4 MEF vinA50I; data digitized from ref. 20,
mean with 95% confidence interval), with their error bars.

Shared code in _hd.py. y: ticks 0, 0.9, 1.8, 2.7 (x: the category ticks under the bars, used
only to find the axis). Bars: columns of the four bar colours reaching the baseline, value at the
top edge of the colour; the bars of each group are found inside that group's columns (the
brackets under the axis: Experiment, then Theory at 300, 200 and 100 sites per um^2). Error
bars: the dark vertical line through each bar's centre, up to its cap and down inside the bar.
x is the cell-line number printed under the bar.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"marks": [(0, 1), (1, 2), (2, 3), (3, 4)], "major": 0.8},
    "y": {"marks": [(0, 0), (1, 0.9), (2, 1.8), (3, 2.7)], "major": 0.8},
}
COLOURS = [(120, 255, 120), (255, 255, 0), (80, 190, 255), (250, 190, 190)]
GROUPS = {"exp": (0.0, 0.415, [1, 2, 3, 4]), "300": (0.415, 0.597, [1, 2, 3]),
          "200": (0.597, 0.778, [1, 2, 3]), "100": (0.778, 1.0, [1, 2, 3])}  # shares of the crop width


def read_group(image, name, err):
    cal = H.calibrate(image, SPEC)
    sp = cal["sp"]
    a, b, labels = GROUPS[name]
    W = image.shape[1]
    box = (max(sp["c1"] + 2, int(a * W)), int(cal["y"].px(2.8)), min(sp["x_to"], int(b * W)), sp["r0"])
    return H.bars(image, COLOURS, 50, cal["y"], box, labels, err=err)


def read(image, at):
    return read_group(image, "exp", True)
