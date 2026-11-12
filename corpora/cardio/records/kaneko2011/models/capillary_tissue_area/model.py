# Tissue area per capillary as the reciprocal of the capillary count per area.
# N in 1/mm^2, A in um^2: 1 mm^2 = 1e6 um^2.


def run(inputs, settings):
    return {"A": 1e6 / inputs["N"]}


def symbolic():
    import sympy as sp

    N = sp.symbols("N", positive=True)
    return {"A": 10**6 / N}
