# F_b = kB T / Delta (SI legend C), pN nm / nm -> pN.


def run(inputs, settings):
    return {"Fb": inputs["kT"] / inputs["delta"]}


def symbolic():
    import sympy as sp
    kT, delta = sp.symbols("kT delta", positive=True)
    return {"Fb": kT / delta}
