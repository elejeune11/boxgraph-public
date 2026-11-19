# v = k * sigma_AP with the unknown constant k written as 1 (um/s per nondimensional stress unit):
# the SI states proportionality only ("in a first approximation, if there is some frictional
# resistance"). A DV-oriented cut has its normal along AP, so the force across it is sigma_AP.


def run(inputs, settings):
    c = inputs["sigma"]
    return {"v": {"x": list(c["x"]), "y": [1.0 * y for y in c["y"]]}}
