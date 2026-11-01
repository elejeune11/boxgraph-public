"""Fig. S6A of gong2018 (PDF p. 18): measured normalized relaxed stiffness of
alginate gels vs time (log axis), for initial moduli 1.4 (blue), 9.0 (red) and
3.4 kPa (yellow), with fitted curves (black dashed lines, not read).

Axes by _axes.py: x from 10^-1 (left spine) to 10^2 (right spine), the decade
ticks on the top spine (`regular` drops the shorter minor ticks that pass the
threshold); y ticks on the right spine at 1, 0.9, 0.8, 0.7 and 0.6 at the bottom
spine.  The data are dense dots that merge into a band; they are read by
_lines.py at the reader's chosen times, the middle of the run of the colour in
a window of +/-`half` columns.  Below about 3 s the three series lie on top of
each other and under the dashed fits; those positions are left out where the
run is not a single one of the right thickness.  The legend is excluded.
"""
import importlib.util
from pathlib import Path

AXES = {"tick_px": 30, "min_col": 300,
        # the decade ticks are about twice as long as the minor ticks: a 30 px band
        # that must be mostly dark keeps only them
        "x": {"labels": [0.1, 1, 10, 100], "scale": "log10", "edge_ticks": ["start", "end"], "band": "top",
              "min_frac": 0.7},
        "y": {"labels": [1, 0.9, 0.8, 0.7, 0.6], "edge_ticks": ["end"], "band": "right", "regular": True}}
LEGEND = [[600, 1850, 2100, 2420]]
SERIES = {
    "k14": {"color": [0, 114, 189], "tol": 70},
    "k90": {"color": [217, 83, 25], "tol": 70},
    # the 3.4 kPa data scatter: read as a band (median row, 10-90% spread)
    "k34": {"color": [237, 177, 32], "tol": 70, "scatter": True, "half": 20},
}
COMMON = {"open_r": 0, "max_run": 70, "min_run": 10, "half": 6, "src_px": 8, "margin": 25}


def read(image, at, key):
    spec = importlib.util.spec_from_file_location("gong2018_lines", Path(__file__).with_name("_lines.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.read_curve(image, at, AXES, {**COMMON, **SERIES[key]}, LEGEND)
