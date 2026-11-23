"""Fig. 5D (PDF p. 5, adapted from ref. 16): average FA area, four bars with upper error bars.

A raster (blurred) with grey axes. Read by the shared code in _raster_bars.py (see its
docstring). Bars left to right: hydrogel soft (grey), hydrogel stiff (black), fibres soft
(grey), fibres stiff (black), given x = 1, 2, 3, 4 (substrate_condition). The dashed grey
divider is narrower than a bar and is not taken for one. The hash pins _raster_bars.py.
"""
import hashlib
import importlib.util
from pathlib import Path

SHARED = Path(__file__).with_name("_raster_bars.py")
SHARED_SHA256 = "5e94f659ba1dfa42dbe34246c04dc8504763535ba8dc63f4fd9340fd9e7e1ceb"

SPEC = {"y_labels": [10, 8, 6, 4, 2, 0], "bar_gray": [0, 205], "categories": [1, 2, 3, 4],
        "min_width": 60, "tick_probe": 18}


def read(image, at):
    if hashlib.sha256(SHARED.read_bytes()).hexdigest() != SHARED_SHA256:
        raise RuntimeError("_raster_bars.py changed; re-check this reading and update SHARED_SHA256")
    spec = importlib.util.spec_from_file_location("cao2017_raster_bars", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_bars(image, at, SPEC)
