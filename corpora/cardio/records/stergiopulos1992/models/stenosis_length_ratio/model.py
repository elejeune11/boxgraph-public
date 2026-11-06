"""Length-to-diameter ratio of a stenosis, Ls/D, with D the segment's diameter (Table 1) at the stenosis.

The paper does not say which diameter it divides by; the segment radius is taken to vary linearly from
its proximal to its distal value (p. 3), and the stenosis is placed at a fraction xi of the segment length.
"""


def run(inputs, settings):
    r = inputs["rp"] + (inputs["rd"] - inputs["rp"]) * inputs["xi"]
    return {"LD": inputs["Ls"] / (2.0 * r)}


def symbolic():
    import sympy as sp

    Ls, rp, rd, xi = sp.symbols("Ls rp rd xi", positive=True)
    return {"LD": Ls / (2 * (rp + (rd - rp) * xi))}
