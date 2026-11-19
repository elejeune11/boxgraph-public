# Reads a released StressEquatEulerStrains_*.gdat file from $BOXGRAPH_SOURCE (nothing is copied into the record) and
# returns the step value the gnuplot scripts draw at angle theta: the band of width pi/nbbins/2 centred on phi_Eul
# (column 3) that contains theta (stress_profile.plot, settings.plot). Pre-stress is chi*(1-x)/x (settings.plot line 9).
import math
import os
import pathlib


def _rows(name):
    out = []
    text = (pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / name).read_text(errors="replace")
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 7:
            continue
        try:
            out.append([float(p) for p in parts])
        except ValueError:
            continue
    return out


def band(rows, x, xcol, nbbins):
    w = math.pi / nbbins / 2
    inside = [r for r in rows if abs(x - r[xcol]) <= w / 2]
    pool = inside or rows
    return min(pool, key=lambda r: abs(x - r[xcol]))


def run(inputs, settings):
    rows = _rows(settings["file"])
    r = band(rows, inputs["theta"], 2, int(settings["nbbins"]))
    x = r[0]
    return {"sigma_ap": r[5], "sigma_dv": r[6], "sigma_a": inputs["chi"] * (1 - x) / x, "ratio": r[5] / r[6]}
