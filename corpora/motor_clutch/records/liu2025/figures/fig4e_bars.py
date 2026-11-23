"""Fig. 4(e) (PDF p. 10): force-loading rates of molecular clutches predicted by the talin WT model
for the four clutch-tension bins (1: 0-10, 2: 10-20, 3: 20-30, 4: 30-40 pN), bars 1-4.

Shared code in _hd.py. y: ticks 0, 2, 4, 6 (x: the four category ticks under the bars, used only
to find the axis). Bars: columns of the four bar colours reaching the baseline; the value is the
top edge of the colour (just under the bar's thin dark outline, which lies within the interval).
x is the bin number printed in the legend.
"""
import importlib.util
from pathlib import Path

_s = importlib.util.spec_from_file_location("liu2025_hd", Path(__file__).with_name("_hd.py"))
H = importlib.util.module_from_spec(_s)
_s.loader.exec_module(H)

SPEC = {
    "x": {"marks": [(0, 1), (1, 2), (2, 3), (3, 4)], "major": 0.8},
    "y": {"marks": [(0, 0), (1, 2), (2, 4), (3, 6)], "major": 0.8},
}
COLOURS = [(235, 240, 30), (250, 195, 40), (245, 155, 60), (235, 120, 85)]


def read(image, at):
    cal = H.calibrate(image, SPEC)
    sp = cal["sp"]
    box = (sp["c1"] + 2, int(cal["y"].px(6.3)), sp["x_to"], sp["r0"])
    return H.bars(image, COLOURS, 45, cal["y"], box, [1, 2, 3, 4])
