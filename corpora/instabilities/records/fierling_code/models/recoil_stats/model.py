# Reads laser_ablation_recoil.gdat from $BOXGRAPH_SOURCE and applies the expressions of laser_ablation_recoil.plot
# (lines 44-45): the mean of the first n embryo columns and the bar sqrt(sum (x - mean)^2)/(n - 1), as written there.
import math
import os
import pathlib


def run(inputs, settings):
    n = int(settings["n"])
    text = (pathlib.Path(os.environ["BOXGRAPH_SOURCE"]) / "laser_ablation_recoil.gdat").read_text(errors="replace")
    for line in text.splitlines():
        parts = line.split()
        if not parts or parts[0].startswith("#"):
            continue
        if abs(float(parts[0]) - inputs["d"]) < 1e-9:
            v = [float(p) for p in parts[1:n + 1]]
            m = sum(v) / n
            return {"mean": m, "bar": math.sqrt(sum((x - m) ** 2 for x in v)) / (n - 1)}
    raise ValueError(f"no row for DV position {inputs['d']} um")
