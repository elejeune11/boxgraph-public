# Reads a released StressEquatEulerStrains_*.gdat file from $BOXGRAPH_SOURCE and returns sigma_AP (column 6) of the
# angular band that contains d/R_DV, as stress_profile_for_laser_ablations.plot draws it (x = R_DV * phi_Eul).
# The plotting script also shifts a band that would overlap the previous one (max(PREV_PHI+width, phi)); bands here
# are taken centred on phi_Eul, which places 0, 8 and 16 um in the same bands as the figure.
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


def run(inputs, settings):
    rows = _rows(settings["file"])
    x = abs(inputs["d"]) / inputs["R_DV"]
    w = math.pi / int(settings["nbbins"]) / 2
    inside = [r for r in rows if abs(x - r[2]) <= w / 2] or rows
    r = min(inside, key=lambda r: abs(x - r[2]))
    return {"sigma_ap": r[5]}
