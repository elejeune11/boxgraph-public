# Eq. 5: p = c p0, for the number of motors.


def run(inputs, settings):
    return {"nm": inputs["c"] * inputs["nm0"]}


def symbolic():
    import sympy as sp
    c, nm0 = sp.symbols("c nm0", positive=True)
    return {"nm": c * nm0}
