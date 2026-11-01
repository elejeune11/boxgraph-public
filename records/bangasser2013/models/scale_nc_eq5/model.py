# Eq. 5: p = c p0, for the number of clutches.


def run(inputs, settings):
    return {"nc": inputs["c"] * inputs["nc0"]}


def symbolic():
    import sympy as sp
    c, nc0 = sp.symbols("c nc0", positive=True)
    return {"nc": c * nc0}
