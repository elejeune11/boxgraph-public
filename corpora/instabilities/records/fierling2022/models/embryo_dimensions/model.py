# The surface Gamma_0 reaches x = +-R_AP at its poles (y = 0, z = Z_p) and its mid cross-section
# (x = 0) is a circle of radius R_DV: length 2 R_AP = 2 ratio R_DV, width 2 R_DV.


def run(inputs, settings):
    return {"L": 2.0 * inputs["ratio"] * inputs["R_DV"], "W": 2.0 * inputs["R_DV"]}


def symbolic():
    import sympy as sp
    R, k = sp.symbols("R_DV ratio", positive=True)
    return {"L": 2 * k * R, "W": 2 * R}
