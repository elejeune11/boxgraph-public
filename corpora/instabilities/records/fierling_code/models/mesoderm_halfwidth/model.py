# Port of the region test of set_zzero (Surface_Evolver_script.txt lines 188, 196) at x = 0 on the initial mid cross-section.
import math


def run(inputs, settings):
    rayon = 1.0
    yb = rayon * (1 / math.sqrt(inputs["ey"]) + inputs["delta"])
    s = inputs["R_DV"] * math.asin(min(yb / rayon, 1.0))
    return {"s": s, "rows": s / inputs["w"]}
