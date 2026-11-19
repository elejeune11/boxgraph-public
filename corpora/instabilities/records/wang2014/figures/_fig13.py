"""Fig. 13 (PDF p. 9): nominal stress S (Pa) against stretch lambda in uniaxial tension of the
Sylgard films; red circles 'Uniaxial tension test' (measured), blue line 'Neo Hookean model'.

The measured points are dense: their circles overlap into a band, read as a curve with the shared
code in _wang.py (calibration, tracing and intervals in its docstring), with these changes:
  * the band's ink is red with the blue fit line drawn over it; the red mask is closed vertically
    over 41 px so the band is not split where the blue line crosses it ('red_bridged');
  * the band is about one circle tall, so w is that height: the value is the centre of the band,
    which is the centre of the circles, and the interval covers q + misfit about it (where the
    band is fused with anything else, the whole run).
The frames are grey, so the frame ink is any neutral pixel with R+G+B < 480.
The source bitmap is coarse (about 150 dpi): at 1200 dpi q = 8.
Tick labels matched per panel (the axis multiplier 'x 10^4' or 'x 10^5' printed above each
panel is applied, so values are in Pa).
"""
import importlib.util
from pathlib import Path

PANELS = {
    "a": {"x": {"lo": 1, "hi": 3, "ticks": [1.5, 2, 2.5]},
          "y": {"lo": 0, "hi": 20000, "ticks": [5000, 10000, 15000]},
          "seed": [1.75, 9000], "blank": [[150, 60, 1150, 340]]},
    "b": {"x": {"lo": 1, "hi": 3.5, "ticks": [1.5, 2, 2.5, 3]},
          "y": {"lo": 0, "ticks": [50000, 100000, 150000]},
          "seed": [1.75, 55000]},
    "c": {"x": {"lo": 1, "hi": 3, "ticks": [1.5, 2, 2.5]},
          "y": {"lo": 0, "hi": 300000, "ticks": [100000, 200000]},
          "seed": [1.75, 140000]},
    "d": {"x": {"lo": 1, "hi": 3, "ticks": [1.5, 2, 2.5]},
          "y": {"lo": 0, "hi": 500000, "ticks": [100000, 200000, 300000, 400000]},
          "seed": [1.75, 200000]},
}


def read(image, at, panel):
    spec = importlib.util.spec_from_file_location("wang2014_wang", Path(__file__).with_name("_wang.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    s = dict(PANELS[panel], ink="red_bridged", w=60.0, q=8, max_px=200, frame_level=480)
    return mod.read_curve(image, at, s)
