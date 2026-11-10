# Steady flow split implied by the territory resistances of Supp. Table S2: each territory's
# flow is proportional to 1/(Ra + Rmicro + Rv) under one common pressure drop.
# Port units: mmHg*s/ml in, percent out.


def run(inputs, settings):
    g = {k: 1.0 / (inputs["Ra_" + k] + inputs["Rm_" + k] + inputs["Rv_" + k]) for k in ("lad", "lcx", "rca")}
    left = g["lad"] + g["lcx"]
    return {"lad_share": 100.0 * g["lad"] / left, "left_share": 100.0 * left / (left + g["rca"])}
